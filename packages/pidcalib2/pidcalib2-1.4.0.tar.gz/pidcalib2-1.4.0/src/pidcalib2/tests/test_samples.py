###############################################################################
# (c) Copyright 2024 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import os
import json
from pathlib import Path
from pyxrootd import client

import pytest

from apd import AnalysisData


@pytest.fixture
def test_path():
    return Path(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.xrootd
@pytest.mark.slow
def test_samples(test_path):
    sample_config_filepath = test_path / "../data/samples.json"
    fs = client.FileSystem("root://eoslhcb.cern.ch/")
    with open(sample_config_filepath, "rb") as f:
        samples = json.load(f)
    for name in samples.keys():
        if "2023" in name or "2024" in name:  # only check for run 3
            for s in samples[name]["sweight_dir"]:
                dirname = s.split(".ch/")[-1]
                assert fs.stat(dirname), f"{dirname} not a directory"
        if "calib_files" in samples[name].keys():  # check for run 1, 2, and 3
            datasets = AnalysisData("pid", samples[name]["calib_files"]["analysis"])
            samples[name]["files"] = datasets(
                    polarity=samples[name]["calib_files"]["polarity"],
                    eventtype=samples[name]["calib_files"]["eventtype"],
                    datatype=samples[name]["calib_files"]["datatype"],
                    version=samples[name]["calib_files"]["version"],
                    name=samples[name]["calib_files"]["name"]
                    )
            if "start_file" in samples[name]["calib_files"]:
                first_file = samples[name]["calib_files"]["start_file"]-1
                samples[name]["files"] = samples[name]["files"][first_file:]
        if "link" not in samples[name].keys():
            for f in samples[name]["files"]:
                filepath = f.split(".ch/")[-1]
                assert fs.stat(filepath), f"{filepath} not found"
                if "2023" in name or "2024" in name:  # only check for run 3
                    filename = filepath.split("/")[-1]
                    sweights_filename = filename.replace(".root", "_sweights.root")
                    sweights_filepath = f"{dirname}{sweights_filename}"
                    assert fs.stat(sweights_filepath), f"{sweights_filepath} not found"
