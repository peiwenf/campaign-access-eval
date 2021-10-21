#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import sys
import traceback

from access_eval.analysis.parse_axe_results import generate_high_level_statistics

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
            prog="parse-axe-results",
            description=(
                "Generate high level statistics from a directory of axe results."
            ),
        )
        p.add_argument(
            "head_dir",
            type=str,
            help=(
                "The directory containing all results for an already analyzed website. "
                "Note: This bin script will clean the `https://` or `http://` prefix "
                "from a provided string."
            ),
        )
        p.parse_args(namespace=self)


###############################################################################


def main() -> None:
    try:
        args = Args()
        generate_high_level_statistics(
            head_dir=args.head_dir.replace("https://", "").replace("http://", ""),
        )
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
