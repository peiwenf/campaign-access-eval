#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import List, Optional, Union

import altair as alt
import pandas as pd

from .constants import ComputedFields, DatasetFields
from .core import flatten_access_eval_2021_dataset, load_access_eval_2021_dataset

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
        save_path = Path("vote-share.png")

    # Ensure save path is Path object
    save_path = Path(save_path)

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
        save_path = Path("pre-post.png")

    # Ensure save path is Path object
    save_path = Path(save_path)

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

    # Set of categorical variables to use for box plot generation
    categorical_variables = [
        DatasetFields.electoral_position,
        DatasetFields.candidate_position,
        DatasetFields.candidate_history,
        DatasetFields.election_result,
        DatasetFields.contacted,
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
                    x=alt.X(
                        f"{DatasetFields.trial}:O",
                        title=None,
                        axis=alt.Axis(labels=False, ticks=False),
                        scale=alt.Scale(padding=1),
                    ),
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
                    color=f"{DatasetFields.trial}:N",
                    column=alt.Column(
                        f"{cat_var}:N", spacing=40, header=alt.Header(orient="bottom")
                    ),
                )
            )

        save_path = Path(f"{cat_var}-errors-split.png").resolve()
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
                        x=alt.X(
                            f"{DatasetFields.trial}:O",
                            title=location,
                            axis=alt.Axis(labels=False, ticks=False),
                            scale=alt.Scale(padding=1),
                        ),
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
                        color=f"{DatasetFields.trial}:N",
                        column=alt.Column(
                            f"{DatasetFields.candidate_position}:N",
                            spacing=60,
                            header=alt.Header(orient="bottom"),
                        ),
                    )
                )

            location_plots &= error_types

    save_path = Path("location-errors-split.png").resolve()
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
            DatasetFields.location,
        ]:
            cat_var_plot |= (
                alt.Chart(data)
                .mark_boxplot(ticks=True)
                .encode(
                    x=alt.X(
                        f"{DatasetFields.trial}:O",
                        title=None,
                        axis=alt.Axis(labels=False, ticks=False),
                        scale=alt.Scale(padding=1),
                    ),
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
                    color=f"{DatasetFields.trial}:N",
                    column=alt.Column(
                        f"{cat_var}:N", spacing=60, header=alt.Header(orient="bottom")
                    ),
                )
            )

        err_type_plots &= cat_var_plot

    save_path = Path("error-types-by-category-splits.png").resolve()
    err_type_plots.save(str(save_path))

    return save_path
