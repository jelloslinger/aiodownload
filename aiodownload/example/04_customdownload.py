import os

import aiodownload
from aiodownload import AioDownload, DownloadStrategy
from aiodownload.example import logger


class MyDownloadStrategy(DownloadStrategy):
    """Save files in "Downloads" directory with filenames a.html, b.html, ... as processed.
    Also, skip files that have already been downloaded.
    """

    def __init__(self):
        super().__init__(skip_cached=True)
        self.home = os.path.sep.join([self.home, 'Downloads'])
        self.file_counter = 0

    def get_file_path(self, bundle):
        self.file_counter += 1
        return os.path.sep.join([
            self.home,
            chr(ord('a') + self.file_counter - 1) + '.html'
        ])


def main():
    download = AioDownload(download_strategy=MyDownloadStrategy())

    urls = ['https://httpbin.org/links/{}'.format(i) for i in range(0, 5)]

    for bundle in aiodownload.swarm(urls, download=download):
        logger.info(bundle.status_msg)


if __name__ == '__main__':
    main()
