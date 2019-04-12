from typing import List
import re
import os
import asyncio
import logging
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup

version = "1.0"
GET = "GET"
POST = "POST"


class CrawlerException(Exception):
    pass


class HTTPError(CrawlerException):
    def __init__(self, status, value=None):
        self.status = status
        self.value = value
        super(HTTPError, self).__init__(f"{self.status}: {repr(self.value)[:200]}")


async def get_url_text(
    url,
    params=None,
    data=None,
    json=False,
    binary=False,
    method=GET,
    include_response=False,
    session: aiohttp.ClientSession = None,
):
    session.get
    allowed_methods = [GET, POST]
    assert method in allowed_methods, f"method must in {allowed_methods}"
    res = await getattr(session, method.lower())(url, params=params, data=data)
    err = None if res.status == 200 else res.status_code

    value = (
        await res.json() if json else (await res.read() if binary else await res.text())
    )
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
        referer=None,  # type: URL
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
    json = None  # type: list or dict
    type = str  # enum: BYTES, TEXT, HTML, JSON
    is_html = False

    url_regexp = re.compile(
        r"(https?|ftp|file)://[-A-Za-z0-9\+&@#/%?=~_|!:,.;]*[-A-Za-z0-9\+&@#/%=~_|]"
    )

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
                x["href"]
                if x["href"].startswith("http")
                else urljoin(self.url.url, x["href"])
                for x in links
                if x.has_attr("href") and not x["href"].startswith("javascript")
            ]
            return [URL(x) for x in urls]
        return []


class URLExt:
    url = None

    def __init__(self, url: URL):
        self.url = url

    async def do_http(self, session: aiohttp.ClientSession) -> Page:
        url = self.url
        (err, value, res) = await get_url_text(
            url.url,
            params=url.params,
            data=url.data,
            json=url.is_json,
            binary=os.getenv("AUTO_CHARSET") or url.is_binary,
            method=url.method,
            include_response=True,
            session=session,
        )
        if err:
            raise HTTPError(err, value)
        is_html = res.headers["content-type"] == "text/html"
        page = Page(url, value, is_html=is_html)
        return page


class Crawler:
    def __init__(self, start_url, loop, concurrency=10):
        self.start_url = start_url
        self.seen = set()

        self.page_queue = asyncio.Queue()
        self.session = aiohttp.ClientSession()

        self.concurrency = concurrency
        self.loop = loop

    async def start(self):
        U = URLExt(URL(self.start_url))
        P = await U.do_http(self.session)
        await self.handle_page(P)

        workers = [
            self.loop.create_task(self.worker(i)) for i in range(self.concurrency)
        ]
        await self.page_queue.join()
        for w in workers:
            w.cancel()
        await self.close()

    def filter_url(self, url: URL) -> bool:
        return True

    def custom_handle_page(self, page):
        pass

    async def async_custom_handle_page(self, page):
        pass

    async def worker(self, id):
        logging.debug(f"starting worker {id}")
        try:
            while True:
                page = await self.page_queue.get()
                await self.handle_page(page)
                self.page_queue.task_done()
        except asyncio.CancelledError:
            pass

    async def handle_page(self, page):
        await self.custom_handle_page(page)
        for _U in filter(self.filter_url, page.get_next_urls()):
            if _U.url not in self.seen:
                self.seen.add(_U.url)
                await self.page_queue.put(await URLExt(_U).do_http(self.session))

    async def close(self):
        await self.session.close()


# async event loop


def get_event_loop(not_running=False):
    try:
        loop = asyncio.get_event_loop()
        if not_running and loop.is_running():
            return asyncio.new_event_loop()
    except Exception as e:
        logging.warning(f"exception in get_event_loop: {e}, will create new one")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def schedule_future_in_loop(future, loop=None):
    if not loop:
        loop = get_event_loop(not_running=True)
    result = loop.run_until_complete(future)
    return result
