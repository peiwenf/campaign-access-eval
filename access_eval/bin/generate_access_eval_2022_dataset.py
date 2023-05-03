#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import sys
import traceback

from access_eval.analysis import constants_2022
from access_eval.analysis.core_2022 import combine_election_data_with_axe_results
from access_eval.analysis.utils_2022 import unpack_data

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
            prog="generate-access-eval-2022-dataset",
            description=(
                "Generate the access evaluation dataset for all races covered in the "
                "2022 preliminary study."
            ),
        )
        p.parse_args(namespace=self)


###############################################################################


def main() -> None:
    try:
        _ = Args()

        # Unpack and store
        eval_data = unpack_data(
            constants_2022.ACCESS_EVAL_2022_EVALS_ZIP,
            constants_2022.ACCESS_EVAL_2022_EVALS_UNPACKED,
            clean=True,
        )

        # Combine
        expanded_data = combine_election_data_with_axe_results(
            constants_2022.ACCESS_EVAL_2022_ELECTION_RESULTS,
            eval_data,
        )
        
        # Store to data dir
        expanded_data.to_csv(constants_2022.ACCESS_EVAL_2022_DATASET, index=False)
        # test local
        # expanded_data.to_csv('data_test.csv', index=False)

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
