#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import sys
import traceback
from shutil import rmtree

from access_eval.analysis import plotting
from access_eval.analysis.core import (
    flatten_access_eval_2021_dataset,
    get_statistical_difference_crucial_stats,
    load_access_eval_2021_dataset,
)

###############################################################################

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)4s: %(module)s:%(lineno)4s %(asctime)s] %(message)s",
)
log = logging.getLogger(__name__)

###############################################################################


class Args(argparse.Namespace):
    def __init__(self) -> None:
        self.__parse()

    def __parse(self) -> None:
        p = argparse.ArgumentParser(
            prog="analyze-access-eval-2021-dataset",
            description=(
                "Generate the access evaluation dataset plots and tables for "
                "all races covered in the 2021 preliminary study."
            ),
        )
        p.add_argument(
            "--all-plots",
            dest="all_plots",
            action="store_true",
            help=(
                "Should all plots be generated (including ones not in the final paper)."
            ),
        )
        p.parse_args(namespace=self)


###############################################################################


def main() -> None:
    try:
        args = Args()

        # Load data
        data = load_access_eval_2021_dataset()
        flat_data = flatten_access_eval_2021_dataset(data)

        # Clear prior plots
        if plotting.PLOTTING_DIR.exists():
            rmtree(plotting.PLOTTING_DIR)

        # Generate plots
        log.info("Generating plots used in paper...")
        plotting.plot_summary_stats(flat_data)
        plotting.plot_location_based_summary_stats(flat_data)
        plotting.plot_election_result_based_summary_stats(flat_data)
        plotting.plot_electoral_position_based_summary_stats(flat_data)
        plotting.plot_candidate_position_based_summary_stats(flat_data)
        plotting.plot_pre_post_errors(flat_data)

        # Generate stats and print
        stats = get_statistical_difference_crucial_stats(flat_data)
        log.info(f"Statistics examined in paper:\n{stats}")
        with open("stats.json", "w") as open_f:
            json.dump(stats, open_f)

        # Generate full plots
        if args.all_plots:
            log.info("Generating extra plots...")
            plotting.plot_computed_fields_over_vote_share(data)
            plotting.plot_pre_post_fields_compare(data)
            plotting.plot_categorical_against_errors_boxplots(flat_data)
            plotting.plot_locations_against_errors_boxplots(flat_data)
            plotting.plot_error_types_boxplots(flat_data)

    except Exception as e:
        log.error("=============================================")
        log.error("\n\n" + traceback.format_exc())
        log.error("=============================================")
        log.error("\n\n" + str(e) + "\n")
        log.error("=============================================")
        sys.exit(1)


###############################################################################
# Allow caller to directly run this module (usually in development scenarios)

if __name__ == "__main__":
    main()
