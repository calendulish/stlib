import steam_api

import pytest

from stlib import client
from tests import debug, steam_api_available


@pytest.mark.skipif(steam_api_available() == False,
                    reason="steam_api is not available in currently environment")
def test_init():
    debug('Instantiating Executor', wait_for=3)
    executor = client.SteamApiExecutor()
    debug('Running Init', wait_for=3)
    result = executor.init()
    debug(f'init_return:{result}')
    executor.shutdown()
    debug("It must be stopped now", wait_for=8)
    assert isinstance(result, bool)


@pytest.mark.skipif(steam_api_available() == False,
                    reason="steam_api is not available in currently environment")
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
