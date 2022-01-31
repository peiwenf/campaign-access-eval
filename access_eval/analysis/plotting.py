#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import altair as alt
import pandas as pd

from .constants import ComputedFields, DatasetFields
from .core import flatten_access_eval_2021_dataset, load_access_eval_2021_dataset

###############################################################################

PLOTTING_DIR = Path("plots/").resolve()

###############################################################################


def plot_computed_fields_over_vote_share(
    data: Optional[pd.DataFrame] = None,
    save_path: Optional[Union[str, Path]] = None,
) -> Path:
    # Load default data
    if data is None:
        data = load_access_eval_2021_dataset()

    # Apply default save path
    if save_path is None:
        save_path = PLOTTING_DIR / "vote-share.png"

    # Ensure save path is Path object
    save_path = Path(save_path).resolve()
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate chart
    vote_share = (
        alt.Chart(data)
        .mark_point()
        .encode(
            alt.X(f"{DatasetFields.vote_share}:Q"),
            alt.Y(alt.repeat("column"), type="quantitative"),
            color=f"{DatasetFields.contacted}:N",
            shape=f"{DatasetFields.contacted}:N",
        )
        .repeat(
            column=[
                ComputedFields.diff_errors.name,
                ComputedFields.diff_critical_errors.name,
                ComputedFields.diff_serious_errors.name,
                ComputedFields.diff_moderate_errors.name,
                ComputedFields.diff_minor_errors.name,
                ComputedFields.avg_errors_per_page_pre.name,
                ComputedFields.avg_errors_per_page_post.name,
                ComputedFields.avg_critical_errors_per_page_pre.name,
                ComputedFields.avg_critical_errors_per_page_post.name,
                ComputedFields.avg_serious_errors_per_page_pre.name,
                ComputedFields.avg_serious_errors_per_page_post.name,
                ComputedFields.avg_moderate_errors_per_page_pre.name,
                ComputedFields.avg_moderate_errors_per_page_post.name,
                ComputedFields.avg_minor_errors_per_page_pre.name,
                ComputedFields.avg_minor_errors_per_page_post.name,
            ],
        )
    )

    vote_share.save(str(save_path.resolve()))
    return save_path


def plot_pre_post_fields_compare(
    data: Optional[pd.DataFrame] = None,
    save_path: Optional[Union[str, Path]] = None,
) -> Path:
    # Load default data
    if data is None:
        data = load_access_eval_2021_dataset()

    # Apply default save path
    if save_path is None:
        save_path = PLOTTING_DIR / "pre-post.png"

    # Ensure save path is Path object
    save_path = Path(save_path).resolve()
    save_path.parent.mkdir(parents=True, exist_ok=True)

    pre_post = alt.hconcat()
    for pre, post in [
        (
            ComputedFields.avg_errors_per_page_pre.name,
            ComputedFields.avg_errors_per_page_post.name,
        ),
        (
            ComputedFields.avg_critical_errors_per_page_pre.name,
            ComputedFields.avg_critical_errors_per_page_post.name,
        ),
        (
            ComputedFields.avg_serious_errors_per_page_pre.name,
            ComputedFields.avg_serious_errors_per_page_post.name,
        ),
        (
            ComputedFields.avg_moderate_errors_per_page_pre.name,
            ComputedFields.avg_moderate_errors_per_page_post.name,
        ),
        (
            ComputedFields.avg_minor_errors_per_page_pre.name,
            ComputedFields.avg_minor_errors_per_page_post.name,
        ),
    ]:
        pre_post |= (
            alt.Chart(data)
            .mark_point()
            .encode(
                x=f"{post}:Q",
                y=f"{pre}:Q",
                color=f"{DatasetFields.contacted}:N",
                shape=f"{DatasetFields.contacted}:N",
            )
        )

    pre_post.save(str(save_path.resolve()))
    return save_path


