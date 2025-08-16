###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

"""This module handles reading and writing of PID data.

It reads in calibration data locations from a JSON file. It also infers relevant
branch names from the PID cuts and binning variables. Lastly, it infers the PID
histogram file names from the requested configuration.
"""

import collections
import json
import os
import pickle
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import boost_histogram as bh
import pandas as pd
import uproot
from logzero import logger as log
from apd import auth

from pidcalib2 import utils
from pidcalib2.aliases import ALIASES, RUN3_ALIASES
from pidcalib2.samples import SIMPLE_SAMPLES, TUPLE_NAMES

from apd import AnalysisData

import numpy as np

GLOBAL_BRANCHES = ["nTracks"]
for aliases in (ALIASES, RUN3_ALIASES):
    for branch in aliases.keys():
        if branch == aliases[branch]:
            GLOBAL_BRANCHES += [branch]
GLOBAL_BRANCHES = list(np.unique(GLOBAL_BRANCHES))


def is_simple(sample: str) -> bool:
    """Return whether a sample has a simple directory structure.

    All Run 1 samples and Run 2 Electron samples have a single DecayTree inside.
    Standard Run 2 samples have multiple directories, each of which has a
    DecayTree inside. This function checks if the sample is in the list of
    simple samples.

    Args:
        sample: Sample name, e.g., Turbo15.
    """
    return sample in SIMPLE_SAMPLES


def get_relevant_branch_names(
    pid_cuts: List[str],
    bin_vars: List[str],
    cuts: Optional[List[str]] = None,
    sweight: Optional[str] = "probe_sWeight",
    particle: Optional[str] = None,
    ordering_variables: List[str] = [],
) -> Dict[str, str]:
    """Return a dict of branch names relevant to the cuts and binning vars.

    The key is user-level variable name/alias. The value is the actual branch
    name.

    Args:
        pid_cuts: Simplified user-level cut list, e.g., ["DLLK < 4"].
        bin_vars: Variables used for the binning.
        cuts: Arbitrary cut list, e.g., ["Dst_IPCHI2 < 10.0"].
        sweight: Name of the sWeight branch (probe_sWeight is used as
                 default, but in Run 3 there are cases where this is
                 not true [e.g. Pi/K sample]).
        particle: Prefix for the aliases, e.g. "p_" or "pi_" etc.
                  If this is not specified then the Run 1 and 2
                  aliases will be used.
    """

    ALIASES_TO_USE = ALIASES
    if particle is not None:
        ALIASES_TO_USE = RUN3_ALIASES

    branch_names = {}

    if sweight is not None:
        branch_names["sWeight"] = sweight

    whitespace = re.compile(r"\s+")
    for pid_cut in pid_cuts:
        pid_cut = re.sub(whitespace, "", pid_cut)
        pid_cut_vars = utils.extract_variable_names(pid_cut)

        for pid_cut_var in pid_cut_vars:
            if pid_cut_var not in ALIASES_TO_USE:
                log.warning(
                    (
                        f"PID cut variable '{pid_cut_var}' is not a known alias, "
                        "using raw variable"
                    )
                )
                branch_names[pid_cut_var] = pid_cut_var
            else:
                branch_names[pid_cut_var] = ALIASES_TO_USE[pid_cut_var].format(particle)

    for bin_var in bin_vars:
        if bin_var not in ALIASES_TO_USE:
            log.warning(
                f"'Binning variable {bin_var}' is not a known alias, using raw variable"
            )
            branch_names[bin_var] = bin_var
        else:
            branch_names[bin_var] = ALIASES_TO_USE[bin_var].format(particle)

    # Add vars in the arbitrary cuts
    if cuts:
        for cut in cuts:
            cut = re.sub(whitespace, "", cut)
            cut_vars = utils.extract_variable_names(cut)
            for cut_var in cut_vars:
                if cut_var not in ALIASES_TO_USE:
                    log.warning(
                        (
                            f"Cut variable '{cut_var}' is not a known alias, "
                            "using raw variable"
                        )
                    )
                    branch_names[cut_var] = cut_var
                else:
                    branch_names[cut_var] = ALIASES_TO_USE[cut_var].format(particle)
    branch_names.update(
        {
            ordering_variable: ordering_variable
            for i, ordering_variable in enumerate(ordering_variables)
            if ordering_variable not in branch_names.values()
        }
    )
    if len(branch_names) != len(set(branch_names.values())):
        duplicates = [
            item
            for item, count in collections.Counter(branch_names.values()).items()
            if count > 1
        ]
        log.error(
            (
                "You are mixing aliases and raw variable names for the same "
                f"variable(s): {duplicates}"
            )
        )
        raise KeyError

    return branch_names


