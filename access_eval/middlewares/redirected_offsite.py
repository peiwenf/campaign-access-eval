#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import TYPE_CHECKING

from scrapy.exceptions import IgnoreRequest
from scrapy.spidermiddlewares.offsite import (
    OffsiteMiddleware as OffsiteSpiderMiddleware,
)

if TYPE_CHECKING:
    from scrapy.spiders import Spider
    from scrapy_selenium import SeleniumRequest

###############################################################################


class OffsiteDownloaderMiddleware(OffsiteSpiderMiddleware):
    def process_request(self, request: "SeleniumRequest", spider: "Spider") -> None:
        result = list(self.process_spider_output(None, [request], spider))
        if not result:
            raise IgnoreRequest()
        return None
