class CrawlerException(Exception):
    pass


class HTTPError(CrawlerException):
    def __init__(self, status, value=None):
        self.status = status
        self.value = value
        super(HTTPError, self).__init__(f"{self.status}: {repr(self.value)[:200]}")
