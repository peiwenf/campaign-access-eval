#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Callable, NamedTuple

###############################################################################
# modify this section if you want apply the same thods to other data

ACCESS_EVAL_2022_STUDY_REPORTS = Path(__file__).parent / "reports_2022"
ACCESS_EVAL_2022_STUDY_DATA = Path(__file__).parent / "data_2022"

# the data used to generate reports 
ACCESS_EVAL_2022_ELECTION_RESULTS = ACCESS_EVAL_2022_STUDY_DATA / "total_2022_axe_score.csv"
# zip file for the reports
ACCESS_EVAL_2022_EVALS_ZIP = (
    ACCESS_EVAL_2022_STUDY_REPORTS / "LocalElections.zip"
)
ACCESS_EVAL_2022_EVALS_UNPACKED = Path("unpacked-eval-results")

# orginal data combines with the information in the reports
ACCESS_EVAL_2022_DATASET = ACCESS_EVAL_2022_STUDY_DATA / "total_2022_ease_of_reading_analyze.csv"
# if want to get a version that contains all the candidates:
# ACCESS_EVAL_2022_DATASET_NA = ACCESS_EVAL_2022_STUDY_DATA / "2022-local-elections-study-data-na.csv"

###############################################################################


class ComputedField(NamedTuple):
    name: str
    func: Callable


class DatasetFields:
    """
    This class stores all of the headers for the analysis dataset.

    Each header will have a description and some examples.
    Use this class as a data dictionary.
    """

    state = "state"
    """
    str: The State where the election is held.

    Examples
    --------
    - "Alabama"
    - "Arizona"
    """

    location = "location"
    """
    str: The District or County for the election.

    Examples
    --------
    - "Alabama 1st"
    - "Little Rock"
    """

    campaign_website_url = "campaign_website_url"
    """
    str: The public URL for the campaign website.

    Examples
    --------
    - "https://www.google.com"
    - "https://jacksonmaxfield.github.io"
    """

    electoral_position = "electoral_position"
    """
    str: The position the candidate was running for.

    Examples
    --------
    - "Mayor"
    - "Council"
    """

    electoral_level= "electoral_level"
    """
    str: The electoral level of the race.

    Examples
    --------
    - "Federal"
    - "State"
    - "Special District"
    - "County"
    - "City"
    - "City/County"
    """

    electoral_level_3= "electoral_level_3"
    """
    str: The electoral level of the races that categorized into
    three levels only(Federal, State, and Local).

    Examples
    --------
    - "Federal"
    - "State"
    - "Local"
    """

    electoral_branch = "electoral_branch"
    """
    str: The electoral branch of the races.

    Examples
    --------
    - "Judicial"
    - "Legisilative"
    - "Executive"
    """

    election_result = "election_result"
    """
    str: Categorical value for is the candidate won (or progressed) or not.

    Examples
    --------
    - "Won"
    - "Lost"

    Notes
    -----
    Pulled from external data source.
    """

    number_of_votes_for_candidate = "number_of_votes_for_candidate"
    """
    int: The number of votes the candidate ultimately received.

    Examples
    --------
    - 12345
    - 2468

    Notes
    -----
    Pulled from external data source.
    """

    number_of_votes_for_race = "number_of_votes_for_race"
    """
    int: The total number of votes returned in the election.

    Examples
    --------
    - 123456
    - 24680

    Notes
    -----
    Pulled from external data source.
    """

    vote_share = "vote_share"
    """
    float: The number of votes the candidate received over the number of votes possible.

    Examples
    --------
    - 0.21
    - 0.47
    """

    party = "party"
    """
    str: The party of the candidate.

    Examples
    --------
    - "Democratic Party"
    - "Independent"
    """

    competitiveness = 'competitiveness'
    """
    float: The distance between the vote share of the candidate and 0.5

    Examples
    --------
    - "0.1"
    - "0.5"
    """

    number_of_words = "number_of_words"
    """
    int: The total number of words found in the whole campaign website.
    Calculated on the latest version of the website.

    Examples
    --------
    - 9999
    - 12345
    """

    number_of_unique_words = "number_of_unique_words"
    """
    int: The total number of unique words found in the whole campaign website.
    Calculated on the latest version of the website.

    Examples
    --------
    - 999
    - 1234
    """

    ease_of_reading = "ease_of_reading"
    """
    float: The lexical complexity of the entire website.
    Calculated on the latest version of the website.

    See: https://github.com/shivam5992/textstat#the-flesch-reading-ease-formula
    for more information.

    Examples
    --------
    - 123.45
    - -12.34
    """

    number_of_pages = "number_of_pages"
    """
    int: The total number of pages found in the whole campaign website before contact.

    Examples
    --------
    - 12
    - 42
    """

    number_of_total_errors = "number_of_total_errors"
    """
    int: The total number of errors for the entire website before contact.

    Examples
    --------
    - 234
    - 450
    """

    number_of_critical_errors = "number_of_critical_errors"
    """
    int: The number of errors categorized as "critical" by aXe for the
    entire website before contact.

    Examples
    --------
    - 123
    - 42
    """

    number_of_serious_errors = "number_of_serious_errors"
    """
    int: The number of errors categorized as "serious" by aXe for the
    entire website before contact.

    Examples
    --------
    - 123
    - 42
    """

    number_of_moderate_errors = "number_of_moderate_errors"
    """
    int: The number of errors categorized as "moderate" by aXe for the
    entire website before contact.

    Examples
    --------
    - 123
    - 42
    """

    number_of_minor_errors = "number_of_minor_errors"
    """
    int: The number of errors categorized as "minor" by aXe for the
    entire website before contact.

    Examples
    --------
    - 123
    - 42
    """

    error_type_x = "error_type_x"
    """
    int: There are many columns that begin with 'error-type_'.
    Such columns are just the aggregate value of that error type X for that campaign.

    Examples
    --------
    - "error-type_label_pre": 12
    - "error-type_frame-title_post": 4

    Notes
    -----
    These columns have a computed field as well which is the `avg_error-type_x` for both
    pre and post.
    """

    axe_score = "axe-score"
    """
    float: A score that reflects the accessibilty of the candidates' website.

    Examples
    --------
    - 78.44787284
    - 80.0
    """

    z_score = 'z_score'
    """
    float: The z-score of the axe-score.

    Examples
    --------
    - 0.66512043
    - -2.495473645
    """

    polarity = "polarity"
    """
    float: The score that shows the tone of the contents in the website, where -1 means negative and
    1 means positive.

    Examples
    --------
    - 0
    - -0.25
    """

    subjectivity = "subjectivity"
    """
    float: The score that shows the amount of textual evidence or personal opinions in the webpage context,
    where 0 means the content is more objective and 1 presents more subjectivity.

    Examples
    --------
    - 0.5
    - 0.315
    """

    reading_score = 'reading_score'
    """
    float: The reading score generated based on the Flesch-Kincaid readbility test,
    where all score above 100 is counted as 100 and the scores below 0 is counted as 0.

    Examples
    --------
    - 30.54
    - 100.0
    """


