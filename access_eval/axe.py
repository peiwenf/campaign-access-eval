#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

import pandas as pd
from axe_selenium_python import Axe
from dataclasses_json import dataclass_json
from selenium import webdriver
from selenium.webdriver import FirefoxOptions

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


###############################################################################


@dataclass_json
@dataclass
class SimplifiedAxeViolation:

    id: str
    impact: str
    impact_score: int
    reason: str
    number_of_elements_in_violation: int
    help_url: str


###############################################################################


def generate_axe_evaluation(
    url: str,
    output_path: Optional[Union[str, Path]] = None,
    geckodriver_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Use Axe to generate an accessibility violation dataframe.

    Parameters
    ----------
    url: str
        The URL to the website to be evaluated for violations.
    output_path: Optional[Union[str, Path]]
        An optional path to store the violations to as JSON.
        Default: None (do not store to file)
    geckodriver_path: Optional[Union[str, Path]]
        An optional path to the location of the geckodriver executable.
        Default: None (Use OS Path for executable)

    Returns
    -------
    report: Dict[str, Any]
        The produced Axe report.

    Notes
    -----
    On Mac and Linux, the geckodriver_path must be stored in OS ENV PATH.
    Export to OS ENV PATH with: `export PATH=$PATH:{geckodriver_path}`

    On Windows, the geckodriver_path must be provided.
    """
    try:
        opts = FirefoxOptions()
        opts.add_argument("--headless")

        # Eval driver path
        if geckodriver_path is not None:
            if isinstance(geckodriver_path, str):
                geckodriver_path = Path(geckodriver_path)
                geckodriver_path = geckodriver_path.resolve(strict=True)
                if not geckodriver_path.is_file():
                    raise IsADirectoryError(
                        "Must provide the path to the geckodriver executable, "
                        "not the directory that contains the executable."
                    )

            # Init driver
            geckodriver = webdriver.Firefox(str(geckodriver_path), firefox_options=opts)

        # If geckodriver_path is None, then assume we are getting from OS path
        else:
            geckodriver = webdriver.Firefox(firefox_options=opts)

        # Determine storage route
        if output_path is not None:
            output_path = Path(output_path).resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)

        # Load content at the URI
        geckodriver.get(url)

        # Pass to Axe
        axe = Axe(geckodriver)
        axe.inject()

        # Run checks and store results
        results = axe.run()

        # Optional store
        if output_path is not None:
            axe.write_results(results, output_path)

    finally:
        # Close the window
        geckodriver.close()

    # Return as dataframe
    return results


def generate_report(
    url: str,
    output_dir: Optional[Union[str, Path]] = None,
    archive: bool = False,
    geckodriver_path: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Compile a full accessibility report for a URL.

    Parameters
    ----------
    url: str
        The URL to compile a report for.
    output_dir: Optional[Union[str, Path]]
        A specific directory to save the report to.
        Default: None (create new directory in current
        directory with the same name as the URL base path)
    archive: bool
        Should the report additionally be archived as tar/zip
        Default: False (do not archive)
    geckodriver_path: Optional[Union[str, Path]]
        See `access_eval.axe.generate_axe_evaluation` for details.

    Returns
    -------
    output_dir: Path
        The output directory where all report assets were stored.
    """
    # TODO: recurse web tree?
    # TODO: screenshot problematic elements? https://www.geeksforgeeks.org/screenshot-element-method-selenium-python/  # noqa: E501

    # Store name for many file naming operations
    resource_name = Path(url).name

    # Get or make output dir
    if output_dir is None:
        # Make the dir name the URL name
        # i.e. https://jacksonmaxfield.github.io -> jacksonmaxfield.github.io/
        output_dir = Path(resource_name)

    # Always path output dir
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process URL and compile report
    axe_results = generate_axe_evaluation(url, geckodriver_path=geckodriver_path)

    # Store axe results to outputs
    with open(output_dir / "full-axe-evaluation.json", "w") as open_resource:
        json.dump(axe_results, open_resource, indent=4)

    # Parse axe tree and construct helpful details
    simplified_violations = []
    for violation in axe_results["violations"]:
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

    # Compile simplified violations to table and
    # sort by the number of elements and severity
    compiled_simplified_violations = pd.DataFrame(
        [v.to_dict() for v in simplified_violations]  # type: ignore
    )
    compiled_simplified_violations = compiled_simplified_violations.sort_values(
        by=["number_of_elements_in_violation", "impact_score"], ascending=False
    )
    compiled_simplified_violations.to_csv(
        output_dir / "accessibility-violations-summarized.csv", index=False
    )

    # Compile archive
    if archive:
        shutil.make_archive(f"{resource_name}--report", "tar", output_dir)

    return output_dir
