from aiodownload import AioDownloadBundle, AioDownload
import asyncio


def one(url_or_bundle, download=None):

    return swarm([url_or_bundle], download=download)[0]


def swarm(iterable, download=None):

    return [e for e in each(iterable, download=download)]


def each(iterable, url_map=None, download=None):

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
