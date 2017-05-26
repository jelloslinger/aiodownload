import errno
import logging
import os
import string
import unicodedata
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class DownloadStrategy(object):
    """DownloadStrategy is an injection class for AioDownload.  The purpose is
    to control download options for AioDownload.
    """

    def __init__(self, chunk_size=65536, home=None, skip_cached=False):
        self.chunk_size = chunk_size
        self.home = home or os.getcwd()
        self.skip_cached = skip_cached

    async def on_fail(self, bundle):

        open(bundle.file_path, 'wb+').close()

    async def on_success(self, response, bundle):

        try:
            os.makedirs(os.path.dirname(bundle.file_path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

        with open(bundle.file_path, 'wb+') as f:
            while True:
                chunk = await response.content.read(self.chunk_size)
                if not chunk:
                    break
                f.write(chunk)

    def get_file_path(self, bundle):
        return os.path.sep.join([self.home, self.url_transform(bundle)])

    def url_transform(self, bundle):

        parsed_url = urlparse(bundle.url)

        path_segments = [
            self._clean_filename(path_segment)
            for path_segment in parsed_url.path.split('/')[1:]
        ]
        if not len(path_segments):
            path_segments = ['index']

        params = self._clean_filename(
            parsed_url.params.replace(';', '-').replace(',', '.').replace('=', '_')
        )
        if len(params):
            params = '(' + params + ')'

        query = self._clean_filename(
            parsed_url.query.replace('=', '_').replace('&', '-')
        )
        if len(query):
            query = '_' + query

        return os.path.sep.join([parsed_url.netloc] + path_segments) + params + query

    def _clean_filename(self, filename):

        return ''.join([
            c for c in unicodedata.normalize('NFKD', filename)
            if not unicodedata.combining(c) and c in '-_.() {0}{1}'.format(
                string.ascii_letters,
                string.digits
            )
        ])


class RequestStrategy(object):
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

    def __init__(self, max_time=2, max_tries=2):
        super(Lenient, self).__init__(max_time, max_tries)

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
        super(BackOff, self).__init__(max_time, max_tries)

    def get_sleep_time(self, num_tries):
        if num_tries < self.max_tries:
            return min(2**(num_tries-2), self._max_time)
        else:
            return -1
