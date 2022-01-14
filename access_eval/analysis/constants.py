#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Callable, NamedTuple

###############################################################################


ACCESS_EVAL_2021_STUDY_DATA = Path(__file__).parent / "data"
ACCESS_EVAL_2021_WEB_SCRAPING = (
    ACCESS_EVAL_2021_STUDY_DATA / "web-scraping-candidates.csv"
)
ACCESS_EVAL_2021_ELECTION_RESULTS = ACCESS_EVAL_2021_STUDY_DATA / "election-results.csv"
ACCESS_EVAL_2021_PRE_CONTACT_EVALS_ZIP = (
    ACCESS_EVAL_2021_STUDY_DATA / "pre-access-eval-results.zip"
)
ACCESS_EVAL_2021_POST_CONTACT_EVALS_ZIP = (
    ACCESS_EVAL_2021_STUDY_DATA / "post-access-eval-results.zip"
)

ACCESS_EVAL_2021_PRE_CONTACT_EVALS_UNPACKED = Path("unpacked-pre-access-eval-results")
ACCESS_EVAL_2021_POST_CONTACT_EVALS_UNPACKED = Path("unpacked-post-access-eval-results")

ACCESS_EVAL_2021_DATASET = ACCESS_EVAL_2021_STUDY_DATA / "2021-study-data.csv"

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

    location = "location"
    """
    str: The municipality or general location where the election
    took place.

    Examples
    --------
    - "Seattle, WA"
    - "New Orleans, LA"
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

    candidate_position = "candidate_position"
    """
    str: Categorical value for if the candidate is the incumbent, a challenger, or open.

    Examples
    --------
    - "Incumbent"
    - "Challenger"
    - "Open"
    """

    candidate_history = "candidate_history"
    """
    str: Categorical value for the electoral history of the candidate.

    Examples
    --------
    - "In-Office"
    - "Previously-Elected"
    - "Never-Held-Office"

    Notes
    -----
    Pulled from external data source.
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

    election_type = "election_type"
    """
    str: Categorical value for the type of election.

    Examples
    --------
    - "Primary"
    - "General"
    - "Runoff"
    """

    eligible_voting_population = "eligible_voting_population"
    """
    int: The total number of people eligible to vote in the election.

    Examples
    --------
    - 123456
    - 24680

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

    race_funding = "race_funding"
    """
    float: The amount of money all candidates in the race received during the campaign.

    Examples
    --------
    - 10000000.00
    - 24500000.00

    Notes
    -----
    Pulled from external data source.
    """

    candidate_funding = "candidate_funding"
    """
    float: The amount of money the candidate received in donations during the campaign.

    Examples
    --------
    - 100000.00
    - 350000.00

    Notes
    -----
    Calculated as sum of all other candidates funding in same race.

    Pulled from external data. (Not all candidates had websites scraped scraped)
    """

    funding_share = "funding_share"
    """
    float: The amount of money the candidate received in donations over the amount of
    money all candidates received during the campaign.

    Examples
    --------
    - 0.21
    - 0.47
    """

    contacted = "contacted"
    """
    str: Was the campaign contacted with the aXe evaluation summarization.

    Examples
    --------
    - "Contacted"
    - "Not-Contacted"

    Notes
    -----
    If the campaign was not contacted, the values for pre and post features are set to
    equal.
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

    number_of_pages_pre = "number_of_pages_pre"
    """
    int: The total number of pages found in the whole campaign website before contact.

    Examples
    --------
    - 12
    - 42
    """

    number_of_total_errors_pre = "number_of_total_errors_pre"
    """
    int: The total number of errors for the entire website before contact.

    Examples
    --------
    - 234
    - 450
    """

    number_of_critical_errors_pre = "number_of_critical_errors_pre"
    """
    int: The number of errors categorized as "critical" by aXe for the
    entire website before contact.

    Examples
    --------
    - 123
    - 42
    """

    number_of_serious_errors_pre = "number_of_serious_errors_pre"
    """
    int: The number of errors categorized as "serious" by aXe for the
    entire website before contact.

    Examples
    --------
    - 123
    - 42
    """

    number_of_moderate_errors_pre = "number_of_moderate_errors_pre"
    """
    int: The number of errors categorized as "moderate" by aXe for the
    entire website before contact.

    Examples
    --------
    - 123
    - 42
    """

    number_of_minor_errors_pre = "number_of_minor_errors_pre"
    """
    int: The number of errors categorized as "minor" by aXe for the
    entire website before contact.

    Examples
    --------
    - 123
    - 42
    """

    number_of_pages_post = "number_of_pages_post"
    """
    int: The total number of pages found in the whole campaign website after contact.

    Examples
    --------
    - 12
    - 42
    """

    number_of_total_errors_post = "number_of_total_errors_post"
    """
    int: The total number of errors for the entire website after contact.

    Examples
    --------
    - 234
    - 450
    """

    number_of_critical_errors_post = "number_of_critical_errors_post"
    """
    int: The number of errors categorized as "critical" by aXe for the
    entire website after contact.

    Examples
    --------
    - 123
    - 42
    """

    number_of_serious_errors_post = "number_of_serious_errors_post"
    """
    int: The number of errors categorized as "serious" by aXe for the
    entire website after contact.

    Examples
    --------
    - 123
    - 42
    """

    number_of_moderate_errors_post = "number_of_moderate_errors_post"
    """
    int: The number of errors categorized as "moderate" by aXe for the
    entire website after contact.

    Examples
    --------
    - 123
    - 42
    """

    number_of_minor_errors_post = "number_of_minor_errors_post"
    """
    int: The number of errors categorized as "minor" by aXe for the
    entire website after contact.

    Examples
    --------
    - 123
    - 42
    """

    trial = "trial"
    """
    str: The categorical variable added when the data has been flattened
    from "pre" and "post" having independent columns to now sharing columns.

    Examples
    --------
    - "Pre"
    - "Post"

    Notes
    -----
    This is only added with the flattened data.
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


class ComputedFields:

    # Differences
    diff_pages = ComputedField(
        name="diff_pages",
        func=lambda data: data[DatasetFields.number_of_pages_post]
        - data[DatasetFields.number_of_pages_pre],
    )

    diff_errors = ComputedField(
        name="diff_errors",
        func=lambda data: data[DatasetFields.number_of_total_errors_post]
        - data[DatasetFields.number_of_total_errors_pre],
    )

    diff_critical_errors = ComputedField(
        name="diff_critical_errors",
        func=lambda data: data[DatasetFields.number_of_critical_errors_post]
        - data[DatasetFields.number_of_critical_errors_pre],
    )

    diff_serious_errors = ComputedField(
        name="diff_serious_errors",
        func=lambda data: data[DatasetFields.number_of_serious_errors_post]
        - data[DatasetFields.number_of_serious_errors_pre],
    )

    diff_moderate_errors = ComputedField(
        name="diff_moderate_errors",
        func=lambda data: data[DatasetFields.number_of_moderate_errors_post]
        - data[DatasetFields.number_of_moderate_errors_pre],
    )

    diff_minor_errors = ComputedField(
        name="diff_minor_errors",
        func=lambda data: data[DatasetFields.number_of_minor_errors_post]
        - data[DatasetFields.number_of_minor_errors_pre],
    )

    # Averages
    avg_errors_per_page_pre = ComputedField(
        name="avg_errors_per_page_pre",
        func=lambda data: data[DatasetFields.number_of_total_errors_pre]
        / data[DatasetFields.number_of_pages_pre],
    )

    avg_errors_per_page_post = ComputedField(
        name="avg_errors_per_page_post",
        func=lambda data: data[DatasetFields.number_of_total_errors_post]
        / data[DatasetFields.number_of_pages_post],
    )

    avg_critical_errors_per_page_pre = ComputedField(
        name="avg_critical_errors_per_page_pre",
        func=lambda data: data[DatasetFields.number_of_critical_errors_pre]
        / data[DatasetFields.number_of_pages_pre],
    )

    avg_critical_errors_per_page_post = ComputedField(
        name="avg_critical_errors_per_page_post",
        func=lambda data: data[DatasetFields.number_of_critical_errors_post]
        / data[DatasetFields.number_of_pages_post],
    )

    avg_serious_errors_per_page_pre = ComputedField(
        name="avg_serious_errors_per_page_pre",
        func=lambda data: data[DatasetFields.number_of_serious_errors_pre]
        / data[DatasetFields.number_of_pages_pre],
    )

    avg_serious_errors_per_page_post = ComputedField(
        name="avg_serious_errors_per_page_post",
        func=lambda data: data[DatasetFields.number_of_serious_errors_post]
        / data[DatasetFields.number_of_pages_post],
    )

    avg_moderate_errors_per_page_pre = ComputedField(
        name="avg_moderate_errors_per_page_pre",
        func=lambda data: data[DatasetFields.number_of_moderate_errors_pre]
        / data[DatasetFields.number_of_pages_pre],
    )

    avg_moderate_errors_per_page_post = ComputedField(
        name="avg_moderate_errors_per_page_post",
        func=lambda data: data[DatasetFields.number_of_moderate_errors_post]
        / data[DatasetFields.number_of_pages_post],
    )

    avg_minor_errors_per_page_pre = ComputedField(
        name="avg_minor_errors_per_page_pre",
        func=lambda data: data[DatasetFields.number_of_minor_errors_pre]
        / data[DatasetFields.number_of_pages_pre],
    )

    avg_minor_errors_per_page_post = ComputedField(
        name="avg_minor_errors_per_page_post",
        func=lambda data: data[DatasetFields.number_of_minor_errors_post]
        / data[DatasetFields.number_of_pages_post],
    )

    avg_number_of_words_per_page = ComputedField(
        name="avg_number_of_words_per_page",
        func=lambda data: data[DatasetFields.number_of_words]
        / data[DatasetFields.number_of_pages_post],
    )

    # Vote share
    vote_share_per_error = ComputedField(
        name="vote_share_per_error",
        func=lambda data: data[DatasetFields.vote_share]
        / data[DatasetFields.number_of_total_errors_post],
    )

    vote_share_per_critical_error = ComputedField(
        name="vote_share_per_critical_error",
        func=lambda data: data[DatasetFields.vote_share]
        / data[DatasetFields.number_of_critical_errors_post],
    )

    vote_share_per_serious_error = ComputedField(
        name="vote_share_per_serious_error",
        func=lambda data: data[DatasetFields.vote_share]
        / data[DatasetFields.number_of_serious_errors_post],
    )

    vote_share_per_moderate_error = ComputedField(
        name="vote_share_per_moderate_error",
        func=lambda data: data[DatasetFields.vote_share]
        / data[DatasetFields.number_of_moderate_errors_post],
    )

    vote_share_per_minor_error = ComputedField(
        name="vote_share_per_minor_error",
        func=lambda data: data[DatasetFields.vote_share]
        / data[DatasetFields.number_of_minor_errors_post],
    )