def get_reference_branch_names(
    ref_pars: Dict[str, List[str]], bin_vars: Dict[str, str]
) -> List[str]:
    """Return a list of relevant branch names in the reference sample.

    Args:
        ref_pars: A dict of {particle branch prefix : [particle type, PID cut]}
    """
    branch_names = []

    for ref_par_name in ref_pars:
        for bin_var, bin_var_branch in bin_vars.items():
            branch_name = get_reference_branch_name(
                ref_par_name, bin_var, bin_var_branch
            )
            # Avoid duplicate entries
            if branch_name not in branch_names:
                branch_names.append(branch_name)
    return branch_names


def get_reference_branch_name(prefix: str, bin_var: str, bin_var_branch: str) -> str:
    """Return a full name of a binning branch in the reference data.

    Args:
        prefix: Branch prefix of the particle in the reference sample.
        bin_var: Variable used for the binning.
        bin_var_branch: Branch name of the variable used for binning.
    """
    if bin_var in GLOBAL_BRANCHES:
        return bin_var_branch

    return f"{prefix}_{bin_var_branch}"


def get_calibration_samples(
    samples_file: Optional[str] = None,
) -> Dict[str, Dict[str, Any]]:
    """Return a dictionary of all files for all calibration samples.

    Args:
        samples_file: JSON file with the calibration file lists.
    """
    if samples_file is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        samples_file = str(Path(current_dir, "data/samples.json"))

    log.debug(f"Reading file lists from '{samples_file}'")
    with open(samples_file) as f:
        samples = json.load(f)
    if "calib_files" in samples.keys():
        datasets = AnalysisData("pid", samples["calib_files"]["analysis"])
        samples["files"] = datasets(
            polarity=samples["calib_files"]["polarity"],
            eventtype=samples["calib_files"]["eventtype"],
            datatype=samples["calib_files"]["datatype"],
            version=samples["calib_files"]["version"],
            name=samples["calib_files"]["name"],
        )
        if "start_file" in samples["calib_files"]:
            first_file = samples["calib_files"]["start_file"] - 1
            samples["files"] = samples["files"][first_file:]
    return samples


def get_calibration_sample(
    sample_name: str,
    magnet: str,
    particle: str,
    samples_file: str,
    max_files: Optional[int] = None,
) -> Dict[str, Any]:
    """Return a list of calibration files for a particular sample.

    Args:
        sample: Data sample name (Turbo18, etc.)
        magnet: Magnet polarity (up, down)
        particle: Particle type (K, pi, etc.)
        samples_file: File in which to look up the file list.
        max_files: Optional. The maximum number of files to get. Defaults to
            None (= all files).
    """
    samples = get_calibration_samples(samples_file)

    magnet = f"Mag{magnet.capitalize()}"
    sample_full_name = "-".join([sample_name, magnet, particle])

    try:
        sample = samples[sample_full_name]
    except KeyError:
        log.error(
            (
                f"Sample '{sample_full_name}' not found. "
                "Consult 'pidcalib2.make_eff_hists --list configs'."
            )
        )
        raise

    calibration_sample = sample.copy()
    if "link" in sample:
        del calibration_sample["link"]
        link = sample["link"]
        try:
            if "files" in samples[link].keys():
                calibration_sample["files"] = samples[link]["files"]
            elif "calib_files" in samples[link].keys():
                calibration_sample["calib_files"] = samples[link]["calib_files"]
        except KeyError:
            log.error(f"Linked sample '{link}' not found in {samples_file}")
            raise
        # Copy configuration from the link (tuple_names, cuts, etc.), but only
        # if it doesn't override the upstream configuration
        for key, item in samples[link].items():
            if key == "calib_files" or key == "files":
                continue
            if key not in calibration_sample:
                calibration_sample[key] = item
    if "calib_files" in calibration_sample.keys():
        datasets = AnalysisData("pid", calibration_sample["calib_files"]["analysis"])
        calibration_sample["files"] = datasets(
            polarity=calibration_sample["calib_files"]["polarity"],
            eventtype=calibration_sample["calib_files"]["eventtype"],
            datatype=calibration_sample["calib_files"]["datatype"],
            version=calibration_sample["calib_files"]["version"],
            name=calibration_sample["calib_files"]["name"],
        )
        if "start_file" in calibration_sample["calib_files"]:
            first_file = calibration_sample["calib_files"]["start_file"] - 1
            calibration_sample["files"] = calibration_sample["files"][first_file:]
    if max_files:
        log.warning(
            "You are using the --max-files option; it should be used only for testing"
        )
        calibration_sample["files"] = calibration_sample["files"][:max_files]
    return calibration_sample


