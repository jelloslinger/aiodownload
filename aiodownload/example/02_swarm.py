import aiodownload
from aiodownload.example import logger


def main():
    urls = ['https://httpbin.org/links/{}'.format(i) for i in range(0, 5)]

    for bundle in aiodownload.swarm(urls):
        logger.info(bundle.status_msg)


if __name__ == '__main__':
    main()
