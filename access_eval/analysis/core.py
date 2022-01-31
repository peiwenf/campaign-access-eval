#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

import pandas as pd
from dataclasses_json import dataclass_json
from scipy import stats as sci_stats
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import FirefoxOptions
from textstat import flesch_reading_ease
from tqdm import tqdm

from ..constants import AGGREGATE_AXE_RESULTS_FILENAME, SINGLE_PAGE_AXE_RESULTS_FILENAME
from ..utils import clean_url
from .constants import (
    ACCESS_EVAL_2021_DATASET,
    ComputedField,
    ComputedFields,
    DatasetFields,
)

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


@dataclass_json
@dataclass
class WordMetric:
    words: int
    unique_words: Set[str]
    ease_of_reading: float


@dataclass_json
@dataclass
class RunningMetrics:
    pages: int = 0
    minor_violations: int = 0
    moderate_violations: int = 0
    serious_violations: int = 0
    critical_violations: int = 0
    word_metrics: Optional[Dict[str, Optional[WordMetric]]] = None


@dataclass_json
@dataclass
class CompiledMetrics:
    pages: int = 0
    minor_violations: int = 0
    moderate_violations: int = 0
    serious_violations: int = 0
    critical_violations: int = 0
    number_of_words: int = 0
    number_of_unique_words: int = 0
    ease_of_reading: float = 0.0
    error_types: Optional[Dict[str, int]] = None


###############################################################################


def _process_page_words(url: str) -> Optional[WordMetric]:
    # Spawn webdriver process
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(firefox_options=opts)

    # Load site
    metric: Optional[WordMetric]
    try:
        driver.get(url)
        text = driver.find_element_by_tag_name("body").text
        tokens = text.split()
        metric = WordMetric(
            words=len(tokens),
            # Lowercase
            # Keep only alphanumeric characters
            # Convert to set
            unique_words=set([re.sub(r"[^a-z0-9]", "", t.lower()) for t in tokens]),
            ease_of_reading=flesch_reading_ease(text),
        )

    except WebDriverException as e:
        log.error(
            f"Failed to create webdriver for page word metrics for page: '{url}' -- {e}"
        )
        metric = None

    finally:
        # Run checks and store results
        driver.close()

    return metric


def _recurse_axe_results(
    axe_results_dir: Path,
    metrics: RunningMetrics,
) -> RunningMetrics:
    # Run _recurse_axe_results for all children dirs -- recursive
    for child in axe_results_dir.iterdir():
        if child.is_dir():
            metrics = _recurse_axe_results(child, metrics=metrics)

    # Get this dirs result file
    this_dir_results = axe_results_dir / SINGLE_PAGE_AXE_RESULTS_FILENAME
    if this_dir_results.exists():
        with open(this_dir_results, "r") as open_f:
            this_dir_loaded_results = json.load(open_f)

        # Increment pages
        metrics.pages += 1

        # Sum different violation levels for this page
        for violation in this_dir_loaded_results["violations"]:
            impact = violation["impact"]
            metric_storage_target = f"{impact}_violations"
            current_count = getattr(metrics, metric_storage_target)
            setattr(
                metrics,
                metric_storage_target,
                current_count
                + len(
                    violation["nodes"],
                ),
            )

        # Calc page word metrics
        url = this_dir_loaded_results["url"]
        if metrics.word_metrics is not None:
            metrics.word_metrics[url] = _process_page_words(url)

    return metrics


