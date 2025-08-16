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

"""Convert pickled PIDCalib2 histograms to TH*D & save them in a ROOT file.

Only 1D, 2D, and 3D histograms are supported by ROOT. Attempting to convert
higher-dimensional histograms will result in an exception.
"""

import argparse
import itertools
import logging
import math
import pathlib
import pickle
import sys
from typing import Dict, List, Optional, Union

import boost_histogram as bh
import logzero
import ROOT
from logzero import logger as log

from pidcalib2 import argparse_tools

try:
    from pidcalib2.version import version as VERSION  # type: ignore
except ImportError:
    VERSION = "N/A"


def decode_arguments(args: List[str]) -> argparse.Namespace:
    """Decode CLI arguments."""
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        formatter_class=argparse_tools.RawDefaultsFormatter,
        description=(
            "This tool converts pickled PIDCalib2 histograms to TH*D and saves "
            "them in a ROOT file. It can be used on histograms produced by "
            "make_eff_hists or plot_calib_distributions. Note that ROOT supports "
            "only 1-, 2-, and 3-dimensional histograms; attempting to convert "
            "higher-dimensional histograms will fail."
        ),
    )
    parser.add_argument(
        "input",
        help="path to the input pickle file",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="(debug) increase verbosity",
    )
    parser.add_argument("-V", "--version", action="version", version=VERSION)
    return parser.parse_args(args)


def convert_to_root_histo(
    name: str, bh_histo: bh.Histogram, bh_error_histo: Optional[bh.Histogram] = None
) -> Union[ROOT.TH1D, ROOT.TH2D, ROOT.TH3D]:
    """Convert boost_histogram histogram to a ROOT histogram.

    Only 1D, 2D, and 3D histograms are supported by ROOT. Attempting to convert
    higher-dimensional histograms will result in an exception.

    Furthermore, the boost histogram must have a storage type that stores
    variance, e.g., Weight.

    Args:
        name: Name of the new ROOT histogram.
        bh_histo: The histogram to convert.

    Returns:
        The converted ROOT histogram. Type depends on dimensionality.
    """
    histo = None
    if len(bh_histo.axes) == 1:
        histo = ROOT.TH1D(name, name, 3, 0, 1)
        histo.SetBins(bh_histo.axes[0].size, bh_histo.axes[0].edges)
        histo.GetXaxis().SetTitle(bh_histo.axes[0].metadata["name"])
    elif len(bh_histo.axes) == 2:
        histo = ROOT.TH2D(name, name, 3, 0, 1, 3, 0, 1)
        histo.SetBins(
            bh_histo.axes[0].size,
            bh_histo.axes[0].edges,
            bh_histo.axes[1].size,
            bh_histo.axes[1].edges,
        )
        histo.GetXaxis().SetTitle(bh_histo.axes[0].metadata["name"])
        histo.GetYaxis().SetTitle(bh_histo.axes[1].metadata["name"])
    elif len(bh_histo.axes) == 3:
        histo = ROOT.TH3D(name, name, 3, 0, 1, 3, 0, 1, 3, 0, 1)
        histo.SetBins(
            bh_histo.axes[0].size,
            bh_histo.axes[0].edges,
            bh_histo.axes[1].size,
            bh_histo.axes[1].edges,
            bh_histo.axes[2].size,
            bh_histo.axes[2].edges,
        )
        histo.GetXaxis().SetTitle(bh_histo.axes[0].metadata["name"])
        histo.GetYaxis().SetTitle(bh_histo.axes[1].metadata["name"])
        histo.GetZaxis().SetTitle(bh_histo.axes[2].metadata["name"])
    else:
        raise TypeError(f"{len(bh_histo.axes)}D histograms not supported by ROOT")

    indices_ranges = [list(range(n)) for n in bh_histo.axes.size]
    for indices_tuple in itertools.product(*indices_ranges):
        root_indices = [index + 1 for index in indices_tuple]
        histo.SetBinContent(
            histo.GetBin(*root_indices), bh_histo[indices_tuple].value  # type: ignore
        )
        histo.SetBinError(
            histo.GetBin(*root_indices), math.sqrt(bh_histo[indices_tuple].variance)  # type: ignore # noqa
        )

    return histo


def convert_pklfile_to_rootfile(path: str) -> None:
    """Convert pickled PIDCalib2 histograms to TH*D & save them in a ROOT file.

    The resulting ROOT file has the same name (and path) as the input file, with
    the suffix changed from .pkl to .root.

    Args:
        path: Path of the Pickle file to convert.
    """
    pkl_path = pathlib.Path(path)
    histos: Dict[str, bh.Histogram] = {}
    with open(pkl_path, "rb") as f:
        while True:
            try:
                histo = pickle.load(f)
            except EOFError:
                if not histos:
                    log.error(f"No objects found in '{pkl_path}'")
                    raise
                break

            try:
                histo.metadata["name"]
            except TypeError:
                log.error(
                    f"It seems '{pkl_path}' is not a PIDCalib2 pickle file or "
                    "was made using a version older than 1.1.0"
                )
                raise

            log.debug(f"Unpickling histogram '{histo.metadata['name']}'")
            assert isinstance(histo, bh.Histogram)
            histos[histo.metadata["name"]] = histo

        root_path = pkl_path.with_suffix(".root")
        root_file = ROOT.TFile(str(root_path), "RECREATE")

        for histo in histos.values():
            name = histo.metadata["name"]
            log.info(f"Converting histogram '{histo.metadata['name']}'")
            root_histo = convert_to_root_histo(name, histos[name])
            root_histo.Write()

        log.info(f"Writing ROOT histograms to '{root_path}'")
        root_file.Close()


def main():  # sourcery skip: docstrings-for-functions, require-return-annotation
    config = decode_arguments(sys.argv[1:])
    if config.verbose:
        logzero.loglevel(logging.DEBUG)
    else:
        logzero.loglevel(logging.INFO)
    convert_pklfile_to_rootfile(sys.argv[1])


if __name__ == "__main__":
    main()
