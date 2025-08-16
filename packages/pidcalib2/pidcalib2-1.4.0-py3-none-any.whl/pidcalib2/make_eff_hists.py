# sourcery skip: require-return-annotation
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

"""Module to make LHCb PID efficiency histograms.

This module creates histograms that can be used to estimate the PID
efficiency of a user's sample.

Examples:
    Create a single efficiency histogram for a single PID cut::

        $ python -m src.pidcalib2.make_eff_hists --sample=Turbo18 --magnet=up \
            --particle=Pi --pid-cut="DLLK > 4" --bin-var=P --bin-var=ETA \
            --bin-var=nSPDHits --output-dir=pidcalib_output

    Create multiple histograms in one run (most of the time is spent reading
    in data, so specifying multiple cuts is much faster than running
    make_eff_hists sequentially)::

        $ python -m src.pidcalib2.make_eff_hists --sample=Turbo16 --magnet=up \
            --particle=Pi --pid-cut="DLLK > 0" --pid-cut="DLLK > 4" \
            --pid-cut="DLLK > 6" --bin-var=P --bin-var=ETA \
            --bin-var=nSPDHits --output-dir=pidcalib_output
"""

import argparse
import json
import logging
import pathlib
import pickle
import re
import sys
# import time
from typing import List

import logzero
# from lb_telemetry.logger import Logger
from logzero import logger as log

from pidcalib2 import argparse_tools, binning, utils

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
            "This module creates histograms that can be used to estimate "
            "the PID efficiency of a user's sample."
            "\n\n"
            "Reading all the relevant calibration files can take a long time. "
            "When running a configuration for the first time, we recommend using "
            "the --max-files 1 option. This will limit PIDCalib2 to reading just "
            "a single calibration file. Such a test will reveal any problems "
            "with, e.g., missing variables quickly. Keep in mind that you might "
            "get a warning about empty bins in the total histogram as you are "
            "reading a small subset of the calibration data. For the purposes of "
            "a quick test, this warning can be safely ignored."
        ),
    )
    parser.add_argument(
        "-s",
        "--sample",
        help="calibration sample; see pidcalib2.make_eff_hists --list configs",
        required=True,
        type=str,
    )
    parser.add_argument(
        "-m",
        "--magnet",
        help="magnet polarity",
        required=True,
        choices=["up", "down"],
    )
    parser.add_argument(
        "-p",
        "--particle",
        help="particle type; see pidcalib2.make_eff_hists --list configs",
        required=True,
    )
    parser.add_argument(
        "-i",
        "--pid-cut",
        help=(
            "PID cut string, e.g., 'DLLK < 4.0' (-i can be used multiple times for "
            "multiple cuts)."
        ),
        action="append",
        dest="pid_cuts",
        required=True,
    )
    parser.add_argument(
        "-c",
        "--cut",
        help=(
            "arbitrary cut string, e.g., 'Dst_IPCHI2 < 10.0' (-c can be used multiple "
            "times for multiple cuts)."
        ),
        action="append",
        dest="cuts",
    )
    parser.add_argument(
        "-b",
        "--bin-var",
        help=(
            "binning variable (-b can be used multiple times for a multi-dimensional "
            "binning)"
        ),
        action="append",
        dest="bin_vars",
        required=True,
    )
    parser.add_argument(
        "-g",
        "--binning-file",
        help="file where new/alternative binnings are defines",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="pidcalib_output",
        help="directory where to save output files",
    )
    parser.add_argument(
        "-l",
        "--list",
        action=argparse_tools.ListValidAction,
        help="list all [configs, aliases]",
    )
    parser.add_argument(
        "-d",
        "--local-dataframe",
        help="(debug) read a calibration DataFrame from file",
    )
    parser.add_argument(
        "-f",
        "--file-list",
        help="(debug) read calibration file paths from a text file",
    )
    parser.add_argument(
        "-a",
        "--samples-file",
        help="(debug) read calibration sample lists from a custom file",
    )
    parser.add_argument(
        "-n",
        "--max-files",
        type=int,
        help="(debug) a max number of files to read",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="(debug) increase verbosity",
    )
    parser.add_argument("-V", "--version", action="version", version=VERSION)
    return parser.parse_args(args)


def make_eff_hists(config: dict) -> None:
    """Create sWeighted PID calibration histograms and save them to disk.

    Calibration samples from EOS are read and relevant branches extracted to
    a DataFrame. Each PID cut is applied to the DataFrame in turn and the
    results are histogrammed (each event with its associated sWeight).
    Particle type and binning variables are used to select an appropriate
    predefined binning. The efficiency histograms are saved to a requested
    output directory.

    Args:
        config: A configuration dictionary. See decode_arguments(args) for
            details.
    """
    if config["verbose"]:
        logzero.loglevel(logging.DEBUG)
    else:
        logzero.loglevel(logging.INFO)

    pattern = re.compile(r"\s+")
    config["pid_cuts"] = [
        re.sub(pattern, "", pid_cut) for pid_cut in config["pid_cuts"]
    ]

    config["version"] = VERSION
    log.info("Running PIDCalib2 make_eff_hists with the following config:")
    utils.log_config(config)

    if not config["cuts"]:
        log.warning(
            "No --cut specified. Cuts on PID samples should match your sample cuts."
        )

    output_dir = pathlib.Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    binning.check_and_load_binnings(
        config["particle"], config["bin_vars"], config.get("binning_file", None)
    )

    if config["local_dataframe"]:
        hists = utils.create_histograms_from_local_dataframe(config)
    else:
        hists = utils.add_hists(list(utils.create_histograms(config).values()))

    eff_hists = utils.create_eff_histograms(hists)

    for name in eff_hists:
        if name.startswith("eff_"):
            cut = name.replace("eff_", "")
            hist_filename = utils.create_hist_filename(
                config["sample"],
                config["magnet"],
                config["particle"],
                cut,
                config["bin_vars"],
            )
            eff_hist_path = output_dir / hist_filename
            with open(eff_hist_path, "wb") as f:
                pickle.dump(eff_hists[f"eff_{cut}"], f)
                pickle.dump(eff_hists[f"passing_{cut}"], f)
                pickle.dump(eff_hists["total"], f)

            log.info(f"Efficiency histograms saved to '{eff_hist_path}'")


def build_telemetry_payload(exec_time: float, config: dict) -> dict:
    args = ["binning_file", "local_dataframe", "file_list", "samples_file"]

    return {
        "sample": config["sample"],
        "magnet": config["magnet"],
        "particle": config["particle"],
        "pid_cuts": "[]"
        if config["pid_cuts"] is None
        else json.dumps(config["pid_cuts"]),
        "cuts": "[]" if config["cuts"] is None else json.dumps(config["cuts"]),
        "max_files": 0 if config["max_files"] is None else config["max_files"],
        "bin_vars": "[]"
        if config["bin_vars"] is None
        else json.dumps(config["bin_vars"]),
        "args": json.dumps({key: config[key] for key in args if key in config}),
        "exec_time": exec_time,
        "version": VERSION,
    }


def main():  # sourcery skip: docstrings-for-functions
    config = vars(decode_arguments(sys.argv[1:]))

    # start_time = time.perf_counter()
    make_eff_hists(config)
    # exec_time = time.perf_counter() - start_time

    # telemetry = build_telemetry_payload(exec_time, config)
    # logger = Logger()
    # _ = logger.log_to_monit(
    #     "PIDCalib2",
    #     telemetry,
    #     tags=["sample", "magnet", "particle", "version"],
    # )


if __name__ == "__main__":
    main()
