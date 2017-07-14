import aiodownload
from aiodownload.example import logger


def main():
    bundle = aiodownload.one('http://httpbin.org/get')

    logger.info(bundle.status_msg)


if __name__ == '__main__':
    main()
