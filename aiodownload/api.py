"""Public API Functions

This module contains the public API functions.  The goal is to gain the
benefits of asynchronous HTTP requests while dropping one of these functions
into a synchronous code flow.  For basic usage, no prior knowledge of
asynchronous programming or asyncio is required.  Simply import aiodownload
and call the functions with some URLs.
"""

import asyncio

from . import AioDownloadBundle, AioDownload


def one(url_or_bundle, download=None):
    """Make one HTTP request and download it

    :param url_or_bundle: a URL string or bundle
    :type url_or_bundle: str or :class:`AioDownloadBundle`
    :param download: (optional) your own customized download object
    :type download: :class:`AioDownload`
    :return: a bundle
    :rtype: :class:`AioDownloadBundle`
    """

    return swarm([url_or_bundle], download=download)[0]


def swarm(iterable, download=None):
    """Make a swarm of requests and download them

    :param iterable: an iterable object (ex. list of URL strings)
    :type iterable: iterable object
    :param download: (optional) your own customized download object
    :type download: :class:`AioDownload`
    :return: a list of bundles
    :rtype: list
    """

    return [e for e in each(iterable, download=download)]


def each(iterable, url_map=None, download=None):
    """For each iterable object, map it to a URL and request asynchronously

    :param iterable: an iterable object (ex. list of objects)
    :type iterable: iterable object
    :param url_map: (optional) callable object mapping an object to a url or bundle
    :type url_map: callable object
    :param download: (optional) your own customized download object
    :type download: :class:`AioDownload`
    :return: generator
    """

    download = download or AioDownload()
    url_map = url_map or (lambda x: str(x))

    tasks = []
    for i in iterable:

        bundle = url_map(i)
        if not isinstance(bundle, AioDownloadBundle):
            bundle = AioDownloadBundle(bundle)

        if i != bundle.url:
            bundle.info = i

        tasks.append(download.loop.create_task(download.main(bundle)))

    for task_set in download.loop.run_until_complete(asyncio.wait(tasks)):
        for task in task_set:
            yield task.result()

    download.client.close()
