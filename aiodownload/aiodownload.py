# -*- coding: utf-8 -*-

import aiohttp
import asyncio
import errno
import logging
import os

from .strategy import Lenient

logger = logging.getLogger(__name__)


class UrlBundle(object):

    def __init__(self, url):

        self.url = url
        self.num_tries = 0
        self._priority = 100

    def __lt__(self, other):
        assert isinstance(other, UrlBundle)
        return self.priority <= other.priority

    @property
    def priority(self):
        return self._priority - self.num_tries


class AioDownload(object):

    def __init__(self, client, concurrent=3, home=None, request_strategy=None, timeout=60, url_transform=None):

        self.priority_queue = asyncio.PriorityQueue()
        self._client = client
        self._concurrent = concurrent
        self._timeout = timeout

        if home is None:
            self._home = os.path.abspath(os.sep)
        else:
            self._home = home

        if request_strategy is None:
            self._request_strategy = Lenient()
        else:
            self._request_strategy = request_strategy

        if url_transform is None:
            self._url_transform = lambda url: os.path.sep.join(url.split('/')[2:])
        else:
            self._url_transform = url_transform

    async def get(self, url_bundle):

        with aiohttp.Timeout(self._timeout):

            pause_time = self._request_strategy.get_time(url_bundle.num_tries)
            if pause_time > 0:

                logger.debug('Pausing for {0} seconds between requests'.format(pause_time))
                await asyncio.sleep(pause_time)

                async with self._client.get(url_bundle.url) as response:

                    try:

                        self._request_strategy.assert_response(response)
                        return await response.read()

                    except AssertionError:

                        if self._request_strategy.retry(response):

                            url_bundle.num_tries += 1
                            self.priority_queue.put_nowait((url_bundle.priority, url_bundle))

                            retries_remaining = self._request_strategy.max_tries - url_bundle.num_tries
                            msg = '{0} more retries left before removal from queue'.format(retries_remaining)

                        else:

                            msg = 'Removed from queue'

                        logger.debug('[Response: {0}, URL: {1}] - {2}'.format(response.status, url_bundle.url, msg))

    async def get_and_write(self, task_id):

        while not self.priority_queue.empty():

            priority, queue_url = await self.priority_queue.get()

            logger.debug('[Task #: {0}, URL: {1}]'.format(task_id, queue_url.url))
            content = await self.get(queue_url)
            if content:

                file_path = self._home + os.path.sep + self._url_transform(queue_url.url)

                if not os.path.exists(os.path.dirname(file_path)):
                    try:
                        os.makedirs(os.path.dirname(file_path))
                    except OSError as exc:  # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise

                with open(file_path, 'wb+') as fd:
                    fd.write(content)

    def get_tasks(self, loop):
        return [
            loop.create_task(self.get_and_write(i))
            for i in range(self._concurrent)
        ]


class AioDownloadException(Exception):
    pass
