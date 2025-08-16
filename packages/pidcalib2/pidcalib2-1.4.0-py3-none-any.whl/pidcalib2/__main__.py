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

"""This module prints an error message when calling pidcalib2 directly.

The pidcalib2 package is not meant to be called directly - one has to call one
of the work modules, e.g., pidcalib2.make_eff_hists. More info in README.md.
"""
import sys

if __name__ == "__main__":
    print("You must call one of the work modules, e.g., pidcalib2.make_eff_hists.")
    sys.exit(1)