def get_ordering_variables(
    sample_name: str,
    magnet: str,
    particle: str,
    samples_file: str,
    max_files: Optional[int] = None,
) -> List[str]:
    """Return a list of calibration files for a particular sample.

    Args:
        sample: Data sample name (Turbo18, etc.)
        magnet: Magnet polarity (up, down)
        particle: Particle type (K, pi, etc.)
        samples_file: File in which to look up the file list.
        max_files: Optional. The maximum number of files to get. Defaults to
            None (= all files).
    """
    samples = get_calibration_samples(samples_file)

    magnet = f"Mag{magnet.capitalize()}"
    sample_full_name = "-".join([sample_name, magnet, particle])

    try:
        sample = samples[sample_full_name]
    except KeyError:
        log.error(
            (
                f"Sample '{sample_full_name}' not found. "
                "Consult 'pidcalib2.make_eff_hists --list configs'."
            )
        )
        raise

    ordering_variables = []
    if "ordering_variables" in sample.keys():
        ordering_variables = sample["ordering_variables"]
    return ordering_variables


def root_to_dataframe(
    path: str,
    tree_names: List[str],
    branches: List[str],
    calibration: bool = False,
    particle: Optional[str] = None,
    sorting_branches: Optional[List] = [],
) -> Union[pd.DataFrame, None]:  # sourcery skip: extract-duplicate-method
    """Return DataFrame with requested branches from tree in ROOT file.

    Args:
        path: Path to the ROOT file; either file system path or URL, e.g.
            root:///eos/lhcb/file.root.
        tree_names: Names of trees inside the ROOT file to read.
        branches: Branches to put in the DataFrame.
        calibration: Whether the file is a calibration sample or a user sample.
        particle: Name of the particle for the aliases. If this is not
                  specified then the Run 1 and 2 aliases will be used.
    """

    # Get the correct aliases
    ALIASES_TO_USE = ALIASES
    if particle is not None:
        ALIASES_TO_USE = RUN3_ALIASES
    tree = None
    # EOS sometimes fails with a message saying the operation expired. It is
    # intermittent and hard to replicate. See this related issue:
    # https://github.com/scikit-hep/uproot4/issues/351. To avoid PIDCalib2
    # completely failing in these cases, we skip the file with a warning
    # message if this happens.
    try:
        # The EOS token is appended to the URL, and contains a semicolon which
        # causes a problem when passing the filename as a string to uproot.open()
        # We therefore use the syntax open({ filename:objectname }) where uproot
        # does not try to parse filename:objectname
        root_file = uproot.open({auth(path): None}, **{"timeout": 1800})
    except FileNotFoundError as exc:
        if "Server responded with an error: [3010]" in exc.args[0]:
            log.error(
                (
                    "Permission denied; do you have Kerberos credentials? "
                    "Try running 'kinit -f [USERNAME]@CERN.CH'"
                )
            )
        raise
    except OSError as err:
        if "Operation expired" not in err.args[0]:
            raise
        log.error(
            f"Failed to open '{path}' because an XRootD operation expired; skipping"
        )
        print(err)
        return None

    dfs = []
    for tree_name in tree_names:
        try:
            tree = root_file[tree_name]

            df = tree.arrays(branches, library="pd")

            if sorting_branches:
                if len(sorting_branches) > 0:
                    df = df.sort_values(by=sorting_branches).reset_index(drop=True)

            dfs.append(df)  # type: ignore
        except uproot.exceptions.KeyInFileError as exc:  # type: ignore
            assert tree is not None
            similar_keys = []
            if calibration:
                aliases_in_tree = [
                    alias
                    for alias, var in ALIASES_TO_USE.items()
                    if var.format(particle) in tree.keys()
                ]
                similar_keys += utils.find_similar_strings(
                    exc.key, aliases_in_tree, 0.80
                )
                similar_keys += utils.find_similar_strings(
                    "probe_" + exc.key, tree.keys(), 0.80
                )
            similar_keys += utils.find_similar_strings(exc.key, tree.keys(), 0.80)
            similar_keys += utils.find_similar_strings(
                exc.key.replace("Brunel", ""), tree.keys(), 0.80
            )
            # Remove duplicates while preserving ordering
            similar_keys = list(dict.fromkeys(similar_keys))
            log.error(
                (
                    f"Branch '{exc.key}' not found; similar aliases and/or branches "
                    f"that exist in the tree: {similar_keys}"
                )
            )
            raise
        except OSError as err:
            if "Operation expired" not in err.args[0]:
                raise

            log.error(
                (
                    f"Failed to open '{path}' because an XRootD operation "
                    "expired; skipping"
                )
            )
            print(err)
            return None

    return pd.concat(dfs, ignore_index=True)


