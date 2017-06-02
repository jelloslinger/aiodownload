import os

from aiodownload.util import clean_filename, make_dirs, default_url_transform


def test_clean_filename():

    sanitized_filename = clean_filename('français.txt')

    assert sanitized_filename == 'francais.txt'


def test_make_dirs(tmpdir):

    test_path = os.path.sep.join([tmpdir.strpath, 'test', 'make', 'dir'])
    make_dirs(os.path.sep.join([test_path, 'mock.txt']))

    assert os.path.isdir(test_path)


def test_default_url_transformation():

    transformed_url = default_url_transform('https://httpbin.org/drip?duration=5&numbytes=5&code=200')

    assert transformed_url == os.path.sep.join(['httpbin.org', 'drip_duration_5-numbytes_5-code_200'])