def process_axe_evaluations_and_extras(
    axe_results_dir: Union[str, Path],
    generate_extras: bool = False,
) -> CompiledMetrics:
    """
    Process all aXe evaluations and generate extra features
    (words, ease of reading, etc.) for the provided aXe result tree.
    Extras are optional to generate.

    Parameters
    ----------
    axe_results_dir: Union[str, Path]
        The directory for a specific website that has been processed using the access
        eval scraper.
    generate_extras: bool
        Should the extra features be generated?
        Default: False (do not generate extra features)

    Returns
    -------
    metrics: CompiledMetrics
        The counts of all violation levels summed for the whole axe results tree
        (and optional extra features).
    """
    # Handle path and dir checking
    axe_results_dir = Path(axe_results_dir).resolve(strict=True)
    if not axe_results_dir.is_dir():
        raise NotADirectoryError(axe_results_dir)

    # Prep for recursive processing
    word_metrics: Optional[Dict]
    if generate_extras:
        word_metrics = {}
    else:
        word_metrics = None

    # Process
    parsed_metrics = _recurse_axe_results(
        axe_results_dir, RunningMetrics(word_metrics=word_metrics)
    )

    # Any post-processing of metrics to get to compiled state
    words = 0
    unique_words: Set[str] = set()
    reading_measures = []
    if parsed_metrics.word_metrics is not None:
        for page_metrics in parsed_metrics.word_metrics.values():
            if page_metrics is not None:
                words += page_metrics.words
                # Union equal (set addition)
                unique_words |= page_metrics.unique_words
                reading_measures.append(page_metrics.ease_of_reading)

    # Handle div zero for mean reading measure
    if len(reading_measures) == 0:
        ease_of_reading = 0.0
    else:
        ease_of_reading = sum(reading_measures) / len(reading_measures)

    # Compile error types
    agg_error_results = pd.read_csv(axe_results_dir / AGGREGATE_AXE_RESULTS_FILENAME)
    error_types = {}
    for _, row in agg_error_results[
        ["id", "number_of_elements_in_violation"]
    ].iterrows():
        error_types[row.id] = row.number_of_elements_in_violation

    return CompiledMetrics(
        pages=parsed_metrics.pages,
        minor_violations=parsed_metrics.minor_violations,
        moderate_violations=parsed_metrics.moderate_violations,
        serious_violations=parsed_metrics.serious_violations,
        critical_violations=parsed_metrics.critical_violations,
        number_of_words=words,
        number_of_unique_words=len(unique_words),
        ease_of_reading=ease_of_reading,
        error_types=error_types,
    )


