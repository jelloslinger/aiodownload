"""aiodownload

This module contains the core classes.
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
    """A container class holding properties related to the URL.

    :class:`AioDownloadBundle`s get utilized by :class:`AioDownload`.  They
    hold information about the state of a bundle as they are processed.

    :param url: URL string (ex. https://www.google.com)
    :type url: str
    :param info: (optional) extra information that can be injected into the bundle
    :type info: dict
    :param params: (optional) params for a POST request
    :type params: dict
    """

    def __init__(self, url, info=None, params=None):

        self.file_path = None  # determined by DownloadStrategy.url_transform
        self.info = info
        self.num_tries = 0  # value to be incremented by AioDownload when a request is attempted
        self.params = params
        self.url = url
        self._status_msg = STATUS_INIT  # set by AioDownload depending of the where it is in the flow of execution

    @property
    def status_msg(self):
        return '[URL: {}, File Path: {}, Attempts: {}, Status: {}]'.format(
            self.url, self.file_path, self.num_tries, self._status_msg
        )


class AioDownload:
    """The core class responsible for the coordination of requests and downloads

    :param client: (optional) client session, a default is instantiated if not provided
    :type client: :class:`aiohttp.ClientSession`
    :param download_strategy: (optional) download strategy, a default is instantiated if not provided
    :type download_strategy: :class:`aiodownload.DownloadStrategy`
    :param request_strategy: (optional) request strategy, a :class:`Lenient` strategy is instantiated if not provided
    :type request_strategy: :class:`aiodownload.RequestStrategy`
    """

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
        """Main entry point for task creation with an asyncio event loop.

        The number of concurrent requests is throttled using this async
        method.  Depending on the download strategy used, the method will call
        the request_and_download async method or immediately return the bundle
        indicating that the file came from cache as the file existed.

        :param bundle: bundle (generally one that has just been instantiated)
        :type bundle: :class:`aiodownload.AioDownloadBundle

        :return: bundle with updated properties reflecting it's final state
        :rtype bundle: :class:`aiodownload.AioDownloadBundle
        """

        with (await self._main_semaphore):

            bundle.file_path = self._download_strategy.get_file_path(bundle)
            file_exists = os.path.isfile(bundle.file_path)

            if not (file_exists and self._download_strategy.skip_cached):

                while bundle._status_msg in (STATUS_ATTEMPT, STATUS_INIT, ):

                    if bundle._status_msg == STATUS_ATTEMPT:
                        logger.info(bundle.status_msg)

                    sleep_time = self._request_strategy.get_sleep_time(bundle)
                    logger.debug('Sleeping {} seconds between requests'.format(sleep_time))
                    await asyncio.sleep(sleep_time)

                    bundle = await self.request_and_download(bundle)

            else:

                bundle._status_msg = STATUS_CACHE

            logger.info(bundle.status_msg)

        return bundle

    async def request_and_download(self, bundle):
        """Make an HTTP request and write it to disk.  Use the download and
        request strategies of the instance to implement how this is achieved.

        :param bundle: bundle with it's url and file_path set
        :type bundle: :class:`aiodownload.AioDownloadBundle

        :return: bundle with updated properties reflecting success or failure
        :rtype bundle: :class:`aiodownload.AioDownloadBundle
        """

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
