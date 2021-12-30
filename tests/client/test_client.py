#!/usr/bin/env python
#
# Lara Maia <dev@lara.monster> 2015 ~ 2021
#
# The stlib is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# The stlib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#

import os

from stlib import client, steam_api

from tests import requires_manual_testing


@requires_manual_testing
def test_game_server() -> None:
    os.environ['SteamAppId'] = '480'
    init_return = steam_api.server_init(0, 0, 1)
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
def test_steam_api_executor(debug) -> None:
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
