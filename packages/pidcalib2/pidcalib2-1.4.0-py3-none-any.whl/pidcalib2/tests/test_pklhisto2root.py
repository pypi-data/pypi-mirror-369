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

import math
import os
import pickle
import shutil
from pathlib import Path

import pytest
import uproot

try:
    from pidcalib2 import pklhisto2root
except ModuleNotFoundError:
    pytest.skip("PyROOT not available", allow_module_level=True)


@pytest.fixture
def test_path():
    return Path(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.pyroot
def test_pklhisto2root_old(test_path, tmp_path):
    shutil.copy(
        test_path / "test_data/effhists-Turbo18-up-K-DLLK>0-P-pre1.1.0.pkl",
        tmp_path / "effhists-Turbo18-up-K-DLLK>0-P-pre1.1.0.pkl",
    )
    pkl_path = tmp_path / "effhists-Turbo18-up-K-DLLK>0-P-pre1.1.0.pkl"
    # Test that using old pickle files without metadata raises an error
    with pytest.raises(TypeError):
        pklhisto2root.convert_pklfile_to_rootfile(pkl_path)


@pytest.mark.pyroot
def test_pklhisto2root(test_path, tmp_path):
    shutil.copy(
        test_path / "test_data/effhists-Turbo18-up-K-DLLK>0-P.pkl",
        tmp_path / "effhists-Turbo18-up-K-DLLK>0-P.pkl",
    )
    pkl_path = tmp_path / "effhists-Turbo18-up-K-DLLK>0-P.pkl"
    root_path = tmp_path / "effhists-Turbo18-up-K-DLLK>0-P.root"
    pklhisto2root.convert_pklfile_to_rootfile(pkl_path)
    names = ["eff_DLLK>0", "passing_DLLK>0", "total"]
    boost_hists = {}
    with open(pkl_path, "rb") as f:
        for name in names:
            boost_hists[name] = pickle.load(f)

    assert root_path.exists()
    root_file = uproot.open(root_path)

    for name in names:
        assert root_file[name].values()[0] == pytest.approx(
            boost_hists[name].values()[0]
        )
        assert root_file[name].errors()[0] == pytest.approx(  # type: ignore
            math.sqrt(boost_hists[name].variances()[0])
        )
