#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

import numpy as np
import pandas as pd
from dataclasses_json import dataclass_json
from scipy import stats as sci_stats
# from selenium import webdriver
# from selenium.common.exceptions import WebDriverException
# from selenium.webdriver import FirefoxOptions
from textstat import flesch_reading_ease
from tqdm import tqdm

from ..constants import SINGLE_PAGE_AXE_RESULTS_FILENAME
from ..utils import clean_url
from .constants_2022_axe_score import (
    ACCESS_EVAL_2022_DATASET,
    ComputedField,
    ComputedFields,
    DatasetFields,
)

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


###############################################################################

def process_axe_evaluations_and_extras(
    axe_results_dir: Union[str, Path],
) -> float:
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
    
    # Get this dirs result file
    this_dir_results = axe_results_dir / SINGLE_PAGE_AXE_RESULTS_FILENAME
    if this_dir_results.exists():
        with open(this_dir_results, "r") as open_f:
            this_dir_loaded_results = json.load(open_f)

        # create dict that contains all info
        needed = ["incomplete", "passes", "violations"]
        data_dict = {"incomplete": {}, "passes": {}, "violations": {}}
        for key in this_dir_loaded_results.keys(): # incomplete, passes, violations
            if key in needed:
                for i in range(0,len(this_dir_loaded_results[key])):
                    test_id = this_dir_loaded_results[key][i]['id']
                    occurance = len(this_dir_loaded_results[key][i]['nodes'])
                    data_dict[key][test_id] = occurance
        # get the weight (1/size)
        unique_keys = set()
        for d in data_dict.values():
            unique_keys.update(d.keys())
        weight = 1/len(unique_keys)
        # get the score
        sum = 0
        for key in data_dict['violations']:
            total = data_dict['incomplete'].get(key, 0) + data_dict['passes'].get(key, 0) + data_dict['violations'].get(key, 0)
            ratio = data_dict['violations'].get(key, 0) / total if total != 0 else 0
            # print(f"Key: {key} Total: {total} Ratio: {ratio}")
            sum = (ratio * weight) + sum
        result = (1-sum)*100

    else:
        result = None

    return result


def _convert_metrics_to_expanded_data(
    result: float,
) -> Dict[str, float]:
    # Unpack error types
    # if metrics.error_types is not None:
    #     track_types = {
    #         f"track-type_{k}": v for k, v in metrics.error_types.items()
    #     }
    # else:
    #     track_types = {}

    return {
        # **track_types,
        # f"number_of_pages": metrics.pages,
        f"axe-score": result,
    }


