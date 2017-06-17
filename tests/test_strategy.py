import os

import pytest
# from unittest.mock import MagicMock


@pytest.mark.asyncio
async def test_download_strategy_on_fail(bundle, download_strategy, tmpdir):
    fail_file_path = os.path.sep.join([tmpdir.strpath, 'test.example.com', 'get-some-data'])

    await download_strategy.on_fail(bundle)

    assert os.path.isfile(fail_file_path)

    with open(fail_file_path) as f:
        assert len(f.read()) == 0


# # Much like the test found in test_aiodownload.py, this seems to bonk as
# # a result of Mock objects not supporting async magic methods.
#
# @pytest.mark.asyncio
# async def test_download_strategy_on_success(bundle, download_strategy, tmpdir):
#
#     async def read_response(chunk_size=4096):
#         async with iter(b'all-the-data') as rr:
#             return rr
#
#     response = MagicMock(
#         content=MagicMock(
#             read=read_response
#         )
#     )
#     success_file_path = os.path.sep.join([tmpdir.strpath, 'test.example.com', 'get-some-data'])
#
#     await download_strategy.on_success(response, bundle)
#
#     assert os.path.isfile(success_file_path)
#
#     with open(success_file_path, 'rb') as f:
#
#         assert len(f.read()) > 0


def test_download_strategy_get_file_path(bundle, download_strategy, tmpdir):
    test_file_path = os.path.sep.join([tmpdir.strpath, 'test.example.com', 'get-some-data'])

    assert download_strategy.get_file_path(bundle) == test_file_path


def test_request_strategy_retry(request_strategy, response_ok):
    assert request_strategy.retry(response_ok) is False


def test_request_strategy_get_sleep_time(request_strategy, bundle):
    assert request_strategy.get_sleep_time(bundle) == -1


def test_lenient_assert_response_ok(lenient, response_ok):
    assert lenient.assert_response(response_ok) is None


def test_lenient_assert_response_not_found(lenient, response_not_found):
    with pytest.raises(AssertionError) as err:
        lenient.assert_response(response_not_found)


def test_lenient_retry_response_ok(lenient, response_ok):
    assert lenient.retry(response_ok) is True


def test_lenient_retry_not_found(lenient, response_not_found):
    assert lenient.retry(response_not_found) is False


def test_lenient_get_sleep_time(lenient, bundle):
    assert lenient.get_sleep_time(bundle) == 0.25

    for _ in range(0, 4):
        bundle.attempts += 1
        assert lenient.get_sleep_time(bundle) == 60


def test_back_off_get_sleep_time(back_off, bundle):
    expected_back_off_sequence = [0.25, 0.5, 1, 2, 4, 8, 16, 32, 60, 60]

    for i in range(0, len(expected_back_off_sequence)):
        assert back_off.get_sleep_time(bundle) == expected_back_off_sequence[i]
        bundle.attempts += 1
