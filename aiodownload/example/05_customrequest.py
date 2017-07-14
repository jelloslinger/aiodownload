from random import randint

import aiodownload
from aiodownload import AioDownload, RequestStrategy
from aiodownload.example import logger


class Random(RequestStrategy):
    """Random request strategy with maximum of 5 attempts
    """

    def __init__(self, max_attempts=5):
        super().__init__(max_attempts=max_attempts)

    def assert_response(self, response):
        """Only accept 200 responses
        """
        assert response.status == 200

    def retry(self, response):
        """Only retry 400 responses
        """
        return True if response.status == 400 else False

    def get_sleep_time(self, bundle):
        return randint(1, 10)


def main():
    download = AioDownload(request_strategy=Random())
    urls = ['https://httpbin.org/status/{}'.format(i) for i in range(200, 500, 100)]

    for bundle in aiodownload.swarm(urls, download=download):
        logger.info(bundle.status_msg)


if __name__ == '__main__':
    main()
