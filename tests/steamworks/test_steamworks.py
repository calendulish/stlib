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

from stlib import steamworks
from tests import requires_manual_testing


@requires_manual_testing
def test_steam_api(debug) -> None:
    print(debug)
    return
    steam_api = steamworks.SteamAPI(480)
    debug("SteamAPI started", wait_for=6)
    assert isinstance(steam_api, steamworks.SteamAPI)

    result = steam_api.is_steam_running()
    assert isinstance(result, bool)

    result = steam_api.restart_app_if_necessary(70)
    assert isinstance(result, bool)

    steam_api.shutdown()
    debug("SteamAPI shutdown", wait_for=6)


@requires_manual_testing
def test_steam_gameserver() -> None:
    steam_gameserver = steamworks.SteamGameServer(480, 0, 0)
    assert isinstance(steam_gameserver, steamworks.SteamGameServer)

    steamid = steam_gameserver.get_steamid()
    assert isinstance(steamid, int)
    assert len(str(steamid)) == 17

    steam_gameserver.shutdown()
