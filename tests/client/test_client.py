import os

from stlib import client, steam_api

from tests import debug, requires_manual_testing


@requires_manual_testing
def test_server() -> None:
    os.environ['SteamAppId'] = '480'
    init_return = steam_api.server_init(0, 0, 0)
    assert isinstance(init_return, bool)
    assert init_return is True

    server = steam_api.SteamGameServer()
    assert isinstance(server, steam_api.SteamGameServer)

    steam_api.server_shutdown()
    os.environ.pop('SteamAppId')

    with client.SteamGameServer() as server:
        assert isinstance(server, steam_api.SteamGameServer)

        server_time = server.get_server_time()
        assert isinstance(server_time, int)
        assert len(str(server_time)) == 10

        steam_id = server.get_steam_id()
        assert isinstance(steam_id, int)
        assert len(str(steam_id)) == 17


@requires_manual_testing
def test_executor() -> None:
    debug('Instantiating Executor', wait_for=3)
    executor = client.SteamApiExecutor()
    assert isinstance(executor, client.SteamApiExecutor)

    debug('Running Init', wait_for=3)
    init_return = executor.init()
    debug(f'init_return:{init_return}')
    assert isinstance(init_return, bool)
    assert init_return is True

    executor.shutdown()
    debug("It must be stopped now", wait_for=6)

    debug('Initializing context manager for executor')
    with client.SteamApiExecutor() as executor:
        steam_utils = executor.call(steam_api.SteamUtils)
        assert isinstance(steam_utils, steam_api.SteamUtils)

        steam_user = executor.call(steam_api.SteamUser)
        assert isinstance(steam_user, steam_api.SteamUser)

        server_time = executor.call(steam_utils.get_server_time)
        assert isinstance(server_time, int)
        assert len(str(server_time)) == 10

        steam_id = executor.call(steam_user.get_steam_id)
        assert isinstance(steam_id, int)
        assert len(str(steam_id)) == 17

    debug("It must be stopped now", wait_for=6)