def plot_categorical_against_errors_boxplots(
    data: Optional[pd.DataFrame] = None,
) -> List[Path]:
    """
    Input data should be the "flattened" dataset.
    """
    # Load default data
    if data is None:
        data = flatten_access_eval_2021_dataset()

    # Only work against the post data for summary stats as there was no difference
    # pre and post (trial / contact)
    data = data[data[DatasetFields.trial] == "B - Post"]

    # Set of categorical variables to use for box plot generation
    categorical_variables = [
        DatasetFields.electoral_position,
        DatasetFields.candidate_position,
        DatasetFields.election_result,
    ]

    # For each categorical variable, create a row of the different error measures
    save_paths = []
    for cat_var in categorical_variables:
        # Break down the categorical variable into all errors and subsets of error type
        error_types = alt.hconcat()
        for err in [
            ComputedFields.avg_errors_per_page_post.name,
            ComputedFields.avg_minor_errors_per_page_post.name,
            ComputedFields.avg_moderate_errors_per_page_post.name,
            ComputedFields.avg_serious_errors_per_page_post.name,
            ComputedFields.avg_critical_errors_per_page_post.name,
        ]:
            feature_name = err.replace("_post", "")
            scale_name = ComputedFields.avg_errors_per_page_post.name.replace(
                "_post", ""
            )

            error_types |= (
                alt.Chart(data)
                .mark_boxplot(ticks=True)
                .encode(
                    y=alt.Y(
                        f"{feature_name}:Q",
                        scale=alt.Scale(
                            domain=(
                                data[scale_name].min(),
                                data[scale_name].max(),
                            ),
                            padding=1,
                        ),
                    ),
                    column=alt.Column(
                        f"{cat_var}:N", spacing=40, header=alt.Header(orient="bottom")
                    ),
                )
            )

        save_path = PLOTTING_DIR / f"{cat_var}-errors-split.png"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        error_types.save(str(save_path))
        save_paths.append(save_path)

    return save_paths


def plot_locations_against_errors_boxplots(
    data: Optional[pd.DataFrame] = None,
) -> Path:
    """
    Input data should be the "flattened" dataset.
    """
    # Load default data
    if data is None:
        data = flatten_access_eval_2021_dataset()

    # Only work against the post data for summary stats as there was no difference
    # pre and post (trial / contact)
    data = data[data[DatasetFields.trial] == "B - Post"]

    # Drop any locations with less than two campaigns
    location_counts = data[DatasetFields.location].value_counts()
    viable_locations = location_counts[location_counts < 2]
    data = data[~data[DatasetFields.location].isin(viable_locations)]

    location_plots = alt.vconcat()
    for location in data[DatasetFields.location].unique():
        location_subset = data.loc[data[DatasetFields.location] == location]

        if len(location_subset) > 4:
            error_types = alt.hconcat()
            for err in [
                ComputedFields.avg_errors_per_page_post.name,
                ComputedFields.avg_minor_errors_per_page_post.name,
                ComputedFields.avg_moderate_errors_per_page_post.name,
                ComputedFields.avg_serious_errors_per_page_post.name,
                ComputedFields.avg_critical_errors_per_page_post.name,
            ]:
                feature_name = err.replace("_post", "")
                scale_name = ComputedFields.avg_errors_per_page_post.name.replace(
                    "_post", ""
                )

                error_types |= (
                    alt.Chart(location_subset)
                    .mark_boxplot(ticks=True)
                    .encode(
                        y=alt.Y(
                            f"{feature_name}:Q",
                            scale=alt.Scale(
                                domain=(
                                    data[scale_name].min(),
                                    data[scale_name].max(),
                                ),
                                padding=1,
                            ),
                        ),
                        column=alt.Column(
                            f"{DatasetFields.candidate_position}:N",
                            spacing=60,
                            header=alt.Header(orient="bottom"),
                        ),
                    )
                )

            location_plots &= error_types

    save_path = PLOTTING_DIR / "location-errors-split.png"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    location_plots.save(str(save_path))

    return save_path


def plot_error_types_boxplots(
    data: Optional[pd.DataFrame] = None,
) -> Path:
    """
    Input data should be the "flattened" dataset.
    """
    # Load default data
    if data is None:
        data = flatten_access_eval_2021_dataset()

    # Only work against the post data for summary stats as there was no difference
    # pre and post (trial / contact)
    data = data[data[DatasetFields.trial] == "B - Post"]

    # Use all pre-computed avg error type features
    common_error_cols = [col for col in data.columns if "avg_error-type_" in col]

    # Create plot
    err_type_plots = alt.vconcat()
    for err_type in common_error_cols:
        cat_var_plot = alt.hconcat()
        for cat_var in [
            DatasetFields.electoral_position,
            DatasetFields.candidate_position,
            DatasetFields.election_result,
        ]:
            cat_var_plot |= (
                alt.Chart(data)
                .mark_boxplot(ticks=True)
                .encode(
                    y=alt.Y(
                        f"{err_type}:Q",
                        scale=alt.Scale(
                            domain=(
                                data[err_type].min(),
                                data[err_type].max(),
                            ),
                            padding=1,
                        ),
                    ),
                    column=alt.Column(
                        f"{cat_var}:N", spacing=60, header=alt.Header(orient="bottom")
                    ),
                )
            )

        err_type_plots &= cat_var_plot

    save_path = PLOTTING_DIR / "error-types-by-category-splits.png"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    err_type_plots.save(str(save_path))

    return save_path


