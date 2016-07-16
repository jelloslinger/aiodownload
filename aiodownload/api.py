# -*- coding: utf-8 -*-

from aiodownload import AioDownloadBundle, AioDownload
import asyncio


def one(url, loop=None):

    return [file_path for file_path in swarm([url], loop=loop)][0]


def swarm(urls, loop=None):

    for e in each(urls, lambda x: str(x), loop=loop):
        yield e[1]


def each(iterable, url_map, loop=None):

    event_loop = loop or asyncio.get_event_loop()

    try:

        download = AioDownload(event_loop)
        tasks = [
            event_loop.create_task(
                download.main(AioDownloadBundle(url_map(i), info=i))
            ) for i in iterable
        ]
        for task_set in event_loop.run_until_complete(asyncio.wait(tasks)):
            for task in task_set:
                info, file_path = task.result()
                yield info, file_path

    finally:

        event_loop.close()
