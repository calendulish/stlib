#!/usr/bin/env python
#
# Lara Maia <dev@lara.monster> 2015 ~ 2022
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

from stlib import client
from tests import requires_manual_testing


@requires_manual_testing
def test_game_server() -> None:
    with client.SteamGameServer() as game_server:
        assert isinstance(game_server, steamworks.SteamGameServer)

        server_time = server.get_server_time()
        assert isinstance(server_time, int)
        assert len(str(server_time)) == 10

    game_server = client.SteamGameServer()
    server_time = game_server.get_server_time()
    assert isinstance(server_time, int)
    assert len(str(server_time)) == 10
    game_server.shutdown()


@requires_manual_testing
def test_steam_api_executor(debug) -> None:
    with client.SteamAPIExecutor() as steam_api:
        assert isinstance(steam_api, steamworks.SteamAPI)
        debug("SteamAPIExecutor started", wait_for=6)

        steamid = steam_api.get_steamid()
        assert isinstance(steamid, int)
        assert len(str(steamid)) == 17

    debug("SteamAPIExecutor shutdown", wait_for=6)

    executor = client.SteamApiExecutor()
    debug("SteamAPIExecutor manually started", wait_for=6)

    steamid = executor.steam_api.get_steamid()
    assert isinstance(steamid, int)
    assert len(str(steamid)) == 17

    executor.shutdown()
    debug("SteamAPIExecutor manually shutdown", wait_for=6)
