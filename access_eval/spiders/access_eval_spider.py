#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import tldextract
from axe_selenium_python import Axe
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider
from scrapy_selenium import SeleniumRequest
from selenium import webdriver
from selenium.webdriver import FirefoxOptions

from .. import constants
from ..utils import clean_url

if TYPE_CHECKING:
    from typing import Any

    from scrapy.http.response.html import HtmlResponse

###############################################################################


class AccessEvalSpider(CrawlSpider):
    name = "AccessEvalSpider"

    custom_settings = {
        'DEPTH_LIMIT': 3,
        }

    def __init__(self, url: str, **kwargs: "Any"):
        # Parse domain
        parsed_url = tldextract.extract(url)

        # Optionally insert subdomain
        domain_parts = [parsed_url.domain, parsed_url.suffix]
        if len(parsed_url.subdomain) > 0:
            domain_parts.insert(0, parsed_url.subdomain)

        # Generate allowed domain
        domain = ".".join(domain_parts)

        # Apply params
        self.allowed_domains = [domain]
        self.start_urls = [url]

        # Super
        super().__init__(**kwargs)

    def parse_result(self, response: "HtmlResponse") -> None:
        # We spawn a new webdriver process for each page because
        # scrapy parses pages asynchronously with the same driver
        # So by the time we are done injecting aXe and processing the page
        # the driver may have moved on to a new page
        # This gets around that by just forcing aXe to run on a new driver each time
        # Expensive but works :shrug:
        opts = FirefoxOptions()
        opts.add_argument("--headless")
        driver = webdriver.Firefox(firefox_options=opts)
        driver.get(response.request.url)

        # Connect Axe to driver
        axe = Axe(driver)
        axe.inject()

        # Run checks and store results
        results = axe.run()
        driver.close()

        # Construct storage path
        url = clean_url(response.request.url)
        storage_dir = Path(url)
        storage_dir.mkdir(exist_ok=True, parents=True)
        axe.write_results(
            results,
            str(storage_dir / constants.SINGLE_PAGE_AXE_RESULTS_FILENAME),
        )

    def start_requests(self) -> SeleniumRequest:
        # Spawn Selenium requests for each link
        # (should just be just the provided URL though)
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                wait_time=5,
                callback=self.parse,
            )

    def parse(self, response: "HtmlResponse", **kwargs: "Any") -> SeleniumRequest:
        self.log(f"Parsing: {response.request.url}", level=logging.INFO)
        # Process with axe
        self.parse_result(response)

        # Recurse down links
        le = LinkExtractor()
        for link in le.extract_links(response):
            yield SeleniumRequest(
                url=link.url,
                wait_time=5,
                callback=self.parse,
            )