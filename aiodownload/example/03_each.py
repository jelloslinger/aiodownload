import aiodownload
from aiodownload.example import logger


class Example:

    def __init__(self, number, flag):
        self.number = number
        self.flag = flag


def main():
    examples = [Example(i, True if i % 2 == 0 else False) for i in range(0, 5)]
    url_map = lambda x: 'https://httpbin.org/links/{}'.format(x.number)

    for bundle in aiodownload.each(examples, url_map=url_map):

        if bundle.info.flag:

            logger.info(bundle.status_msg + ' Flag is True')

            # Do some type of processing on this bundle

        else:

            logger.warning(bundle.status_msg + ' Flag is False')

            # Do some alternate type of processing on this bundle


if __name__ == '__main__':
    main()
