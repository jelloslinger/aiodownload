import logging
import os

from aiodownload.util import default_url_transform, make_dirs

logger = logging.getLogger(__name__)


class DownloadStrategy:
    """DownloadStrategy is an injection class for AioDownload.  The purpose is
    to control download options for AioDownload.
    """

    def __init__(self, chunk_size=65536, concurrent=2, home=None, skip_cached=False):
        self.chunk_size = chunk_size
        self.concurrent = concurrent
        self.home = home or os.getcwd()
        self.skip_cached = skip_cached

    async def on_fail(self, bundle):

        make_dirs(bundle.file_path)
        open(bundle.file_path, 'wb+').close()

    async def on_success(self, response, bundle):

        make_dirs(bundle.file_path)

        with open(bundle.file_path, 'wb+') as f:
            while True:
                chunk = await response.content.read(self.chunk_size)
                if not chunk:
                    break
                f.write(chunk)

    def get_file_path(self, bundle):

        return os.path.sep.join([
            self.home,
            default_url_transform(bundle.url)       # transforms the URL into a relative file path
        ])


class RequestStrategy:
    """RequestStrategy is an injection class for AioDownload.  The purpose is
    to control how AioDownload performs requests and retry requests.
    """

    def __init__(self, max_time=0, max_tries=0, timeout=60):
        self.max_tries = max_tries
        self.timeout = timeout
        self._max_time = max_time

    @staticmethod
    def assert_response(response):
        assert response.status < 400

    def retry(self, response):
        return False

    def get_sleep_time(self, num_tries):
        return -1


class Lenient(RequestStrategy):
    def __init__(self, max_time=60, max_tries=5):
        RequestStrategy.__init__(self, max_time, max_tries)

    def retry(self, response):
        if response.status == 404:
            return False
        return True

    def get_sleep_time(self, num_tries):
        if num_tries < self.max_tries:
            return self._max_time
        else:
            return -1


class BackOff(RequestStrategy):
    def __init__(self, max_time=60, max_tries=10):
        RequestStrategy.__init__(self, max_time, max_tries)

    def get_sleep_time(self, num_tries):
        if num_tries < self.max_tries:
            return min(2**(num_tries - 2), self._max_time)
        else:
            return -1
