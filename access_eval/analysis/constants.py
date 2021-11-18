#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

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

###############################################################################


class DatasetFields:
    """
    This class stores all of the headers for the analysis dataset.

    Each header will have a description and some examples.
    Use this class as a data dictionary.
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

    diff_pages = "diff_pages"
    """
    int: The difference in the number of pages before and after contact.

    Examples
    --------
    - 1
    - 2
    """

    diff_errors = "diff_errors"
    """
    int: The difference in the number of errors before and after contact.

    Examples
    --------
    - 12
    - 42
    """

    diff_critical_errors = "diff_critical_errors"
    """
    int: The difference in the number of errors categorized as "critical" by aXe
    before and after contact.

    Examples
    --------
    - 12
    - 42
    """

    diff_serious_errors = "diff_serious_errors"
    """
    int: The difference in the number of errors categorized as "serious" by aXe
    before and after contact.

    Examples
    --------
    - 12
    - 42
    """

    diff_moderate_errors = "diff_moderate_errors"
    """
    int: The difference in the number of errors categorized as "moderate" by aXe
    before and after contact.

    Examples
    --------
    - 12
    - 42
    """

    diff_minor_errors = "diff_minor_errors"
    """
    int: The difference in the number of errors categorized as "minor" by aXe
    before and after contact.

    Examples
    --------
    - 12
    - 42
    """
