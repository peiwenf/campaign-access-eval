#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Union

import pandas as pd

from .. import constants

###############################################################################

TEMPLATE_TEXT = """
Hello,

We are a team of researchers at the University of Washington – We are reaching out to candidates running for an elected position about the accessibility of their campaign website.

The content published at: '{url}' currently contains accessibility violations for hearing and/ or visually impaired people that depend on screen reading software.

The most common violation types we found from your website are described below and our full accessibility evaluation results can be found in the attached Google Drive link. Each violation comes with an explanation of the issue and a link that you can provide to your website developer with directions for how to potentially fix the problem.

Most Common Violations:

{violations_tree}

Full Results:
<GOOGLE DRIVE LINK>

If you would like any further instruction or help, please see our documentation explaining the layout and the content of the Google Drive folder which contains the full accessibility violation results: https://bits-research.github.io/campaign-access-eval/results_explainer.html

Additionally please feel free to respond to this email and we will be happy to talk with any of your staff. We are not trying to sell you any services or consultation, we simply want to help ensure that all voters are able to view and interact with each candidate's website for the upcoming election.

Thank you for your time and attention – And best of luck with your campaign.

Nic Weber
University of Washington School of Information
nmweber@uw.edu
""".strip()  # noqa: 501


def generate_email_text(head_dir: Union[str, Path]) -> Path:
    """
    Generate email text from data found in the provided directory.

    Parameters
    ----------
    head_dir: Union[str, Path]
        The directory with all results.

    Returns
    -------
    email_text: Path
        Path to text file containing suggested email message.
    """
    # Validate provided dir
    if isinstance(head_dir, str):
        head_dir = Path(head_dir)

    # Resolve
    head_dir = head_dir.resolve(strict=True)
    if head_dir.is_file():
        raise NotADirectoryError(str(head_dir))

    # Get and read the aggregate results
    agg_results = pd.read_csv(head_dir / constants.AGGREGATE_AXE_RESULTS_FILENAME)

    # Get head for top results
    agg_head = agg_results.head()

    # Construct violations tree
    violations_tree = []
    for i, row in agg_head.iterrows():
        this_section = [
            f"Impact: {row.impact}",
            f"Description: {row.reason}",
            f"Further Documentation: {row.help_url}",
            f"Number of Pages Affected: {row.number_of_pages_affected}",
            (
                f"Number of Individual Elements Affected: "
                f"{row.number_of_elements_in_violation}"
            ),
        ]
        this_section_str = "\n\t".join(this_section)
        violations_tree.append(f"{i}. {row.id}\n\t{this_section_str}")

    # Convert violations tree to text
    violations_tree_str = "\n\n".join(violations_tree)

    # Format email and store
    email_txt = TEMPLATE_TEXT.format(
        url=head_dir.name,
        violations_tree=violations_tree_str,
    )
    email_text_filepath = head_dir / "email.txt"
    with open(email_text_filepath, "w") as open_f:
        open_f.write(email_txt)

    return email_text_filepath