def _plot_and_fig_text(
    data: pd.DataFrame,
    plot_cols: List[str],
    fig_text_prefix: str,
    subset_name: str,
    column: Optional[alt.Column] = None,
    consistent_scale: bool = False,
) -> None:
    if consistent_scale:
        scale_min = min([data[col].min() for col in plot_cols])
        scale_max = max([data[col].max() for col in plot_cols])
        scale = alt.Scale(
            domain=(scale_min, scale_max),
            padding=1,
        )
    else:
        scale = alt.Scale()

    chart = alt.hconcat(spacing=40)
    for col in plot_cols:
        if column is None:
            chart |= (
                alt.Chart(data)
                .mark_boxplot()
                .encode(
                    y=alt.Y(
                        col,
                        scale=scale,
                    )
                )
            )
        else:
            chart |= (
                alt.Chart(data)
                .mark_boxplot()
                .encode(
                    y=alt.Y(
                        col,
                        scale=scale,
                    ),
                    column=column,
                )
            )
        fig_text_prefix += (
            f" {col} "
            f"mean: {round(data[col].mean(), 2)}, "
            f"std: {round(data[col].std(), 2)}, "
            f"min: {round(data[col].min(), 2)}, "
            f"max: {round(data[col].max(), 2)}."
        )
    chart.properties(title="Campaign Website Content")

    # Save fig and text
    fig_save_path = PLOTTING_DIR / f"{subset_name}.png"
    fig_save_path.parent.mkdir(parents=True, exist_ok=True)
    chart.save(str(fig_save_path))
    with open(fig_save_path.with_suffix(".txt"), "w") as open_f:
        open_f.write(fig_text_prefix)


def plot_summary_stats(
    data: Optional[pd.DataFrame] = None,
    subset_name: str = "",
    keep_cols: List[str] = [],
    plot_kwargs: Dict[str, Any] = {},
) -> None:
    """
    Input data should be the "flattened" dataset.
    """
    # Load default data
    if data is None:
        data = flatten_access_eval_2021_dataset()

    # Only work against the post data for summary stats as there was no difference
    # pre and post (trial / contact)
    data = data[data[DatasetFields.trial] == "B - Post"]

    # Split into different commonly grouped stats
    # Content is the actual website content
    content_cols = [
        DatasetFields.number_of_pages_post.replace("_post", ""),
        DatasetFields.ease_of_reading,
        DatasetFields.number_of_words,
        DatasetFields.number_of_unique_words,
    ]

    # Error count norm stats
    error_counts_normed_cols = [
        c.replace("_post", "")
        for c in [
            ComputedFields.avg_errors_per_page_post.name,
            ComputedFields.avg_minor_errors_per_page_post.name,
            ComputedFields.avg_moderate_errors_per_page_post.name,
            ComputedFields.avg_serious_errors_per_page_post.name,
            ComputedFields.avg_critical_errors_per_page_post.name,
        ]
    ]

    # Error types are the actual error value (what was the error)
    error_types_cols = [c for c in data.columns if "avg_error-type_" in c]

    # Create content plots
    _plot_and_fig_text(
        data=data[[*content_cols, *keep_cols]],
        plot_cols=content_cols,
        fig_text_prefix=(
            "Distributions for key content statistics "
            "gathered while scraping campaign websites."
        ),
        subset_name=f"{subset_name}content-stats",
        **plot_kwargs,
    )

    # Create norm stats plots
    _plot_and_fig_text(
        data=data[[*error_counts_normed_cols, *keep_cols]],
        plot_cols=error_counts_normed_cols,
        fig_text_prefix=(
            "Distributions for normalized error severity counts "
            "(counts for each error severity / number of pages) "
            "statistics gathered from scraping campaign websites."
        ),
        subset_name=f"{subset_name}error-severity",
        consistent_scale=True,
        **plot_kwargs,
    )

    # Create error types plots
    _plot_and_fig_text(
        data=data[[*error_types_cols, *keep_cols]],
        plot_cols=error_types_cols,
        fig_text_prefix=(
            "Distributions for normalized error types counts "
            "(counts for each error type / number of pages) "
            "statistics gathered from scraping campaign websites."
        ),
        subset_name=f"{subset_name}error-types",
        consistent_scale=True,
        **plot_kwargs,
    )


