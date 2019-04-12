## Install

`pip3 install simple-crawler`

Set environment `AUTO_CHARSET=1` to pass `bytes` to beautifulsoup4 and let it detect the charset.

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
