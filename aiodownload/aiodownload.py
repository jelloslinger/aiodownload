# -*- coding: utf-8 -*-

import aiohttp
import asyncio
from concurrent.futures import as_completed, ProcessPoolExecutor
import errno
import logging
import os

from .strategy import Lenient

logger = logging.getLogger(__name__)


class AioDownloadBundle(object):

    def __init__(self, url, processor='sink'):

        self.num_tries = 0
        self.processor = processor
        self.url = url
        self._priority = 100

    def __lt__(self, other):
        assert isinstance(other, AioDownloadBundle)
        if self._priority == other._priority:
            return self.url < other.url
        else:
            return self._priority < other.priority

    @property
    def priority(self):
        return self._priority - self.num_tries


class AioDownload(object):

    CONFIG = {
        'concurrent': 2,
        'home': os.path.abspath(os.sep),
        'max_workers': 2,
        'request_strategy': Lenient(),
        'skip_cached': False,
        'timeout': 60,
        'url_transform': lambda x: os.path.sep.join(x.split('/')[2:])
    }

    def __init__(
        self,
        client,
        concurrent=None,
        home=None,
        max_workers=None,
        request_strategy=None,
        skip_cached=None,
        timeout=None,
        url_transform=None
    ):

        self.priority_queue = asyncio.PriorityQueue()
        self._client = client
        self._concurrent = concurrent or AioDownload.CONFIG['concurrent']

        max_workers = max_workers or AioDownload.CONFIG['max_workers']
        self._file_pool = ProcessPoolExecutor(max_workers=max_workers)

        self._home = home or AioDownload.CONFIG['home']
        self._request_strategy = request_strategy or AioDownload.CONFIG['request_strategy']
        self._skip_cached = skip_cached or AioDownload.CONFIG['skip_cached']
        self._timeout = timeout or AioDownload.CONFIG['timeout']
        self._url_transform = url_transform or AioDownload.CONFIG['url_transform']

    async def get(self, url_bundle):

        with aiohttp.Timeout(self._timeout):

            pause_time = self._request_strategy.get_time(url_bundle.num_tries)
            if pause_time >= 0:

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

            priority, queue_url_bundle = await self.priority_queue.get()
            file_path = os.path.sep.join([self._home, self._url_transform(queue_url_bundle.url)])
            file_exists = os.path.isfile(file_path)

            if not file_exists:
                try:
                    os.makedirs(os.path.dirname(file_path))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            if not (file_exists and self._skip_cached):

                content = await self.get(queue_url_bundle) or b''
                with open(file_path, 'wb+') as f:
                    f.write(content)

                msg = 'File written'

            else:

                msg = 'Cache hit'

            logger.info('[Task #: {0}, URL: {1}, File: {2}] {3}'.format(task_id, queue_url_bundle.url, file_path, msg))

            processor = getattr(self, queue_url_bundle.processor)
            if processor:
                future_bundles = self._file_pool.submit(processor, file_path)
                as_completed(self._queue_future_bundles(future_bundles))

    def get_tasks(self, loop):

        return [
            loop.create_task(self.get_and_write(i))
            for i in range(self._concurrent)
        ]

    @staticmethod
    def sink(file_path):
        pass

    def _queue_future_bundles(self, future):
        future_bundles = future.result() or []
        for fb in future_bundles:
            self.priority_queue.put_nowait((fb.priority, fb, ))


class AioDownloadException(Exception):
    pass
