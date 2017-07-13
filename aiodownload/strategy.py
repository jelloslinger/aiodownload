"""Strategies

This module contains base class and sensible default class implementations
for the request and download strategies used by :class:`AioDownload`
"""

import logging
import os

from .util import default_url_transform, make_dirs

logger = logging.getLogger(__name__)


class DownloadStrategy:
    """DownloadStrategy is an injection class for AioDownload.  The purpose is
    to control download options for AioDownload.

    :param chunk_size: the incremental chunk size to read from the response
    :type chunk_size: (optional) int
    :param home: the base file path to use for writing response content to file
    :type honme: (optional) str
    :param skip_cached: indicates whether existing written files should be skipped
    :type skip_cached: bool
    """

    def __init__(self, chunk_size=65536, home=None, skip_cached=False):
        self.chunk_size = chunk_size
        self.home = home or os.getcwd()
        self.skip_cached = skip_cached

    async def on_fail(self, bundle):
        """Write an empty file

        :param bundle: bundle (file_path should exist)
        :type bundle: :class:`AioDownloadBundle`

        :return: None
        """

        make_dirs(bundle.file_path)
        open(bundle.file_path, 'wb+').close()

    async def on_success(self, response, bundle):
        """Write the response to the file path indicated in the bundle

        :param response: successful response from an HTTP response
        :type response: :class:`aiohttp.ClientResponse`
        :param bundle: bundle (file_path should exist)
        :type bundle: :class:`AioDownloadBundle`

        :return: None
        """

        make_dirs(bundle.file_path)

        with open(bundle.file_path, 'wb+') as f:
            while True:
                chunk = await response.content.read(self.chunk_size)
                if not chunk:
                    break
                f.write(chunk)

    def get_file_path(self, bundle):
        """Get the file path for the bundle

        :param bundle: bundle (generally, it's file_path should be None)
        :type bundle: :class:`AioDownloadBundle`

        :return: full file_path for the bundle (via the default URL transformation)
        :rtype: str
        """

        return os.path.sep.join([
            self.home,
            default_url_transform(bundle.url)       # transforms the URL into a relative file path
        ])


class RequestStrategy:
    """RequestStrategy is an injection class for AioDownload.  The purpose is
    to control how AioDownload performs requests and retries requests.

    :param concurrent: the number of concurrent asynchronous HTTP requests to maintain
    :type concurrent: (optional) int
    :param max_attempts: maximum number of attempts before giving up
    :type max_attempts: int
    :param time_out: timeout for the client session
    :type time_out: int
    """

    def __init__(self, concurrent=2, max_attempts=0, timeout=60):
        self.concurrent = concurrent
        self.max_attempts = max_attempts
        self.timeout = timeout

    def assert_response(self, response):
        """Assertion for the response

        :param response: response from an HTTP response
        :type response: :class:`aiohttp.ClientResponse`
        :return: None or AssertionError
        """

        assert response.status < 400

    def retry(self, response):
        """Retry the HTTP request based on the response

        :param response: response from an HTTP response
        :type response: :class:`aiohttp.ClientResponse`

        :return:
        :rtype: bool
        """

        return False

    def get_sleep_time(self, bundle):
        """Returns how much time the bundle should sleep based on it's properties

        :param bundle: bundle
        :type bundle: :class:`AioDownloadBundle`

        :return: sleep time
        :rtype: int
        """

        return -1


class Lenient(RequestStrategy):
    """Lenient request strategy designed for an average web server.  Try five
    times with a minute between each retry.
    """

    def __init__(self, max_attempts=5):
        RequestStrategy.__init__(self, max_attempts)

    def retry(self, response):
        """Retry any unsuccessful HTTP response except a 404 (if they say
        it's not there, let's believe them)
        """

        return False if response.status == 404 else True

    def get_sleep_time(self, bundle):

        # Retry pattern: 0.25, 60, 60, 60, 60
        return 0.25 if bundle.attempts == 0 else 60


class BackOff(RequestStrategy):
    """Back Off request strategy designed for APIs and web servers that can
    be hammered a little harder.  Exponentially back away if a failed
    response is returned.
    """

    def __init__(self, max_attempts=10):
        RequestStrategy.__init__(self, max_attempts)

    def get_sleep_time(self, bundle):

        # Retry pattern: 0.25, 0.5, 1, 2, 4, 8, 16, 32, 60, 60
        return min(2**(bundle.attempts - 2), 60)
