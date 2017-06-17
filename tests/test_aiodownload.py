from aiohttp import ClientSession
from aiodownload.aiodownload import STATUS_INIT, AioDownload


def test_aiodownloadbundle(bundle):
    default_status_msg = '[URL: {url}, File Path: {file_path}, Attempts: {attempts}, Status: {status}]'.format(**{
        'url': bundle.url,
        'file_path': bundle.file_path,
        'attempts': 0,
        'status': STATUS_INIT
    })
    assert bundle.status_msg == default_status_msg


def test_aiodownload_init_client():

    download = AioDownload(client=ClientSession())

    assert isinstance(download.client, ClientSession)


def test_aiodownload_init_strategy(download_strategy, request_strategy):

    download = AioDownload(download_strategy=download_strategy, request_strategy=request_strategy)

    assert download._download_strategy.chunk_size == download_strategy.chunk_size
    assert download._download_strategy.home == download_strategy.home
    assert download._download_strategy.skip_cached == download_strategy.skip_cached

    assert download._request_strategy.concurrent == request_strategy.concurrent
    assert download._request_strategy.max_attempts == request_strategy.max_attempts
    assert download._request_strategy.timeout == request_strategy.timeout


# Running the following test below raises the following error:

# >               async with client_method(bundle.url) as response:
# E               AttributeError: __aexit__
#
# ..\aiodownload\aiodownload.py:140: AttributeError

# Looks like there are no straight forward approaches to patching objects
# that require async magic method support.  Relevant conversations:
# http://bugs.python.org/issue26467
# https://github.com/Martiusweb/asynctest/issues/29

# from unittest.mock import patch
#
# from aiohttp import ClientSession
# from aiohttp.web import Response
# import pytest
#
# from aiodownload import AioDownload, AioDownloadBundle
#
#
# @pytest.fixture
# async def get_response():
#     return Response(body='all the data')
#
#
# @pytest.mark.asyncio
# async def test_download(event_loop):
#
#     with patch.object(ClientSession, 'get', return_value=get_response) as patched_get:
#
#         with patch.object(patched_get, '_loop', return_value=event_loop) as patched_client:
#
#             download = AioDownload(client=patched_client)
#             bundle = await download.main(AioDownloadBundle('http://test.example.com'))
#
#             assert True       # TODO - make assertions against the bundle
