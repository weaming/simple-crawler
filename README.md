## Install

`pip3 install simple-crawler`

Set environment `AUTO_CHARSET=1` to pass `bytes` to beautifulsoup4 and let it detect the charset.

## Classes

* `URL`: define a URL
* `URLExt`: class to handle `URL`
* `Page`: define a request result of a `URL`
    * `url`: type `URL`
    * `content`, `text`, `json`: response content properties from library `requests`
    * `type`: the response body type, is a enum which allows `BYTES`, `TEXT`, `HTML`, `JSON`
    * `is_html`: check whether is html accorrding to the response headers's `Content-Type`
    * `soup`: `BeautifulSoup` contains html if `is_html`
* `Crawler`: schedule the crawler by calling `handler_page()` recusively

## Example

```
from simple_crawler import *


class MyCrawler(Crawler):
    name = 'output.txt'
    aysnc def custom_handle_page(self, page):
        print(page.url)
        tags = page.soup.select("#container")
        tag = tags and tags[0]
        with open(self.name, 'a') as f:
            f.write(tag.text)
        # do some async call

    def filter_url(self, url: URL) -> bool:
        return url.url.startswith("https://xxx.com/xxx")


loop = get_event_loop(True)
c = MyCrawler("https://xxx.com/xxx", loop, concurrency=10)
schedule_future_in_loop(c.start(), loop=loop)
```

## TODO

* [x] Speed up using async or threading
