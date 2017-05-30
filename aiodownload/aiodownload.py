"""aiodownload

The purpose of this package is to asynchronously download content via HTTP and
write it to disk.

TODO - insert usage
"""

import aiohttp
import asyncio
import logging
import os

from .strategy import DownloadStrategy, Lenient

logger = logging.getLogger(__name__)

STATUS_ATTEMPT = 'Download attempted'
STATUS_CACHE = 'Cache hit'
STATUS_DONE = 'File written'
STATUS_FAIL = 'Download failed'
STATUS_INIT = 'Initialized'


class AioDownloadBundle:
    def __init__(self, url, info=None, params=None):

        self.file_path = None
        self.info = info
        self.num_tries = 0
        self.params = params
        self.url = url
        self._status_msg = STATUS_INIT

    @property
    def status_msg(self):
        return '[URL: {}, File Path: {}, Attempts: {}, Status: {}]'.format(
            self.url, self.file_path, self.num_tries, self._status_msg
        )


class AioDownload:
    def __init__(self, client=None, download_strategy=None, request_strategy=None):

        if not client:
            # Get the event loop and initialize a client session if not provided
            self.loop = asyncio.get_event_loop()
            self.client = aiohttp.ClientSession(loop=self.loop)
        else:
            # Or grab the event loop from the client session
            self.loop = client._loop
            self.client = client

        # Configuration objects managing download and request strategies
        self._download_strategy = download_strategy or DownloadStrategy()  # chunk_size, concurrent, home, skip_cached
        self._request_strategy = request_strategy or Lenient()  # max_time, max_tries, timeout

        # Bounded semaphore guards how many requests can run concurrently
        self._main_semaphore = asyncio.BoundedSemaphore(self._download_strategy.concurrent)

    async def main(self, bundle):

        with (await self._main_semaphore):

            bundle.file_path = self._download_strategy.get_file_path(bundle)
            file_exists = os.path.isfile(bundle.file_path)

            if not (file_exists and self._download_strategy.skip_cached):

                while bundle._status_msg in (STATUS_ATTEMPT, STATUS_INIT, ):

                    if bundle._status_msg == STATUS_ATTEMPT:
                        logger.info(bundle.status_msg)

                    sleep_time = self._request_strategy.get_sleep_time(bundle)
                    logger.debug('Sleeping {0} seconds between requests'.format(sleep_time))
                    await asyncio.sleep(sleep_time)

                    bundle = await self.request_and_download(bundle)

            else:

                bundle._status_msg = STATUS_CACHE

            logger.info(bundle.status_msg)

        return bundle

    async def request_and_download(self, bundle):

        with aiohttp.Timeout(self._request_strategy.timeout):

            try:

                bundle.num_tries += 1

                client_method = getattr(self.client, 'post' if bundle.params else 'get')
                async with client_method(bundle.url) as response:

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


class AioDownloadException(Exception):
    pass
