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

import os
from pathlib import Path

import pytest

from pidcalib2 import ref_calib


@pytest.fixture
def test_path():
    return Path(os.path.dirname(os.path.abspath(__file__)))


def test_ref_calib_ElectronTables(test_path, tmp_path):
    config = {
        "sample": "2024_WithUT_block1_Tables_2brem",
        "magnet": "up",
        "bin_vars": '{"P": "P"}',
        "histo_dir": (str(test_path / "test_data")),
        "output_file": str(
            tmp_path / "PIDCalibResultsElectronTables.root"
        ),
        "merge": False,
        "ref_file": str(
            test_path / "test_data/ref_test_data_ElectronTables.root"
        ),
        "ref_tree": "DecayTree",
        "ref_pars": '{"eprobe": ["e", "DLLe > 0"]}',
        "verbose": False,
    }
    ref_calib.ref_calib(config)
    assert (tmp_path / "PIDCalibResultsElectronTables.root").exists()
