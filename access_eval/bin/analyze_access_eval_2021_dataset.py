#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import sys
import traceback

from access_eval.analysis import plotting
from access_eval.analysis.core import (
    flatten_access_eval_2021_dataset,
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
        p.parse_args(namespace=self)


###############################################################################


def main() -> None:
    try:
        _ = Args()

        # Load data
        data = load_access_eval_2021_dataset()
        flat_data = flatten_access_eval_2021_dataset(data)

        # Generate full plots
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
