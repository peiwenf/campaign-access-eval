#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Union

import pandas as pd
from dataclasses_json import dataclass_json

from .. import constants

###############################################################################
# Axe look up tables and constants
# Pulled from: https://github.com/dequelabs/axe-core/blob/55fb7c00e866ab17486ff114932199f8f9661389/build/configure.js#L42  # noqa: E501


class AxeImpact:
    minor: str = "minor"
    moderate: str = "moderate"
    serious: str = "serious"
    critical: str = "critical"


AXE_IMPACT_SCORE_LUT = {
    AxeImpact.minor: 1,
    AxeImpact.moderate: 2,
    AxeImpact.serious: 3,
    AxeImpact.critical: 4,
}


@dataclass_json
@dataclass
class SimplifiedAxeViolation:
    id: str
    impact: str
    impact_score: int
    reason: str
    number_of_elements_in_violation: int
    help_url: str


@dataclass_json
@dataclass
class AggregateAxeViolation:
    id: str
    impact: str
    impact_score: int
    reason: str
    number_of_pages_affected: int
    number_of_elements_in_violation: int
    help_url: str


###############################################################################


def generate_high_level_statistics(head_dir: Union[str, Path]) -> None:
    """
    Recursive glob of all directories for axe results and generate high level
    statistics both for single page and whole website.

    Parameters
    ----------
    head_dir: Union[str, Path]
        The directory to start the recursive glob for axe results in.
    """
    # Get all individual page axe results to consolidate
    if isinstance(head_dir, str):
        head_dir = Path(head_dir)

    # Resolve
    head_dir = head_dir.resolve(strict=True)
    if head_dir.is_file():
        raise NotADirectoryError(str(head_dir))

    # Iter results and combine
    overall_stats = {}
    for axe_result_file in head_dir.glob(
        f"**/{constants.SINGLE_PAGE_AXE_RESULTS_FILENAME}"
    ):
        simplified_violations = []
        # Open result file
        with open(axe_result_file, "r") as open_f:
            single_page_axe_results = json.load(open_f)

        # Parse and simplify
        for violation in single_page_axe_results["violations"]:
            # Add to this pages violations
            simplified_violations.append(
                SimplifiedAxeViolation(
                    id=violation["id"],
                    impact=violation["impact"],
                    impact_score=AXE_IMPACT_SCORE_LUT[violation["impact"]],
                    reason=violation["help"],
                    number_of_elements_in_violation=len(violation["nodes"]),
                    help_url=violation["helpUrl"],
                )
            )

            # Set or update the overall stats
            if violation["id"] not in overall_stats:
                overall_stats[violation["id"]] = AggregateAxeViolation(
                    id=violation["id"],
                    impact=violation["impact"],
                    impact_score=AXE_IMPACT_SCORE_LUT[violation["impact"]],
                    reason=violation["help"],
                    number_of_pages_affected=1,
                    number_of_elements_in_violation=len(violation["nodes"]),
                    help_url=violation["helpUrl"],
                )

            else:
                overall_stats[violation["id"]].number_of_pages_affected += 1
                overall_stats[violation["id"]].number_of_elements_in_violation += len(
                    violation["nodes"]
                )

        # Compile simplified violations to table and
        # sort by the number of elements and severity
        compiled_simplified_violations = pd.DataFrame(
            [v.to_dict() for v in simplified_violations],  # type: ignore
            columns=[
                "id",
                "impact",
                "impact_score",
                "reason",
                "number_of_elements_in_violation",
                "help_url",
            ],
        )
        compiled_simplified_violations = compiled_simplified_violations.sort_values(
            by=["number_of_elements_in_violation", "impact_score"], ascending=False
        )
        compiled_simplified_violations.to_csv(
            axe_result_file.parent
            / constants.SINGLE_PAGE_SIMPLIFIED_AXE_RESULTS_FILENAME,
            index=False,
        )

    # Compile overall stats
    overall_simplified_violations = pd.DataFrame(
        [v.to_dict() for v in overall_stats.values()]  # type: ignore
    )
    overall_simplified_violations = overall_simplified_violations.sort_values(
        by=[
            "number_of_elements_in_violation",
            "impact_score",
            "number_of_pages_affected",
        ],
        ascending=False,
    )
    overall_simplified_violations.to_csv(
        head_dir / constants.AGGREGATE_AXE_RESULTS_FILENAME,
        index=False,
    )
