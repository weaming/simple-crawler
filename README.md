## Install

`pip3 install simple-crawler`

Set environment `AUTO_CHARSET=1` to pass `bytes` to beautifulsoup4 and let it detect the charset.

## Classes

* `URL`: define a URL
* `URLExt`: object to handle `URL`
* `Page`: request result of a `URL`
    * `url`: type `URL`
    * `content`, `text`, `json`: response content properties from library `requests`
    * `type`: the response body type, is a enum which allows `BYTES`, `TEXT`, `HTML`, `JSON`
    * `is_html`: check whether is html accorrding to the response headers's `Content-Type`
* `Crawler`: schedule the crawler by calling `handler_page()` recusively

## Example

```
from simple_crawler import *


class MyCrawler(Crawler):
    name = 'output.txt'
    def custom_handler_page(self, page):
        print(page.url)
        tags = page.soup.select("#nr1")
        tag = tags and tags[0]
        with open(self.name, 'a') as f:
            f.write(tag.text)
        print(tag.text)

    def filter_url(self, url: URL) -> bool:
        return url.url.startswith("https://xxx.com/xxx")


c = MyCrawler("https://xxx.com/xxx")
c.start()
```

## TODO

* [ ] Speed up using async or threading
