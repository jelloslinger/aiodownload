# -*- coding: utf-8 -*-

import aiohttp
import asyncio
import errno
import logging
import os

from .strategy import Lenient

logger = logging.getLogger(__name__)

STATUS_ATTEMPT = 'Download attempted'
STATUS_CACHE = 'Cache hit'
STATUS_DONE = 'File written'
STATUS_FAIL = 'Download failed'
STATUS_INIT = 'Initialized'


class AioDownloadBundle(object):

    def __init__(self, url, info=None):

        self.info = info
        self.num_tries = 0
        self.url = url
        self._status_msg = STATUS_INIT

    @property
    def status_msg(self):
        return '[URL: {0}, Attempts: {1}, Status: {2}]'.format(
            self.url,
            self.num_tries,
            self._status_msg
        )


class AioDownload(object):

    CONFIG = {
        'concurrent': 2,
        'home': os.path.abspath(os.sep),
        'request_strategy': Lenient(),
        'skip_cached': False,
        'timeout': 60,
        'url_transform': lambda x: os.path.sep.join(x.split('/')[2:])
    }
    CHUNK_SIZE = 65536

    def __init__(
        self,
        loop,
        client,
        concurrent=None,
        home=None,
        request_strategy=None,
        skip_cached=None,
        timeout=None,
        url_transform=None
    ):

        self._loop = loop
        self._client = client
        self._home = home or AioDownload.CONFIG['home']
        self._request_strategy = request_strategy or AioDownload.CONFIG['request_strategy']

        _concurrent = concurrent or AioDownload.CONFIG['concurrent']
        self._semaphore = asyncio.Semaphore(_concurrent)

        self._skip_cached = skip_cached or AioDownload.CONFIG['skip_cached']
        self._timeout = timeout or AioDownload.CONFIG['timeout']
        self._url_transform = url_transform or AioDownload.CONFIG['url_transform']

    async def _main(self, bundle):

        with (await self._semaphore):

            file_path = self._home + self._url_transform(bundle.url)
            file_exists = os.path.isfile(file_path)

            if not (file_exists and self._skip_cached):

                while bundle._status_msg in (STATUS_ATTEMPT, STATUS_INIT, ):

                    if bundle._status_msg == STATUS_ATTEMPT:
                        logger.info(bundle.status_msg)

                    sleep_time = self._request_strategy.get_sleep_time(bundle.num_tries)
                    logger.debug('Sleeping {0} seconds between requests'.format(sleep_time))
                    await asyncio.sleep(sleep_time)

                    bundle = await self._get_and_write(bundle, file_path)

            else:

                bundle._status_msg = STATUS_CACHE

            logger.info(bundle.status_msg)

    async def _get_and_write(self, bundle, file_path):

        with aiohttp.Timeout(self._timeout):

            async with self._client.get(bundle.url) as response:

                try:

                    self._request_strategy.assert_response(response)

                    try:
                        os.makedirs(os.path.dirname(file_path))
                    except OSError as exc:  # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise

                    # TODO - more checking around write path?
                    with open(file_path, 'wb+') as f:
                        while True:
                            chunk = await response.content.read(AioDownload.CHUNK_SIZE)
                            if not chunk:
                                break
                            f.write(chunk)

                    bundle._status_msg = STATUS_DONE

                except AssertionError:

                    if self._request_strategy.retry(response):

                        bundle.num_tries += 1

                        if bundle.num_tries == self._request_strategy.max_tries:
                            open(file_path, 'wb+').close()
                            bundle._status_msg = STATUS_FAIL
                        else:
                            bundle._status_msg = STATUS_ATTEMPT

                    else:

                        open(file_path, 'wb+').close()
                        bundle._status_msg = STATUS_FAIL

        return bundle


class AioDownloadException(Exception):
    pass
