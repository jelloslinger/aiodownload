# -*- coding: utf-8 -*-

from aiodownload import AioDownloadBundle, AioDownload
import asyncio


def one(url, download=None):

    return [s for s in swarm([url], download=download)][0]


def swarm(urls, download=None):

    return [e for e in each(urls, download=download)]


def each(iterable, url_map=None, download=None):

    url_map = url_map or _url_map
    download = download or AioDownload()

    tasks = []
    for i in iterable:
        url = url_map(i)
        info = None if i == url else i
        tasks.append(
            download._loop.create_task(
                download.main(AioDownloadBundle(url, info=info))
            )
        )

    for task_set in download._loop.run_until_complete(asyncio.wait(tasks)):
        for task in task_set:
            yield task.result()


def _url_map(x):
    return str(x)

