import steam_api

from stlib import client
from tests import debug, requires_steam_api


@requires_steam_api
def test_init() -> None:
    debug('Instantiating Executor', wait_for=3)
    executor = client.SteamApiExecutor()
    debug('Running Init', wait_for=3)
    result = executor.init()
    debug(f'init_return:{result}')
    executor.shutdown()
    debug("It must be stopped now", wait_for=8)
    assert isinstance(result, bool)


@requires_steam_api
def test_steam_utils() -> None:
    debug('Instantiating Executor', wait_for=3)
    with client.SteamApiExecutor() as executor:
        debug('Calling SteamUtils', wait_for=3)
        steam_utils = executor.call(steam_api.SteamUtils)
        debug('Calling get_server_time')
        result = executor.call(steam_utils.get_server_time)
        debug(f'process_return:{result}')
        assert isinstance(result, int)
    debug("It must be stopped now", wait_for=8)