def combine_election_data_with_axe_results(
    election_data: Union[str, Path, pd.DataFrame],
    axe_scraping_results: Union[str, Path],
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
    axe_scraping_results = Path(axe_scraping_results).resolve(
        strict=True
    )

    if isinstance(election_data, (str, Path)):
        election_data = Path(election_data).resolve(strict=True)
        election_data = pd.read_csv(election_data)

    # Confirm axe scraping results is dir
    if not axe_scraping_results.is_dir():
        raise NotADirectoryError(axe_scraping_results)

    # Iter election data and create List of expanded dicts with added
    expanded_data = []
    for _, row in tqdm(election_data.iterrows()):
        if isinstance(row[DatasetFields.campaign_website_url], str):
            cleaned_url = clean_url(row[DatasetFields.campaign_website_url])
            access_eval = axe_scraping_results / cleaned_url
        else:
            access_eval = None

        # post_access_eval = post_contact_axe_scraping_results / cleaned_url

        # Only continue with the addition if pre and post both exist
        # if not access_eval == None:
        if access_eval != None and access_eval.exists():
            # Run metric generation
            axe_score = process_axe_evaluations_and_extras(
                access_eval,
            )

            # Combine and merge to expanded data
            expanded_data.append(
                {
                    # Original row details
                    **row,
                    # axe-report
                    **_convert_metrics_to_expanded_data(
                        axe_score,
                    ),
                }
            )
        else:
            row.campaign_website_url = None
            expanded_data.append(
                {
                    # Original row details with unworking links removed
                    **row,
                }
            )

    log.info(
        f"Dropped {len(election_data) - len(expanded_data)} rows from dataset "
        f"because they were missing a result directory."
    )
    return pd.DataFrame(expanded_data)


def load_access_eval_2022_dataset(
    path: Optional[Union[str, Path]] = None
) -> pd.DataFrame:
    """
    Load the default access eval 2022 dataset or a provided custom dataset
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
        path = ACCESS_EVAL_2022_DATASET

    # Load base data
    data = pd.read_csv(ACCESS_EVAL_2022_DATASET)

    # Add computed fields
    for attr in ComputedFields.__dict__.values():
        if isinstance(attr, ComputedField):
            data[attr.name] = attr.func(data)
    
    # Replace the NaN with 0 
    for col in data.columns:
        if "error-type_" in col:
            data[col] = data[col].fillna(0)

    # Collect error type cols with a value above 0 at the 25th percentile
    common_error_cols = []
    for col in data.columns:
        if "error-type_" in col and data[col].quantile(0.75) > 0:
            common_error_cols.append(col)

    # Create norm cols
    for common_error_col in common_error_cols:
        error_type = common_error_col
        avg_error_type_col_name = f"avg_{error_type}_per_page"
        norm_col = DatasetFields.number_of_pages
        # if "_pre" in common_error_col:
        #     avg_error_type_col_name = f"avg_{error_type}_per_page_pre"
        #     norm_col = DatasetFields.number_of_pages_pre
        # else:
        #     avg_error_type_col_name = f"avg_{error_type}_per_page_post"
        #     norm_col = DatasetFields.number_of_pages_post

        # Norm
        data[avg_error_type_col_name] = data[common_error_col] / data[norm_col]

    return data

def get_crucial_stats(
    data: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Generate statistics we found useful in the 2021 paper.

    This includes:
    * mayoral vs council campaigns by content features.
    * percent of total errors per each error severity level
    * majority of ease of reading range
    * ordered most common error types
    * winning vs losing campaigns by content features
    * winning vs losing campaigns by average errors by page
    """
    # Load default data
    if data is None:
        data = load_access_eval_2022_dataset()

    # Create standard column name for long format table
    # avg_errs_per_page_col = ComputedFields.avg_errors_per_page.name
    # avg_minor_errs_per_page_col = (
    #     ComputedFields.avg_minor_errors_per_page.name
    # )
    # avg_moderate_errs_per_page_col = (
    #     ComputedFields.avg_moderate_errors_per_page.name
    # )
    # avg_serious_errs_per_page_col = (
    #     ComputedFields.avg_serious_errors_per_page.name
    # )
    # avg_critical_errs_per_page_col = (
    #     ComputedFields.avg_critical_errors_per_page.name
    # )
    # num_pages_col = DatasetFields.number_of_pages

    # # Generate demographics and tables
    # with open("overall-stats.txt", "w") as open_f:
    #     open_f.write(
    #         data[[ num_pages_col, avg_errs_per_page_col]]
    #         .agg([np.mean, np.std])
    #         .to_latex()
    #     )

    #####
    # Important:
    # At this point we subset the data to just "post" or trial "b"
    #####
    # data = data.loc[data[DatasetFields.trial] == "B - Post"]
    print("Number of sites for this run:", len(data))
    # print(
    #     "Number of sites contacted:",
    #     len(data.loc[data[DatasetFields.contacted] == "Contacted"]),
    # )
    # print(
    #     "Number of Attorney General campaigns:",
    #     len(data.loc[data[DatasetFields.electoral_position] == "Attorney General"]),
    # )
    # print(
    #     "Number of Governor campaigns:",
    #     len(data.loc[data[DatasetFields.electoral_position] == "Governor"]),
    # )
    # print(
    #     "Number of Mayor campaigns:",
    #     len(data.loc[data[DatasetFields.electoral_position] == "Mayor"]),
    # )
    # print(
    #     "Number of House campaigns:",
    #     len(data.loc[data[DatasetFields.electoral_position] == "House"]),
    # )
    # print(
    #     "Number of council campaigns:",
    #     len(data.loc[data[DatasetFields.electoral_position] == "Council"]),
    # )
    # print(
    #     "Number of open campaigns:",
    #     len(data.loc[data[DatasetFields.candidate_position] == "Open"]),
    # )
    # print(
    #     "Number of incumbent campaigns:",
    #     len(data.loc[data[DatasetFields.candidate_position] == "Incumbent"]),
    # )
    # print(
    #     "Number of challenger campaigns:",
    #     len(data.loc[data[DatasetFields.candidate_position] == "Challenger"]),
    # )
    print(
        "Number of State campaigns:",
        len(data.loc[data[DatasetFields.electoral_level] == "State"]),
    )
    print(
        "Number of City campaigns:",
        len(data.loc[data[DatasetFields.electoral_level] == "City"]),
    )
    print(
        "Number of County campaigns:",
        len(data.loc[data[DatasetFields.electoral_level] == "County"]),
    )
    print(
        "Number of Federal campaigns:",
        len(data.loc[data[DatasetFields.electoral_level] == "Federal"]),
    )
    print(
        "Number of Judicial campaigns:",
        len(data.loc[data[DatasetFields.electoral_branch] == "Judicial"]),
    )
    print(
        "Number of Executive campaigns:",
        len(data.loc[data[DatasetFields.electoral_branch] == "Executive"]),
    )
    print(
        "Number of Legislative campaigns:",
        len(data.loc[data[DatasetFields.electoral_branch] == "Legislative"]),
    )

    # Generate election outcome by location and position
    with open("demographics.txt", "w") as open_f:
        open_f.write(
            data.groupby(
                [
                    DatasetFields.location,
                    DatasetFields.electoral_branch,
                    DatasetFields.electoral_level,
                    # DatasetFields.candidate_position,
                ]
            )
            .size()
            .to_latex()
        )

    # Store all stats in dict to be returned
    # stats: Dict[str, sci_stats.stats.Ttest_indResult] = {
    #     "contacted pre and post | avg errors per page": contacted_t_test,
    #     "not contacted pre and post | avg errors per page": not_contacted_t_test,
    # }

    # Get trends in mayoral vs council races
    # Have to use Welch t-test here because we don't know / can't be certain
    # of variance between samples
    # change back when doing othe race:
    # attorney_general_races = data[data[DatasetFields.electoral_position] == "Attorney General"]
    # governor_races = data[data[DatasetFields.electoral_position] == "Governor"]
    # mayoral_races = data[data[DatasetFields.electoral_position] == "Mayor"]'
    # house_races = data[data[DatasetFields.electoral_position] == "House"]

    # council_races = data[data[DatasetFields.electoral_position] == "Council"]

    # Shorten number of pages col title
    # number_of_pages = DatasetFields.number_of_pages

    # Compute stats and save
    # stats: Dict[str, sci_stats.stats.Ttest_indResult] = {
    #     "mayoral vs council | number of pages": sci_stats.ttest_ind(
    #     mayoral_races[number_of_pages],
    #     council_races[number_of_pages],
    #     equal_var=False,)
    # }
    # stats["mayoral vs council | number of pages"] = sci_stats.ttest_ind(
    #     mayoral_races[number_of_pages],
    #     council_races[number_of_pages],
    #     equal_var=False,
    # )
    # stats: Dict[str, sci_stats.stats.Ttest_indResult] = {
    #     "attorney general | number of pages | mean and std":
    #     {"mean": attorney_general_races[number_of_pages].mean(),
    #     "std": attorney_general_races[number_of_pages].std(),}
    # }
    stats: Dict[str, sci_stats.stats.Ttest_indResult] = {
        "read | total-b | mean and std":
        {"mean": data[DatasetFields.axe_score].mean(),
        "std": data[DatasetFields.axe_score].std(),}
    }
    # stats["z | total-b | mean and std"] = {
    #     "mean": data[DatasetFields.z_score].mean(),
    #     "std": data[DatasetFields.z_score].std(),}
    # stats["mayoral | number of pages | mean and std"] = {
    #     "mean": mayoral_races[number_of_pages].mean(),
    #     "std": mayoral_races[number_of_pages].std(),
    # }
    # stats["council | number of pages | mean and std"] = {
    #     "mean": council_races[number_of_pages].mean(),
    #     "std": council_races[number_of_pages].std(),
    # }
    # data_pages = data[number_of_pages]
    # data_words = data[DatasetFields.number_of_words]
    # data_uwords = data[DatasetFields.number_of_unique_words]
    # no_na_pages = data_pages[~np.isnan(data_pages)]
    # no_na_words = data_words[~np.isnan(data_words)]
    # no_na_uwords = data_uwords[~np.isnan(data_uwords)]
    # number of pages and number of words correlation
    # stats["vote_share | axe_core | corr"] = sci_stats.pearsonr(
    #     data[DatasetFields.vote_share],
    #     data[DatasetFields.axe_score],
    # )
    # stats["number of pages | number of unique words | corr"] = sci_stats.pearsonr(
    #     data[number_of_pages],
    #     data[DatasetFields.number_of_unique_words],
    # )

    # number of words mayor vs council
    # stats["mayoral vs council | number of words"] = sci_stats.ttest_ind(
    #     mayoral_races[DatasetFields.number_of_words],
    #     council_races[DatasetFields.number_of_words],
    #     equal_var=False,
    # )
    # stats["attorney general | number of words | mean and std"] = {
    #     "mean": attorney_general_races[DatasetFields.number_of_words].mean(),
    #     "std": attorney_general_races[DatasetFields.number_of_words].std(),
    # }
    # stats["house | number of words | mean and std"] = {
    #     "mean": house_races[DatasetFields.number_of_words].mean(),
    #     "std": house_races[DatasetFields.number_of_words].std(),
    # }
    # stats["council | number of words | mean and std"] = {
    #     "mean": council_races[DatasetFields.number_of_words].mean(),
    #     "std": council_races[DatasetFields.number_of_words].std(),
    # }

    # number of unique words mayor vs council
    # stats["mayoral vs council | number of unique words"] = sci_stats.ttest_ind(
    #     mayoral_races[DatasetFields.number_of_unique_words],
    #     council_races[DatasetFields.number_of_unique_words],
    #     equal_var=False,
    # )
    # stats["attorney general | number of unique words | mean and std"] = {
    #     "mean": attorney_general_races[DatasetFields.number_of_unique_words].mean(),
    #     "std": attorney_general_races[DatasetFields.number_of_unique_words].std(),
    # }
    # stats["house | number of unique words | mean and std"] = {
    #     "mean": house_races[DatasetFields.number_of_unique_words].mean(),
    #     "std": house_races[DatasetFields.number_of_unique_words].std(),
    # }
    # stats["council | number of unique words | mean and std"] = {
    #     "mean": council_races[DatasetFields.number_of_unique_words].mean(),
    #     "std": council_races[DatasetFields.number_of_unique_words].std(),
    # }

    # number of pages, number of words, number of unique words by candidate position
    # candidate_position_grouped = data.groupby(DatasetFields.candidate_position)
    # candidate_position_split = [
    #     candidate_position_grouped.get_group(g)
    #     for g in candidate_position_grouped.groups.keys()
    # ]
    # candidate_position_split_n_pages = [
    #     df[num_pages_col] for df in candidate_position_split
    # ]
    # stats["n pages | candidate position"] = sci_stats.f_oneway(
    #     *candidate_position_split_n_pages
    # )
    # candidate_position_split_n_words = [
    #     df[DatasetFields.number_of_words] for df in candidate_position_split
    # ]
    # stats["n words | candidate position"] = sci_stats.f_oneway(
    #     *candidate_position_split_n_words
    # )
    # candidate_position_split_n_unique_words = [
    #     df[DatasetFields.number_of_unique_words] for df in candidate_position_split
    # ]
    # stats["n unique words | candidate position"] = sci_stats.f_oneway(
    #     *candidate_position_split_n_unique_words
    # )

    def sig_str(p: float) -> str:
        if p >= 0.05:
            return "n.s."
        if p >= 0.01:
            return "p<.05 *"
        if p >= 0.005:
            return "p<.01 **"
        if p >= 0.001:
            return "p<.005 ***"
        return "p<.001 ***"

    # Average errors per page by candidate position
    # electoral position and election outcome
    # err_severity_table_gen: Dict[str, Dict[str, str]] = {}
    # for err_col in [
    #     avg_errs_per_page_col,
    #     avg_minor_errs_per_page_col,
    #     avg_moderate_errs_per_page_col,
    #     avg_serious_errs_per_page_col,
    #     avg_critical_errs_per_page_col,
    # ]:
    #     this_measure_stats: Dict[str, str] = {}

    #     # # Handle candidate position
    #     # cp_err_col = [df[err_col] for df in candidate_position_split]
    #     # anova = sci_stats.f_oneway(*cp_err_col)

    #     # this_measure_stats[
    #     #     DatasetFields.candidate_position
    #     # ] = f"F(2, 57) = {round(anova.statistic, 2)}, {sig_str(anova.pvalue)}"
    #     # Handle t-tests add electoral_position after contact the dataframes
    #     for group_col in [
    #         DatasetFields.election_result,
    #         # DatasetFields.electoral_position,
    #     ]:
    #         subset_group = data.groupby(group_col)
    #         subset_split = [
    #             subset_group.get_group(g) for g in subset_group.groups.keys()
    #         ]
    #         subset_split_err_col = [df[err_col] for df in subset_split]
    #         t_result = sci_stats.ttest_ind(
    #             *subset_split_err_col,
    #             equal_var=False,
    #         )
    #         this_measure_stats[
    #             group_col
    #         ] = f"t(58) = {round(t_result.statistic, 2)}, {sig_str(t_result.pvalue)}"

    #     # Attach this measure stats to table data
    #     err_severity_table_gen[err_col] = this_measure_stats

    # # Convert table gen to table
    # with open("err-severity-stats.txt", "w") as open_f:
    #     open_f.write(pd.DataFrame(err_severity_table_gen).T.to_latex())

    # # Get avg percent of errors severities
    # avg_errors = data[avg_errs_per_page_col].mean()
    # avg_minor_errors = data[avg_minor_errs_per_page_col].mean()
    # avg_moderate_errors = data[avg_moderate_errs_per_page_col].mean()
    # avg_serious_errors = data[avg_serious_errs_per_page_col].mean()
    # avg_critical_errors = data[avg_critical_errs_per_page_col].mean()
    # stats["percent minor errors of total"] = avg_minor_errors / avg_errors
    # stats["percent moderate errors of total"] = avg_moderate_errors / avg_errors
    # stats["percent serious errors of total"] = avg_serious_errors / avg_errors
    # stats["percent critical errors of total"] = avg_critical_errors / avg_errors

    # Get majority of ease of reading
    # stats["axe"] = data[DatasetFields.number_of_total_trackers].quantile(
    #     [0.25, 0.5, 0.75]
    # )
    # stats["z"] = data[DatasetFields.z_score].quantile(
    #     [0.25, 0.5, 0.75]
    # )
    stats["ease of reading"] = data[DatasetFields.axe_score].quantile(
        [0.25, 0.5, 0.75]
    )
    # stats["number_of_total_trackers"] = data[DatasetFields.number_of_total_trackers].quantile(
    #     [0.25, 0.5, 0.75]
    # )
    # stats["behaviour_event_listeners"] = data[DatasetFields.behaviour_event_listeners].quantile(
    #     [0.25, 0.5, 0.75]
    # )
    # stats["canvas_fingerprinters"] = data[DatasetFields.canvas_fingerprinters].quantile(
    #     [0.25, 0.5, 0.75]
    # )
    # stats["canvas_font_fingerprinters"] = data[DatasetFields.canvas_font_fingerprinters].quantile(
    #     [0.25, 0.5, 0.75]
    # )
    # stats["cookies"] = data[DatasetFields.cookies].quantile(
    #     [0.25, 0.5, 0.75]
    # )
    # stats["fb_pixel_events"] = data[DatasetFields.fb_pixel_events].quantile(
    #     [0.25, 0.5, 0.75]
        
    # )
    # stats["key_logging"] = data[DatasetFields.key_logging].quantile(
    #     [0.25, 0.5, 0.75]
    # )
    # stats["session_recorders"] = data[DatasetFields.session_recorders].quantile(
    #     [0.25, 0.5, 0.75]
    # )
    # stats["third_party_trackers"] = data[DatasetFields.third_party_trackers].quantile(
    #     [0.25, 0.5, 0.75]
        
    # )
    # stats["ease of reading | mean and std"] = {
    #     "mean": data[DatasetFields.ease_of_reading].mean(),
    #     "std": data[DatasetFields.ease_of_reading].std(),
    # }

    # Rank error types
    # avg_error_type_cols = [col for col in data.columns if "avg_error-type" in col]
    # err_type_averages: Dict[str, Dict[str, float]] = {}
    # for col in avg_error_type_cols:
    #     err_type_averages[col] = {
    #         "mean": data[col].mean(),
    #         "std": data[col].std(),
    #     }
    # err_type_averages_df = (
    #     pd.DataFrame(err_type_averages)
    #     .sort_values(by="mean", axis=1, ascending=False)
    #     .round(3)
    # )
    # with open("err-types-stats.txt", "w") as open_f:
    #     open_f.write(err_type_averages_df.T.to_latex())

    # Get trends for election outcome
    # winning_races = data[data[DatasetFields.election_result] == "Won"]
    # losing_races = data[data[DatasetFields.election_result] == "Lost"]
    # stats["win vs lose | axe-score"] = sci_stats.ttest_ind(
    #     winning_races[DatasetFields.axe_score],
    #     losing_races[DatasetFields.axe_score],
    #     equal_var=False,
    # )
    # stats["win vs lose | ease of reading"] = sci_stats.ttest_ind(
    #     winning_races[DatasetFields.ease_of_reading],
    #     losing_races[DatasetFields.ease_of_reading],
    #     equal_var=False,
    # )
    # stats["win vs lose | number of words"] = sci_stats.ttest_ind(
    #     winning_races[DatasetFields.number_of_words],
    #     losing_races[DatasetFields.number_of_words],
    #     equal_var=False,
    # )
    # stats["win vs lose | number of unique words"] = sci_stats.ttest_ind(
    #     winning_races[DatasetFields.number_of_unique_words],
    #     losing_races[DatasetFields.number_of_unique_words],
    #     equal_var=False,
    # )
    # Clean stats
    for k, v in stats.items():
        if isinstance(
            v,
            (
                sci_stats.stats.Ttest_indResult,
                sci_stats.stats.F_onewayResult,
                sci_stats.stats.Ttest_relResult,
            ),
        ):
            stats[k] = {"statistic": v.statistic, "pvalue": v.pvalue}
        elif isinstance(v, pd.Series):
            stats[k] = v.tolist()

    return stats
