#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import sys
import traceback

from access_eval.analysis import constants
from access_eval.analysis.core import combine_election_data_with_axe_results
from access_eval.analysis.utils import unpack_data

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
            prog="process-access-eval-2021-results",
            description=(
                "Process the access evaluation results for all races covered in the "
                "2021 preliminary study."
            ),
        )
        p.parse_args(namespace=self)


###############################################################################


def main() -> None:
    try:
        _ = Args()

        # Unpack and store
        pre_eval_data = unpack_data(
            constants.ACCESS_EVAL_2021_PRE_CONTACT_EVALS_ZIP,
            constants.ACCESS_EVAL_2021_PRE_CONTACT_EVALS_UNPACKED,
            clean=True,
        )
        post_eval_data = unpack_data(
            constants.ACCESS_EVAL_2021_POST_CONTACT_EVALS_ZIP,
            constants.ACCESS_EVAL_2021_POST_CONTACT_EVALS_UNPACKED,
            clean=True,
        )

        # Combine
        expanded_data = combine_election_data_with_axe_results(
            constants.ACCESS_EVAL_2021_ELECTION_RESULTS,
            pre_eval_data,
            post_eval_data,
        )

        # Store local
        expanded_data.to_csv("combined-study-data.csv", index=False)

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