def plot_location_based_summary_stats(
    data: Optional[pd.DataFrame] = None,
) -> None:
    """
    Input data should be the "flattened" dataset.
    """
    # Load default data
    if data is None:
        data = flatten_access_eval_2021_dataset()

    # Only work against the post data for summary stats as there was no difference
    # pre and post (trial / contact)
    data = data[data[DatasetFields.trial] == "B - Post"]

    # Drop any locations with less than two campaigns
    location_counts = data[DatasetFields.location].value_counts()
    viable_locations = location_counts[location_counts <= 2].index
    data = data[~data[DatasetFields.location].isin(viable_locations)]

    # Plot basic stats
    plot_summary_stats(
        data,
        subset_name="location-split-",
        keep_cols=[DatasetFields.location],
        plot_kwargs={"column": alt.Column(DatasetFields.location, spacing=60)},
    )


def plot_election_result_based_summary_stats(
    data: Optional[pd.DataFrame] = None,
) -> None:
    """
    Input data should be the "flattened" dataset.
    """
    # Load default data
    if data is None:
        data = flatten_access_eval_2021_dataset()

    # Only work against the post data for summary stats as there was no difference
    # pre and post (trial / contact)
    data = data[data[DatasetFields.trial] == "B - Post"]

    # Plot basic stats
    plot_summary_stats(
        data,
        subset_name="election-result-split-",
        keep_cols=[DatasetFields.election_result],
        plot_kwargs={"column": alt.Column(DatasetFields.election_result, spacing=40)},
    )


def plot_electoral_position_based_summary_stats(
    data: Optional[pd.DataFrame] = None,
) -> None:
    """
    Input data should be the "flattened" dataset.
    """
    # Load default data
    if data is None:
        data = flatten_access_eval_2021_dataset()

    # Only work against the post data for summary stats as there was no difference
    # pre and post (trial / contact)
    data = data[data[DatasetFields.trial] == "B - Post"]

    # Plot basic stats
    plot_summary_stats(
        data,
        subset_name="election-position-split-",
        keep_cols=[DatasetFields.electoral_position],
        plot_kwargs={
            "column": alt.Column(DatasetFields.electoral_position, spacing=40)
        },
    )


def plot_candidate_position_based_summary_stats(
    data: Optional[pd.DataFrame] = None,
) -> None:
    """
    Input data should be the "flattened" dataset.
    """
    # Load default data
    if data is None:
        data = flatten_access_eval_2021_dataset()

    # Only work against the post data for summary stats as there was no difference
    # pre and post (trial / contact)
    data = data[data[DatasetFields.trial] == "B - Post"]

    # Plot basic stats
    plot_summary_stats(
        data,
        subset_name="candidate-position-split-",
        keep_cols=[DatasetFields.candidate_position],
        plot_kwargs={
            "column": alt.Column(DatasetFields.candidate_position, spacing=40)
        },
    )


def plot_pre_post_errors(
    data: Optional[pd.DataFrame] = None,
) -> None:
    """
    Input data should be the "flattened" dataset.
    """
    # Load default data
    if data is None:
        data = flatten_access_eval_2021_dataset()

    # Make pre post chart with split by contacted
    chart = (
        alt.Chart(data)
        .mark_boxplot()
        .encode(
            x=DatasetFields.contacted,
            y=f"{ComputedFields.avg_errors_per_page_post.name.replace('_post', ''):}:Q",
            column=alt.Column(DatasetFields.trial, spacing=30),
            color=DatasetFields.contacted,
        )
    )

    # Save
    PLOTTING_DIR.mkdir(parents=True, exist_ok=True)
    chart.save(str(PLOTTING_DIR / "pre-post-errors.png"))
