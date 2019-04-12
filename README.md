## Example

```
from crawler import *


class MyCrawler(Crawler):
    name = 'output.txt'
    def custom_handler_page(self, page):
        print(page.url)
        tags = page.soup.select("#nr1")
        tag = tags and tags[0]
        with open(name, 'a') as f:
            f.write(tag.text)
        print(tag.text)

    def filter_url(self, url: URL) -> bool:
        return url.url.startswith("https://xxx.com/xxx")


c = MyCrawler("https://xxx.com/xxx")
c.start()
```
