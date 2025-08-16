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

"""Module that contains contains overrides for argparse.

It allows us to print the valid configs and aliases when the user requests it,
as well as print the default values for parameters together with a
RawDecription (allowing more control over formatting).
"""

import argparse
import contextlib
from logzero import logger as log

from pidcalib2 import markdown_table, pid_data


class ListValidAction(argparse.Action):
    """Class that overrides required parameters and prints valid configs."""

    def __call__(self, parser, namespace, values, option_string=None):
        # sourcery skip: docstrings-for-functions

        if values == "configs" or values.endswith(".json"):
            header = ["Sample", "Magnet", "Particle"]
            table = markdown_table.MarkdownTable(header)

            # Print configs from the default samples.json if no file specified
            if values == "configs":
                values = None

            for entry in pid_data.get_calibration_samples(values).keys():
                # Skip group entries like "Turbo18-MagUp"
                with contextlib.suppress(ValueError):
                    sample, magnet, particle = entry.split("-")
                    magnet = magnet[3:].lower()
                    table.add_row([sample, magnet, particle])
            table.print()

        elif values == "aliases":
            print(
                "For data collected in Run 1 and 2, "
                "the following aliases are available: "
            )
            table_pid = markdown_table.MarkdownTable(["Alias", "Variable"])
            for alias, var in pid_data.ALIASES.items():
                table_pid.add_row([alias, var])
            table_pid.print()
            print("\n{}\n".format("=" * 87))
            print("For data collected in Run 3, the following aliases are available: ")
            table_pid = markdown_table.MarkdownTable(["Alias", "Variable"])
            for alias, var in pid_data.RUN3_ALIASES.items():
                if "{}" in var:
                    table_pid.add_row([alias, var.replace("{}", "{particle}")])
                else:
                    table_pid.add_row([alias, var])
            table_pid.print()
        else:
            log.error(f"'{values}' is not a known keyword for list-valid")
            raise KeyError

        parser.exit()


class RawDefaultsFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    """Combines the ArgumentDefaults and the RawDescription formatters."""

    pass
