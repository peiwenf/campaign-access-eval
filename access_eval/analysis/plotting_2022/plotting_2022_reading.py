#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging


import altair as alt
import pandas as pd

from ..constants_2022 import DatasetFields
from ..core_2022 import load_access_eval_2022_dataset

###############################################################################

PLOTTING_DIR = Path("plots/").resolve()
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)4s: %(module)s:%(lineno)4s %(asctime)s] %(message)s",
)
log = logging.getLogger(__name__)

###############################################################################


def plot_computed_fields_over_vote_share(
    data: Optional[pd.DataFrame] = None,
    save_path: Optional[Union[str, Path]] = None,
) -> Path:
    # Load default data
    if data is None:
        data = load_access_eval_2022_dataset()

    # Apply default save path
    if save_path is None:
        save_path = PLOTTING_DIR / "vote-share.png"

    # Ensure save path is Path object
    save_path = Path(save_path).resolve()
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate chart for axe-score
    reading_scale = alt.Scale(
        domain=[0, 100],
    )
    plot_cols = [
        DatasetFields.reading_score,
    ]

    chart = alt.hconcat(spacing=40)
    for col in plot_cols:
        scale=reading_scale
        chart |= (
            alt.Chart(data)
            .mark_point()
            .encode(
                alt.X(f"{DatasetFields.vote_share}:Q",
                      bin=alt.Bin(maxbins=20)),
                alt.Y(
                        col,
                        scale=scale
                    )
))
    chart.properties(title="Campaign Website Content")

    # Save fig and text
    fig_save_path = PLOTTING_DIR / "vote-share.png"
    fig_save_path.parent.mkdir(parents=True, exist_ok=True)
    chart.save(str(fig_save_path))
    return fig_save_path

def plot_computed_fields_over_vote_share_distance(
    data: Optional[pd.DataFrame] = None,
    save_path: Optional[Union[str, Path]] = None,
) -> Path:
    # Load default data
    if data is None:
        data = load_access_eval_2022_dataset()

    reading_scale = alt.Scale(
        domain=[0, 100],
    )
    plot_cols = [
        DatasetFields.reading_score,
    ]

    chart = alt.hconcat(spacing=40)
    for col in plot_cols:
        scale = reading_scale
        chart |= (
            alt.Chart(data)
            .mark_point()
            .encode(
                alt.X(f"{DatasetFields.competitiveness}:Q",
                      bin=alt.Bin(maxbins=20)),
                alt.Y(
                        col,
                        scale=scale
                    )
))
    chart.properties(title="Campaign Website Content")

    # Save fig and text
    fig_save_path = PLOTTING_DIR / "competitiveness.png"
    fig_save_path.parent.mkdir(parents=True, exist_ok=True)
    chart.save(str(fig_save_path))
    return fig_save_path

def plot_categorical_against_errors_boxplots(
    data: Optional[pd.DataFrame] = None,
) -> List[Path]:
    """
    Input data should be the "flattened" dataset.
    """
    # Load default data
    if data is None:
        data = load_access_eval_2022_dataset()

    # Set of categorical variables to use for box plot generation
    categorical_variables = [
        DatasetFields.electoral_level,
        DatasetFields.electoral_branch,
        DatasetFields.election_result,
        DatasetFields.electoral_level_3,
    ]

    save_paths = []
    reading_scale = alt.Scale(
        domain=[0, 100],
    )
    for cat_var in categorical_variables:
        # Break down the categorical variable
        if cat_var == DatasetFields.election_result:
            data = data.dropna(axis=0, subset=['election_result'])
        error_types = alt.hconcat()
        for err in [
            DatasetFields.reading_score,
        ]:
            feature_name = err
            plot_scale = reading_scale
            error_types |= (
                alt.Chart(data)
                .mark_boxplot(ticks=True)
                .encode(
                    y=alt.Y(
                        f"{feature_name}:Q",
                        scale=plot_scale,
                    ),
                    column=alt.Column(
                        f"{cat_var}:N", spacing=40, header=alt.Header(orient="bottom")
                    ),
                )
            )
        save_path = PLOTTING_DIR / f"{cat_var}-sentiment-split.png"
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
        data = load_access_eval_2022_dataset()


    location_counts = data[DatasetFields.state].value_counts()
    top_5_locations = location_counts.nlargest(5).index
    data = data[data[DatasetFields.location].isin(top_5_locations)]

    location_plots = alt.vconcat()
    reading_scale = alt.Scale(
        domain=[0, 100],
    )
    for location in data[DatasetFields.location].unique():
        location_subset = data.loc[data[DatasetFields.location] == location]

        if len(location_subset) > 4:
            error_types = alt.hconcat()
            for err in [
                DatasetFields.reading_score,
            ]:
                feature_name = err
                plot_scale = reading_scale
                error_types |= (
                    alt.Chart(location_subset)
                    .mark_boxplot(ticks=True)
                    .encode(
                        y=alt.Y(
                            f"{feature_name}:Q",
                            scale=plot_scale,
                        ),
                        column=alt.Column(
                            f"{DatasetFields.candidate_position}:N",
                            spacing=60,
                            header=alt.Header(orient="bottom"),
                        ),
                    )
                )

            location_plots &= error_types

    save_path = PLOTTING_DIR / "location-sentiment-split.png"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    location_plots.save(str(save_path))

    return save_path

