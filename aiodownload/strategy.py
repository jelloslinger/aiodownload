# -*- coding: utf-8 -*-


class RequestStrategy(object):
    """RequestStrategy is an injection class for AioDownload.  The purpose is
    to control how AioDownload performs requests and retry requests.
    """

    def __init__(self, max_time=0, max_tries=0):
        self.max_tries = max_tries
        self._max_time = max_time

    def assert_response(self, response):
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
