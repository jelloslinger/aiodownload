# -*- coding: utf-8 -*-

from aiodownload import AioDownloadBundle, AioDownload
import asyncio


def one(url, loop=None):

    return [s for s in swarm([url], loop=loop)][0]


def swarm(urls, loop=None):

    return [e for e in each(urls, loop=loop)]


def each(iterable, url_map=None, loop=None):

    url_map = url_map or _url_map

    event_loop = loop or asyncio.get_event_loop()

    download = AioDownload(event_loop)
    tasks = [
        event_loop.create_task(
            download.main(AioDownloadBundle(url_map(i), info=i))
        ) for i in iterable
    ]
    for task_set in event_loop.run_until_complete(asyncio.wait(tasks)):
        for task in task_set:
            yield task.result()


def _url_map(x):
    return str(x)