def _plot_and_fig_text(
    data: pd.DataFrame,
    plot_cols: List[str],
    fig_text_prefix: str,
    subset_name: str,
    column: Optional[alt.Column] = None,
    consistent_scale: bool = False,
) -> None:
    reading_scale = alt.Scale(
        domain=[0, 100],
    )
    chart = alt.hconcat(spacing=40)
    for col in plot_cols:
        scale = reading_scale
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
        data = load_access_eval_2022_dataset()

    # Split into different commonly grouped stats
    # Content is the actual website content
    score_cols = [
        DatasetFields.reading_score,
    ]

    # Create content plots
    _plot_and_fig_text(
        data=data[[*score_cols, *keep_cols]],
        plot_cols=score_cols,
        fig_text_prefix=(
            "Distributions for key content statistics "
            "gathered while scraping campaign websites."
        ),
        subset_name=f"{subset_name}content-stats",
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
        data = load_access_eval_2022_dataset()

    # Drop any locations with less than two campaigns (originally <= 2)
    location_counts = data[DatasetFields.state].value_counts()
    top_5_locations = location_counts.nlargest(5).index
    log.info(top_5_locations)
    data = data[data[DatasetFields.state].isin(top_5_locations)]

    # Plot basic stats
    plot_summary_stats(
        data,
        subset_name="location-split-",
        keep_cols=[DatasetFields.state],
        plot_kwargs={"column": alt.Column(DatasetFields.state, spacing=60)},
    )


def plot_party_based_summary_stats(
    data: Optional[pd.DataFrame] = None,
) -> None:
    """
    Input data should be the "flattened" dataset.
    """
    # Load default data
    if data is None:
        data = load_access_eval_2022_dataset()

    location_counts = data[DatasetFields.party].value_counts()
    top_5_locations = location_counts.nlargest(5).index
    data = data[data[DatasetFields.party].isin(top_5_locations)]

    # Plot basic stats
    plot_summary_stats(
        data,
        subset_name="election-party-split-",
        keep_cols=[DatasetFields.party],
        plot_kwargs={"column": alt.Column(DatasetFields.party, spacing=40)},
    )


def plot_electoral_position_based_summary_stats(
    data: Optional[pd.DataFrame] = None,
) -> None:
    """
    Input data should be the "flattened" dataset.
    """
    # Load default data
    if data is None:
        data = load_access_eval_2022_dataset()

    location_counts = data[DatasetFields.electoral_position].value_counts()
    top_5_locations = location_counts.nlargest(5).index
    log.info(top_5_locations)
    data = data[data[DatasetFields.electoral_position].isin(top_5_locations)]

    # Plot basic stats
    plot_summary_stats(
        data,
        subset_name="election-position-split-",
        keep_cols=[DatasetFields.electoral_position],
        plot_kwargs={
            "column": alt.Column(DatasetFields.electoral_position, spacing=40)
        },
    )

def plot_electoral_level_against_vote_share(
    data: Optional[pd.DataFrame] = None,
) -> Path:
    """
    Input data should be the "flattened" dataset.
    """
    # Load default data
    if data is None:
        data = load_access_eval_2022_dataset()

    level_plots = alt.vconcat()
    reading_scale = alt.Scale(
        domain=[0, 100],
    )
    for level in data[DatasetFields.electoral_level].unique():
        level_subset = data.loc[data[DatasetFields.electoral_level] == level]

        error_types = alt.hconcat()
        for err in [
            DatasetFields.reading_score,
        ]:
            feature_name = err
            plot_scale = reading_scale
            error_types |= (
                alt.Chart(level_subset)
                .mark_point()
                .encode(
                    x=alt.X(
                        f"{DatasetFields.vote_share}:Q",
                        scale = alt.Scale(
        domain=[0, 1],
    )),
                    y=alt.Y(
                        f"{feature_name}:Q",
                        scale=plot_scale,
                    ),
                    column=alt.Column(
                        f"{level}:N",
                        spacing=40,
                        header=alt.Header(orient="top"),
                    ),
                ).properties(
                    title = f"{level}"
                )
            )
        level_plots &= error_types

    save_path = PLOTTING_DIR / "level-sentiment-split.png"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    level_plots.save(str(save_path))

    return save_path

def plot_electoral_branch_against_vote_share(
    data: Optional[pd.DataFrame] = None,
) -> Path:
    """
    Input data should be the "flattened" dataset.
    """
    # Load default data
    if data is None:
        data = load_access_eval_2022_dataset()

    branch_plots = alt.vconcat()
    reading_scale = alt.Scale(
        domain=[0, 100],
    )
    for branch in data[DatasetFields.electoral_branch].unique():
        branch_subset = data.loc[data[DatasetFields.electoral_branch] == branch]

        error_types = alt.hconcat()
        for err in [
            DatasetFields.reading_score,
        ]:
            feature_name = err
            plot_scale = reading_scale
            error_types |= (
                alt.Chart(branch_subset)
                .mark_point()
                .encode(
                    x=alt.X(
                        f"{DatasetFields.vote_share}:Q",
                        scale = alt.Scale(
        domain=[0, 1],
    )),
                    y=alt.Y(
                        f"{feature_name}:Q",
                        scale=plot_scale,
                    ),
                    column=alt.Column(
                        f"{branch}:N",
                        spacing=40,
                        header=alt.Header(orient="top"),
                    ),
                ).properties(
                    title = f"{branch}"
                )
            )
        branch_plots &= error_types

    save_path = PLOTTING_DIR / "branch-sentiment-split.png"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    branch_plots.save(str(save_path))

    return save_path