def get_tree_paths(
    particle: str,
    sample: str,
    override_tuple_names: Optional[List[str]] = None,
) -> List[str]:
    """Return a list of internal ROOT paths to relevant trees in the files

    Args:
        particle: Particle type (K, pi, etc.)
        sample: Data sample name (Turbo18, etc.)
        override_tuple_names: Tree names to use instead of the default
    """
    tree_paths = []
    if is_simple(sample):
        # Run 1 (and Run 2 Electron) files have a simple structure with a single
        # tree
        tree_paths.append("DecayTree")
    elif override_tuple_names:
        log.debug("Tree paths overriden by tuple_names")
        tree_paths.extend(
            f"{tuple_name}/DecayTree" for tuple_name in override_tuple_names
        )

    else:
        tree_paths.extend(
            f"{tuple_name}/DecayTree" for tuple_name in TUPLE_NAMES[particle]
        )

    return tree_paths


def dataframe_from_local_file(path: str, branch_names: List[str]) -> pd.DataFrame:
    """Return a dataframe read from a local file (instead of EOS).

    Args:
        path: Path to the local file.
        branch_names: Columns to read from the DataFrame.
    """
    if path.endswith(".pkl"):
        df = pd.read_pickle(path)
    elif path.endswith(".csv"):
        df = pd.read_csv(path, index_col=0)
    else:
        log.error(
            (
                f"Local dataframe file '{path}' "
                f"has an unknown suffix (csv and pkl supported)"
            )
        )
        raise TypeError("Only csv and pkl files supported")
    log.info(f"Read {path} with a total of {len(df.index)} events")

    try:
        df = df[branch_names]
    except KeyError:
        log.error("The requested branches are missing from the local file")
        raise

    return df


def get_calib_hists(
    hist_dir: str,
    sample: str,
    magnet: str,
    ref_pars: Dict[str, List[str]],
    bin_vars: Dict[str, str],
) -> Dict[str, Dict[str, bh.Histogram]]:
    """Get calibration efficiency histograms from all necessary files.

    Args:
        hist_dir: Directory where to look for the required files.
        sample: Data sample name (Turbo18, etc.).
        magnet: Magnet polarity (up, down).
        ref_pars: Reference particle prefixes with a particle type and PID cut.
        bin_vars: Binning variables ({standard name: reference sample branch name}).

    Returns:
        Dictionary with an efficiency histogram for each reference particle.
        The reference particle prefixes are the dictionary keys.
    """
    hists: Dict[str, Dict[str, bh.Histogram]] = {}
    for ref_par in ref_pars:
        particle = ref_pars[ref_par][0]

        pid_cut = ref_pars[ref_par][1]
        whitespace = re.compile(r"\s+")
        pid_cut = re.sub(whitespace, "", pid_cut)

        calib_name = Path(
            hist_dir,
            utils.create_hist_filename(
                sample, magnet, particle, pid_cut, list(bin_vars)
            ),
        )

        log.debug(f"Loading efficiency histograms from '{calib_name}'")

        hists[ref_par] = {}
        try:
            with open(calib_name, "rb") as f:
                hists[ref_par]["eff"] = pickle.load(f)
                hists[ref_par]["passing"] = pickle.load(f)
                hists[ref_par]["total"] = pickle.load(f)
        except FileNotFoundError:
            log.error(
                (
                    "Efficiency histogram file not found. You must first "
                    "run make_eff_hists with matching parameters to create the "
                    "efficiency histograms."
                )
            )
            raise
    return hists


def save_dataframe_as_root(
    df: pd.DataFrame, name: str, filename: str, columns: Optional[List[str]] = None
) -> None:
    """Save a DataFrame as a TTree in a ROOT file.

    NaN entries are changed to -999 because ROOT TTrees don't support NaNs.

    Args:
        df: DataFrame to be saved.
        name: Name of the new TTree.
        filename: Name of the file to which to save the TTree.
        columns: Optional. Names of the columns which are to be saved. If
            'None', all the columns will be saved.
    """
    df_wo_nan = df.fillna(-999)
    if columns is None:
        columns = list(df_wo_nan.keys())
    branches_w_types = {branch: df_wo_nan[branch].dtype for branch in columns}
    with uproot.recreate(filename) as f:
        log.debug(f"Creating a TTree with the following branches: {branches_w_types}")
        f.mktree(name, branches_w_types)
        branch = {
            branch_name: df_wo_nan[branch_name] for branch_name in branches_w_types
        }
        f[name].extend(branch)
    log.info(f"Efficiency tree saved to {filename}")
