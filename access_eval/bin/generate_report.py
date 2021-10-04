#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import sys
import traceback
from pathlib import Path
from typing import Optional

from access_eval.axe import generate_report

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
            prog="access-eval-generate-report",
            description="Generate an accessibility evaluation report.",
        )
        p.add_argument(
            "url",
            type=str,
            help="The URL to compile a report for.",
        )
        p.add_argument(
            "-o",
            "--output_dir",
            type=Path,
            default=None,
            help=(
                "A specific directory to save the report to. "
                "Default: None (create new directory in current "
                "directory with the same name as the URL base path)"
            ),
        )
        p.add_argument(
            "-a",
            "--archive",
            action="store_true",
            help="Should the report additionally be archived as tar/zip",
        )
        p.add_argument(
            "-g",
            "--geckodriver_path",
            type=Path,
            default=None,
            help="See `access_eval.axe.generate_axe_evaluation` for details.",
        )
        p.parse_args(namespace=self)


###############################################################################


def _generate(
    url: str,
    output_dir: Optional[Path] = None,
    archive: bool = False,
    geckodriver_path: Optional[Path] = None,
) -> None:
    # Run report and log needed info
    output_dir = generate_report(
        url=url,
        output_dir=output_dir,
        archive=archive,
        geckodriver_path=geckodriver_path,
    )

    log.info("Completed report generation.")
    log.info(f"Report stored to: {output_dir.resolve(strict=True)}")

    # Log archive location
    if archive:
        archive_location = Path(f"{output_dir}.tar").resolve(strict=True)
        log.info(f"Archive stored to: {archive_location}")


def main() -> None:
    try:
        args = Args()
        _generate(
            url=args.url,
            output_dir=args.output_dir,
            archive=args.archive,
            geckodriver_path=args.geckodriver_path,
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
