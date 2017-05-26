from aiodownload import AioDownloadBundle, AioDownload
import asyncio


def one(url_or_bundle, download=None):

    return [s for s in swarm([url_or_bundle], download=download)][0]


def swarm(iterable, download=None):

    return [e for e in each(iterable, download=download)]


def each(iterable, url_map=None, download=None):

    url_map = url_map or _url_map
    download = download or AioDownload()

    tasks = []
    for i in iterable:

        bundle = url_map(i)
        if i != bundle.url:
            bundle.info = i

        tasks.append(
            download._loop.create_task(
                download.main(bundle)
            )
        )

    for task_set in download._loop.run_until_complete(asyncio.wait(tasks)):
        for task in task_set:
            yield task.result()


def _url_map(x):

    if not isinstance(x, AioDownloadBundle):
        x = AioDownloadBundle(x)
    return x
