#!/usr/bin/env python
# -*- coding: utf-8 -*-


def clean_url(url: str) -> str:
    print(url)
    url = url.replace("https://", "").replace("http://", "")
    if url.endswith("/"):
        url = url[:-1]

    return url