class ComputedFields:

    # Averages
    avg_errors_per_page = ComputedField(
        name="avg_errors_per_page",
        func=lambda data: data[DatasetFields.number_of_total_errors]
        / data[DatasetFields.number_of_pages],
    )

    avg_critical_errors_per_page = ComputedField(
        name="avg_critical_errors_per_page",
        func=lambda data: data[DatasetFields.number_of_critical_errors]
        / data[DatasetFields.number_of_pages],
    )

    avg_serious_errors_per_page = ComputedField(
        name="avg_serious_errors_per_page",
        func=lambda data: data[DatasetFields.number_of_serious_errors]
        / data[DatasetFields.number_of_pages],
    )

    avg_moderate_errors_per_page = ComputedField(
        name="avg_moderate_errors_per_page",
        func=lambda data: data[DatasetFields.number_of_moderate_errors]
        / data[DatasetFields.number_of_pages],
    )

    avg_minor_errors_per_page = ComputedField(
        name="avg_minor_errors_per_page",
        func=lambda data: data[DatasetFields.number_of_minor_errors]
        / data[DatasetFields.number_of_pages],
    )

    avg_number_of_words_per_page = ComputedField(
        name="avg_number_of_words_per_page",
        func=lambda data: data[DatasetFields.number_of_words]
        / data[DatasetFields.number_of_pages],
    )

    # Vote share
    vote_share_per_error = ComputedField(
        name="vote_share_per_error",
        func=lambda data: data[DatasetFields.vote_share]
        / data[DatasetFields.number_of_total_errors],
    )

    vote_share_per_critical_error = ComputedField(
        name="vote_share_per_critical_error",
        func=lambda data: data[DatasetFields.vote_share]
        / data[DatasetFields.number_of_critical_errors],
    )

    vote_share_per_serious_error = ComputedField(
        name="vote_share_per_serious_error",
        func=lambda data: data[DatasetFields.vote_share]
        / data[DatasetFields.number_of_serious_errors],
    )

    vote_share_per_moderate_error = ComputedField(
        name="vote_share_per_moderate_error",
        func=lambda data: data[DatasetFields.vote_share]
        / data[DatasetFields.number_of_moderate_errors],
    )

    vote_share_per_minor_error = ComputedField(
        name="vote_share_per_minor_error",
        func=lambda data: data[DatasetFields.vote_share]
        / data[DatasetFields.number_of_minor_errors],
    )
