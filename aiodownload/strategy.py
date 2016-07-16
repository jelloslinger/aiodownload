# -*- coding: utf-8 -*-

import os


class DownloadStrategy(object):
    """DownloadStrategy is an injection class for AioDownload.  The purpose is
    to control download options for AioDownload.
    """

    def __init__(self, chunk_size=65536, home=None, skip_cached=False):
        self.chunk_size = chunk_size
        self.home = home or os.path.abspath(os.sep)
        self.skip_cached = skip_cached

    def get_file_path(self, url):
        # TODO - cleanse the file_path
        return self.home + self.url_transform(url)

    @staticmethod
    def url_transform(url):
        # TODO - this could be tighter
        return os.path.sep.join(url.split('/')[2:])


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
