from aiohttp import web
import pytest

from aiodownload import AioDownloadBundle, BackOff, DownloadStrategy, Lenient, RequestStrategy


@pytest.fixture
def download_strategy(tmpdir):
    return DownloadStrategy(home=tmpdir.strpath)


@pytest.fixture
def request_strategy():
    return RequestStrategy()


@pytest.fixture
def lenient():
    return Lenient()


@pytest.fixture
def back_off():
    return BackOff()


@pytest.fixture
def bundle(download_strategy):
    bundle = AioDownloadBundle('http://test.example.com/get-some-data')
    bundle.file_path = download_strategy.get_file_path(bundle)
    return bundle


@pytest.fixture
def response_ok():
    return web.Response(**{'status': 200})


@pytest.fixture
def response_not_found():
    return web.Response(**{'status': 404})