def _convert_metrics_to_expanded_data(
    metrics: CompiledMetrics,
    phase: str,
) -> Dict[str, int]:
    # Unpack error types
    if metrics.error_types is not None:
        error_types = {
            f"error-type_{k}_{phase}": v for k, v in metrics.error_types.items()
        }
    else:
        error_types = {}

    return {
        **error_types,
        f"number_of_pages_{phase}": metrics.pages,
        f"number_of_total_errors_{phase}": (
            metrics.critical_violations
            + metrics.serious_violations
            + metrics.moderate_violations
            + metrics.minor_violations
        ),
        f"number_of_critical_errors_{phase}": metrics.critical_violations,
        f"number_of_serious_errors_{phase}": metrics.serious_violations,
        f"number_of_moderate_errors_{phase}": metrics.moderate_violations,
        f"number_of_minor_errors_{phase}": metrics.minor_violations,
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
        The original election data, the summed violation counts for both pre and post
        contact, and the scraped text features using the post-contact aXe URLs
        for each campaign website combined into a single dataframe.

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
    for _, row in tqdm(election_data.iterrows()):
        cleaned_url = clean_url(row[DatasetFields.campaign_website_url])
        pre_access_eval = pre_contact_axe_scraping_results / cleaned_url
        post_access_eval = post_contact_axe_scraping_results / cleaned_url

        # Only continue with the addition if pre and post both exist
        if pre_access_eval.exists() and post_access_eval.exists():
            # Run metric generation
            pre_access_eval_metrics = process_axe_evaluations_and_extras(
                pre_access_eval,
                generate_extras=False,
            )
            post_access_eval_metrics = process_axe_evaluations_and_extras(
                post_access_eval,
                generate_extras=True,
            )

            # Combine and merge to expanded data
            expanded_data.append(
                {
                    # Original row details
                    **row,
                    # Pre-contact info
                    **_convert_metrics_to_expanded_data(
                        pre_access_eval_metrics,
                        "pre",
                    ),
                    # Post-contact info
                    **_convert_metrics_to_expanded_data(
                        post_access_eval_metrics,
                        "post",
                    ),
                    # Extra features only apply for post-contact
                    DatasetFields.number_of_words: post_access_eval_metrics.number_of_words,  # noqa: E501
                    DatasetFields.number_of_unique_words: post_access_eval_metrics.number_of_unique_words,  # noqa: E501
                    DatasetFields.ease_of_reading: post_access_eval_metrics.ease_of_reading,  # noqa: E501
                }
            )

    log.info(
        f"Dropped {len(election_data) - len(expanded_data)} rows from dataset "
        f"because they were missing a pre or post aXe result directory."
    )
    return pd.DataFrame(expanded_data)


def load_access_eval_2021_dataset(
    path: Optional[Union[str, Path]] = None
) -> pd.DataFrame:
    """
    Load the default access eval 2021 dataset or a provided custom dataset
    and add all computed fields.

    Parameters
    ----------
    path: Optional[Union[str, Path]]
        An optional path for custom data to load.
        Default: None (load official 2021 access eval dataset)

    Returns
    -------
    data: pd.DataFrame
        The loaded dataframe object with all extra computed fields added.
    """

    if path is None:
        path = ACCESS_EVAL_2021_DATASET

    # Load base data
    data = pd.read_csv(ACCESS_EVAL_2021_DATASET)

    # Add computed fields
    for attr in ComputedFields.__dict__.values():
        if isinstance(attr, ComputedField):
            data[attr.name] = attr.func(data)

    # Collect error type cols with a value above 0 at the 25th percentile
    common_error_cols = []
    for col in data.columns:
        if "error-type_" in col and data[col].quantile(0.75) > 0:
            common_error_cols.append(col)

    # Create norm cols
    for common_error_col in common_error_cols:
        error_type = common_error_col.replace("_pre", "").replace("_post", "")
        if "_pre" in common_error_col:
            avg_error_type_col_name = f"avg_{error_type}_per_page_pre"
            norm_col = DatasetFields.number_of_pages_pre
        else:
            avg_error_type_col_name = f"avg_{error_type}_per_page_post"
            norm_col = DatasetFields.number_of_pages_post

        # Norm
        data[avg_error_type_col_name] = data[common_error_col] / data[norm_col]

    return data


def flatten_access_eval_2021_dataset(
    data: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Flatten the access eval 2021 dataset by adding a new column called "Trial"
    which stores a categorical value for "Pre" or "Post" which allows us
    to simplify the columns into just "avg_errors_per_page" for example instead
    of having both "avg_errors_per_page_pre" and "avg_errors_per_page_post".

    Parameters
    ----------
    data: pd.DataFrame
        Preloaded access eval data.
        Default: None (load access eval 2021 data)

    Returns
    -------
    flattened: pd.DataFrame
        The flattened dataset.

    Notes
    -----
    This only provides a subset of the full dataset back.
    Notably dropping the "diff" computed fields.
    """
    # Load default data
    if data is None:
        data = load_access_eval_2021_dataset()

    # Drop general columns
    data = data.drop(
        [
            ComputedFields.diff_pages.name,
            ComputedFields.diff_errors.name,
            ComputedFields.diff_minor_errors.name,
            ComputedFields.diff_moderate_errors.name,
            ComputedFields.diff_serious_errors.name,
            ComputedFields.diff_critical_errors.name,
        ],
        axis=1,
    )

    # Get a list of the column names with pre and post in them
    # (just for pre, we will use string edit to swap to post)
    cols_pre = [col for col in data.columns if "_pre" in col]
    cols_post = [col.replace("_pre", "_post") for col in cols_pre]

    # Get all data for pre and post
    # For pre, this means, take all columns _except_ post columns
    # For post, this means, take all columns _except_ pre columns
    pre = data[[col for col in data.columns if col not in cols_post]]
    post = data[[col for col in data.columns if col not in cols_pre]]

    # Drop the pre and post from the column names for the error data
    pre = pre.rename(columns={col: col.replace("_pre", "") for col in pre.columns})
    post = post.rename(columns={col: col.replace("_post", "") for col in post.columns})

    # Add the tag for pre and post
    pre[DatasetFields.trial] = "A - Pre"
    post[DatasetFields.trial] = "B - Post"

    return pd.concat([pre, post], ignore_index=True)


def get_statistical_difference_crucial_stats(
    data: Optional[pd.DataFrame] = None,
) -> Dict[str, Union[sci_stats.stats.Ttest_indResult, Any]]:
    """
    aasdasd
    """
    # Load default data
    if data is None:
        data = flatten_access_eval_2021_dataset()

    # Store all stats in dict to be returned
    stats: Dict[str, sci_stats.stats.Ttest_indResult] = {}

    # Get trends in mayoral vs council races
    # Have to use Welch t-test here because we don't know / can't be certain
    # of variance between samples
    mayoral_races = data[data[DatasetFields.electoral_position] == "Mayor"]
    council_races = data[data[DatasetFields.electoral_position] == "Council"]
    stats["mayoral vs council | df"] = len(mayoral_races) + len(council_races) - 2

    # Shorten number of pages col title
    number_of_pages = DatasetFields.number_of_pages_post.replace("_post", "")

    # Compute stats and save
    stats["mayoral vs council | number of pages"] = sci_stats.ttest_ind(
        mayoral_races[number_of_pages],
        council_races[number_of_pages],
        equal_var=False,
    )
    stats["mayoral vs council | number of words"] = sci_stats.ttest_ind(
        mayoral_races[DatasetFields.number_of_words],
        council_races[DatasetFields.number_of_words],
        equal_var=False,
    )
    stats["mayoral vs council | number of unique words"] = sci_stats.ttest_ind(
        mayoral_races[DatasetFields.number_of_unique_words],
        council_races[DatasetFields.number_of_unique_words],
        equal_var=False,
    )

    # Get avg percent of errors severities
    avg_errors = data[
        ComputedFields.avg_errors_per_page_post.name.replace("_post", "")
    ].mean()
    avg_minor_errors = data[
        ComputedFields.avg_minor_errors_per_page_post.name.replace("_post", "")
    ].mean()
    avg_moderate_errors = data[
        ComputedFields.avg_moderate_errors_per_page_post.name.replace("_post", "")
    ].mean()
    avg_serious_errors = data[
        ComputedFields.avg_serious_errors_per_page_post.name.replace("_post", "")
    ].mean()
    avg_critical_errors = data[
        ComputedFields.avg_critical_errors_per_page_post.name.replace("_post", "")
    ].mean()
    stats["percent minor errors of total"] = avg_minor_errors / avg_errors
    stats["percent moderate errors of total"] = avg_moderate_errors / avg_errors
    stats["percent serious errors of total"] = avg_serious_errors / avg_errors
    stats["percent critical errors of total"] = avg_critical_errors / avg_errors

    # Get majority of ease of reading
    stats["majority ease of reading"] = data[DatasetFields.ease_of_reading].quantile(
        [0.25, 0.75]
    )

    # Rank error types
    avg_error_type_cols = [col for col in data.columns if "avg_error-type" in col]
    err_type_averages: Dict[str, float] = {}
    for col in avg_error_type_cols:
        err_type_averages[col] = data[col].mean()
    stats["ordered most common error types"] = dict(
        sorted(
            err_type_averages.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )

    # Get trends for election outcome
    winning_races = data[data[DatasetFields.election_result] == "Won"]
    losing_races = data[data[DatasetFields.election_result] == "Lost"]
    stats["win vs lose | number of pages"] = sci_stats.ttest_ind(
        winning_races[number_of_pages],
        losing_races[number_of_pages],
        equal_var=False,
    )
    stats["win vs lose | ease of reading"] = sci_stats.ttest_ind(
        winning_races[DatasetFields.ease_of_reading],
        losing_races[DatasetFields.ease_of_reading],
        equal_var=False,
    )
    stats["win vs lose | number of words"] = sci_stats.ttest_ind(
        winning_races[DatasetFields.number_of_words],
        losing_races[DatasetFields.number_of_words],
        equal_var=False,
    )
    stats["win vs lose | number of unique words"] = sci_stats.ttest_ind(
        winning_races[DatasetFields.number_of_unique_words],
        losing_races[DatasetFields.number_of_unique_words],
        equal_var=False,
    )
    stats[
        "win vs lose | number of avg errors per page -- t-test"
    ] = sci_stats.ttest_ind(
        winning_races[
            ComputedFields.avg_errors_per_page_post.name.replace("_post", "")
        ],
        losing_races[ComputedFields.avg_errors_per_page_post.name.replace("_post", "")],
        equal_var=False,
    )
    stats["win vs lose | number of avg errors per page -- anova"] = sci_stats.f_oneway(
        winning_races[
            ComputedFields.avg_errors_per_page_post.name.replace("_post", "")
        ],
        losing_races[ComputedFields.avg_errors_per_page_post.name.replace("_post", "")],
    )
    stats["winning vs losing | df"] = len(winning_races) + len(losing_races) - 2
    stats["n winning campaigns"] = len(winning_races)

    return stats
