import inspect
import steam_api
import time

import pytest

from stlib import client

MANUAL_TESTING = False


@pytest.fixture(autouse=True)
def debug(msg: str = None, wait_for: int = 5):
    if MANUAL_TESTING:
        current_frame = inspect.currentframe()
        outer_frame = inspect.getouterframes(current_frame, 2)

        if msg:
            print(f'   -> {outer_frame[1][3]}:{msg}')
            time.sleep(wait_for)
        else:
            print('\n')


def test_init():
    debug('Instantiating Executor', wait_for=3)
    executor = client.SteamApiExecutor()
    debug('Running Init', wait_for=3)
    result = executor.init()
    debug(f'init_return:{result}')
    executor.shutdown()
    debug("It must be stopped now", wait_for=8)
    assert isinstance(result, bool)


def test_steam_utils():
    debug('Instantiating Executor', wait_for=3)
    with client.SteamApiExecutor() as executor:
        debug('Calling SteamUtils', wait_for=3)
        steam_utils = executor.call(steam_api.SteamUtils)
        debug('Calling get_server_time')
        result = executor.call(steam_utils.get_server_time)
        debug(f'process_return:{result}')
        assert isinstance(result, int)
    debug("It must be stopped now", wait_for=8)
