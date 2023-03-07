#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import sys
import time
import traceback
from functools import partial
from pathlib import Path

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from textblob import TextBlob
from tqdm import tqdm

###############################################################################

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)4s: %(module)s:%(lineno)4s %(asctime)s] %(message)s",
)
log = logging.getLogger(__name__)

###############################################################################


class Args(argparse.Namespace):
    def __init__(self) -> None:
        self.__parse()

    def __parse(self) -> None:
        p = argparse.ArgumentParser(
            prog="get-sentiment-for-landing-page-content",
            description=(
                "For each campaign website in the provided dataset, "
                "load the page, retrieve all text content, "
                "and compute sentiment with spacy."
            ),
        )
        p.add_argument(
            "dataset",
            type=str,
            help="The path to the dataset as a CSV to use.",
        )
        p.add_argument(
            "-c",
            "--url_column",
            type=str,
            default="campaign_website_url",
            help=(
                "The column name in the dataset which contains "
                "the campaign website URLs."
            ),
        )
        p.parse_args(namespace=self)


###############################################################################


def _process_url(row: pd.Series, url_column: str) -> float:
    try:
        # Create new firefox headless browser
        opts = FirefoxOptions()
        opts.add_argument("--headless")
        url = row[url_column]
        with webdriver.Firefox(firefox_options=opts) as driver:
            log.debug(f"Starting page load for: '{url}'.")
            # Start page load
            driver.get(url)
            log.debug("Sleeping for 2 seconds.")
            # Wait for all page content
            time.sleep(2)

            # Get all text
            log.debug("Getting all page text.")
            page_text = driver.find_element(By.XPATH, "/html/body").text

        # Get sentiment
        log.debug("Processing text to get sentiment.")
        blob = TextBlob(page_text)
        row["polarity"] = blob.polarity
        row["subjectivity"] = blob.subjectivity

    except Exception:
        row["polarity"] = np.nan
        row["subjectivity"] = np.nan

    return row


def _process_dataset(dataset: str, url_column: str = "campaign_website_url") -> str:
    # Create process function partial
    process_func = partial(_process_url, url_column=url_column)

    # Load the dataset
    df = pd.read_csv(dataset)

    # Apply tqdm pandas
    tqdm.pandas()

    # Progress apply
    df = df.progress_apply(process_func, axis=1)

    # Store to new dataset
    original_path = Path(dataset).resolve()
    new_path = original_path.with_name(f"{original_path.stem}-with-sentiment")
    df.to_csv(new_path, index=False)


def main() -> None:
    try:
        args = Args()
        _process_dataset(args.dataset, args.url_column)

    except Exception as e:
        log.error("=============================================")
        log.error("\n\n" + traceback.format_exc())
        log.error("=============================================")
        log.error("\n\n" + str(e) + "\n")
        log.error("=============================================")
        sys.exit(1)


###############################################################################
# Allow caller to directly run this module (usually in development scenarios)

if __name__ == "__main__":
    main()
