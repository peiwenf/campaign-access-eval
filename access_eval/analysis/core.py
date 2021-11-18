#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Union

import pandas as pd
from dataclasses_json import dataclass_json

from ..constants import SINGLE_PAGE_AXE_RESULTS_FILENAME
from ..utils import clean_url
from .constants import DatasetFields

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


@dataclass_json
@dataclass
class ViolationCounts:
    pages: int = 0
    minor: int = 0
    moderate: int = 0
    serious: int = 0
    critical: int = 0


def _get_counts(
    axe_results_dir: Path,
    counts: ViolationCounts,
) -> ViolationCounts:
    # Run _get_counts for all children dirs -- recursive
    for child in axe_results_dir.iterdir():
        if child.is_dir():
            counts = _get_counts(child, counts=counts)

    # Get this dirs result file
    this_dir_results = axe_results_dir / SINGLE_PAGE_AXE_RESULTS_FILENAME
    if this_dir_results.exists():
        with open(this_dir_results, "r") as open_f:
            this_dir_loaded_results = json.load(open_f)

        # Increment pages
        counts.pages += 1

        # Sum different violation levels for this page
        for violation in this_dir_loaded_results["violations"]:
            impact = violation["impact"]
            current_count = getattr(counts, impact)
            setattr(counts, impact, current_count + len(violation["nodes"]))

    return counts


def sum_axe_violation_levels(axe_results_dir: Union[str, Path]) -> ViolationCounts:
    """
    Sum the various levels of axe violations for a whole axe result tree.

    Parameters
    ----------
    axe_results_dir: Union[str, Path]
        The directory for a specific website that has been processed using the access
        eval scraper.

    Returns
    -------
    violation_counts: ViolationCounts
        The counts of all violation levels summed for the whole axe results tree.
    """
    # Handle path and dir checking
    axe_results_dir = Path(axe_results_dir).resolve(strict=True)
    if not axe_results_dir.is_dir():
        raise NotADirectoryError(axe_results_dir)

    # Run _get_counts for whole tree
    return _get_counts(axe_results_dir, ViolationCounts())


def _convert_violation_counts_to_expanded_data(
    counts: ViolationCounts,
    phase: str,
) -> Dict[str, int]:
    return {
        f"number_of_pages_{phase}": counts.pages,
        f"number_of_total_errors_{phase}": (
            counts.critical + counts.serious + counts.moderate + counts.minor
        ),
        f"number_of_critical_errors_{phase}": counts.critical,
        f"number_of_serious_errors_{phase}": counts.serious,
        f"number_of_moderate_errors_{phase}": counts.moderate,
        f"number_of_minor_errors_{phase}": counts.minor,
    }


def combine_election_data_with_axe_results(
    election_data: Union[str, Path, pd.DataFrame],
    pre_contact_axe_scraping_results: Union[str, Path],
    post_contact_axe_scraping_results: Union[str, Path],
) -> pd.DataFrame:
    """
    Combine election data CSV (or in memory DataFrame) with the axe results for each
    campaign website.

    Parameters
    ----------
    election_data: Union[str, Path, pd.DataFrame]
        The path to, or the in-memory dataframe, containing basic election data.
        This CSV or dataframe should contain a column "campaign_website_url"
        that can be used to find the associated directory of axe results for that
        campaigns website.
    pre_contact_axe_scraping_results: Union[str, Path]
        The path to the directory that contains sub-directories for each campaign
        website's axe results. I.e. data/site-a and data/site-b, provide the directory
        "data" as both "site-a" and "site-b" are direct children.
    post_contact_axe_scraping_results: Union[str, Path]
        The path to the directory that contains sub-directories for each campaign
        website's axe results. I.e. data/site-a and data/site-b, provide the directory
        "data" as both "site-a" and "site-b" are direct children.

    Returns
    -------
    full_data: pd.DataFrame
        The original election data and the summed violation counts for both pre and post
        contact for each campaign website combined into a single dataframe.

    Notes
    -----
    For both the *_axe_scraping_results parameters, provide the parent directory of all
    individual campaign axe scraping result directories.

    I.e. if the data is stored like so:
    |- pre-data/
        |- site-a/
        |- site-b/
    |- post-data/
        |- site-a/
        |- site-b/

    Provide the parameters as `"pre-data/"` and `"post-data/"` respectively.

    Additionally, if the provided campaign website url is missing from either the pre
    or post axe results directories, the site is skipped / dropped from the expanded
    dataset.

    Finally, any `https://` or `http://` is dropped from the campaign url.
    I.e. in the spreadsheet the value is `https://website.org` but the associated
    directory should be: `pre-data/website.org`
    """
    # Confirm paths
    pre_contact_axe_scraping_results = Path(pre_contact_axe_scraping_results).resolve(
        strict=True
    )
    post_contact_axe_scraping_results = Path(post_contact_axe_scraping_results).resolve(
        strict=True
    )
    if isinstance(election_data, (str, Path)):
        election_data = Path(election_data).resolve(strict=True)
        election_data = pd.read_csv(election_data)

    # Confirm axe scraping results is dir
    if not pre_contact_axe_scraping_results.is_dir():
        raise NotADirectoryError(pre_contact_axe_scraping_results)
    if not post_contact_axe_scraping_results.is_dir():
        raise NotADirectoryError(post_contact_axe_scraping_results)

    # Iter election data and create List of expanded dicts with added
    expanded_data = []
    for _, row in election_data.iterrows():
        cleaned_url = clean_url(row[DatasetFields.campaign_website_url])
        pre_access_eval = pre_contact_axe_scraping_results / cleaned_url
        post_access_eval = post_contact_axe_scraping_results / cleaned_url

        # Only continue with the addition if pre and post both exist
        if pre_access_eval.exists() and post_access_eval.exists():
            # Run summing
            pre_access_eval_counts = sum_axe_violation_levels(pre_access_eval)
            post_access_eval_counts = sum_axe_violation_levels(post_access_eval)

            # Combine and merge to expanded data
            expanded_data.append(
                {
                    **row,
                    **_convert_violation_counts_to_expanded_data(
                        pre_access_eval_counts,
                        "pre",
                    ),
                    **_convert_violation_counts_to_expanded_data(
                        post_access_eval_counts,
                        "post",
                    ),
                }
            )

    log.info(
        f"Dropped {len(election_data) - len(expanded_data)} rows from dataset "
        f"because they were missing a pre or post aXe result directory."
    )
    return pd.DataFrame(expanded_data)
