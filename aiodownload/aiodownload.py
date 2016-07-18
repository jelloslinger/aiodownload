# -*- coding: utf-8 -*-

import aiohttp
import asyncio
from concurrent.futures import ProcessPoolExecutor
import logging
import os

from .strategy import DownloadStrategy, Lenient

logger = logging.getLogger(__name__)

STATUS_ATTEMPT = 'Download attempted'
STATUS_CACHE = 'Cache hit'
STATUS_DONE = 'File written'
STATUS_FAIL = 'Download failed'
STATUS_INIT = 'Initialized'


class AioDownloadBundle(object):

    def __init__(self, url, info=None):

        self.file_path = None
        self.info = info
        self.num_tries = 0
        self.url = url
        self._status_msg = STATUS_INIT

    @property
    def status_msg(self):
        return '[URL: {0}, File Path: {1}, Attempts: {2}, Status: {3}]'.format(
            self.url,
            self.file_path,
            self.num_tries,
            self._status_msg
        )


class AioDownload(object):

    def __init__(self, loop=None, client=None, concurrent=2, max_workers=1, download_strategy=None, request_strategy=None):

        self._loop = loop or asyncio.get_event_loop()
        self._client = client or aiohttp.ClientSession(loop=self._loop)

        # Bounded semaphores guard how many main and process methods proceed
        self._main_semaphore = asyncio.BoundedSemaphore(concurrent)        # maximum concurrent aiohttp connections
        self._process_semaphore = asyncio.BoundedSemaphore(max_workers)    # maximum number of file_path processors

        # Configuration objects managing download and request strategies
        self._download_strategy = download_strategy or DownloadStrategy()  # properties: chunk_size, home, skip_cached
        self._request_strategy = request_strategy or Lenient()             # properties: max_time, max_tries, timeout

    async def main(self, bundle):

        with (await self._main_semaphore):

            bundle.file_path = self._download_strategy.get_file_path(bundle.url)
            file_exists = os.path.isfile(bundle.file_path)

            if not (file_exists and self._download_strategy.skip_cached):

                while bundle._status_msg in (STATUS_ATTEMPT, STATUS_INIT, ):

                    if bundle._status_msg == STATUS_ATTEMPT:
                        logger.info(bundle.status_msg)

                    sleep_time = self._request_strategy.get_sleep_time(bundle.num_tries)
                    logger.debug('Sleeping {0} seconds between requests'.format(sleep_time))
                    await asyncio.sleep(sleep_time)

                    bundle = await self.get_and_write(bundle)

            else:

                bundle._status_msg = STATUS_CACHE

            logger.info(bundle.status_msg)
            process = self._loop.create_task(self._process(bundle))

        await process
        return bundle

    async def get_and_write(self, bundle):

        with aiohttp.Timeout(self._request_strategy.timeout):

            try:

                bundle.num_tries += 1
                async with self._client.get(bundle.url) as response:

                    try:

                        self._request_strategy.assert_response(response)
                        await self._download_strategy.on_success(response, bundle)
                        bundle._status_msg = STATUS_DONE

                    except AssertionError:

                        if self._request_strategy.retry(response):

                            if bundle.num_tries == self._request_strategy.max_tries:

                                await self._download_strategy.on_fail(bundle)
                                bundle._status_msg = STATUS_FAIL

                            else:

                                bundle._status_msg = STATUS_ATTEMPT

                        else:

                            await self._download_strategy.on_fail(bundle)
                            bundle._status_msg = STATUS_FAIL

            except ValueError as err:

                bundle._status_msg = STATUS_FAIL
                logger.warn(' '.join([bundle.status_msg, str(err)]))

        return bundle

    async def _process(self, bundle):

        with (await self._process_semaphore):
            with ProcessPoolExecutor():
                try:
                    result = self.process(bundle)
                except NotImplementedError as err:
                    result = None
                    logger.debug(str(err))

        return result

    def get_bundled_tasks(self, urls):
        return [
            self._loop.create_task(self.main(AioDownloadBundle(url)))
            for url in urls
        ]

    def process(self, bundle):

        msg = (
            'A process method has not been implemented.  Developers may '
            'inherit {0} and implement this method to process a file returned '
            'from a download.  No action taken on {1}.'
        ).format(self.__class__.__name__, bundle.file_path)
        raise NotImplementedError(msg)


class AioDownloadException(Exception):
    pass
