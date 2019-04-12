from typing import List
import re
import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

version = "0.3"
GET = "GET"
POST = "POST"


class CrawlerException(Exception):
    pass


class HTTPError(CrawlerException):
    def __init__(self, status, value=None):
        self.status = status
        self.value = value
        super(HTTPError, self).__init__(f"{self.status}: {repr(self.value)[:200]}")


def get_url_text(
    url,
    params=None,
    data=None,
    json=False,
    binary=False,
    method=GET,
    include_response=False
):
    allowed_methods = [GET, POST]
    assert method in allowed_methods, f"method must in {allowed_methods}"
    res = getattr(requests, method.lower())(url, params=params, data=data)
    err = None if res.status_code == 200 else res.status_code
    value = res.json() if json else res.content if binary else res.text
    if include_response:
        return err, value, res
    else:
        return err, value


def html2soup(html, from_encoding=None):
    if from_encoding:
        rv = BeautifulSoup(html, "html.parser", from_encoding=from_encoding)
    else:
        rv = BeautifulSoup(html, "html.parser")
    return rv


class URL:
    method: str = GET
    url: str = None
    params: dict = None
    data: dict = None
    # default text
    is_json = False
    is_binary = False

    referer = None

    def __init__(
        self,
        url: str,
        method: str = GET,
        params=None,
        data=None,
        is_json=False,
        is_binary=False,
        referer=None # type: URL
    ):
        self.method = method
        self.url = url
        self.params = params
        self.data = data
        self.is_json = is_json
        self.is_binary = is_binary
        self.referer = referer

    def __repr__(self):
        return f"<URL: {self.method} {self.url}>"


class Page:
    url: URL = None
    content: bytes = None
    text: str = None
    soup: BeautifulSoup = None
    json = None # type: list or dict
    type = str # enum: BYTES, TEXT, HTML, JSON
    is_html = False

    url_regexp = re.compile(r"(https?|ftp|file)://[-A-Za-z0-9\+&@#/%?=~_|!:,.;]*[-A-Za-z0-9\+&@#/%=~_|]")

    def __init__(self, url: URL, value=None, is_html=False):
        self.url = url
        self.is_html = is_html

        if isinstance(value, bytes):
            self.type = "BYTES"
            self.content = value
            if is_html:
                self.type = "HTML"
                self.soup = html2soup(value)
        elif isinstance(value, str):
            self.type = "TEXT"
            self.text = value
            if is_html:
                self.type = "HTML"
                self.soup = html2soup(value)
        elif isinstance(value, (list, dict)):
            self.type = "JSON"
            self.json = value

    def __repr__(self):
        return f"<Page: {self.type} {self.url}>"

    def is_binary(self):
        return self.text is not None

    def get_next_urls(self) -> List[URL]:
        if self.is_html:
            links = self.soup.select("a")
            urls = [
                x["href"] if x[
                    "href"
                ].startswith("http") else urljoin(self.url.url, x["href"])
                for x in links
                if
                x.has_attr("href") and not x["href"].startswith("javascript")
            ]
            return [URL(x) for x in urls]
        return []


class URLExt:
    url = None

    def __init__(self, url: URL):
        self.url = url

    def do_http(self) -> Page:
        url = self.url
        (
            err,
            value,
            res
        ) = get_url_text(url.url, params=url.params, data=url.data, json=url.is_json, binary=os.getenv("AUTO_CHARSET")
        or
        url.is_binary, method=url.method, include_response=True)
        if err:
            raise HTTPError(err, value)
        is_html = res.headers["content-type"] == "text/html"
        page = Page(url, value, is_html=is_html)
        return page


class Crawler:
    def __init__(self, start_url):
        self.start_url = start_url
        self.seen = set()

    def start(self):
        U = URLExt(URL(self.start_url))
        P = U.do_http()
        self.handler_page(P)

    def filter_url(self, url: URL) -> bool:
        return True

    def custom_handler_page(self, page):
        pass

    def handler_page(self, page):
        self.custom_handler_page(page)
        for _U in filter(self.filter_url, page.get_next_urls()):
            if _U.url not in self.seen:
                self.seen.add(_U.url)
                self.handler_page(URLExt(_U).do_http())
