#!/usr/bin/env python
#
# Lara Maia <dev@lara.monster> 2015 ~ 2023
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
from tests import requires_manual_testing, debug


@requires_manual_testing
def test_steam_api() -> None:
    steam_api = steamworks.SteamAPI(480)
    debug("SteamAPI started", wait_for=6)
    assert isinstance(steam_api, steamworks.SteamAPI)

    result = steam_api.is_steam_running()
    assert isinstance(result, bool)

    result = steam_api.restart_app_if_necessary(70)
    assert isinstance(result, bool)

    seconds = steam_api.get_seconds_since_app_active()
    assert isinstance(seconds, int)

    seconds = steam_api.get_seconds_since_computer_active()
    assert isinstance(seconds, int)

    universe = steam_api.get_connected_universe()
    assert isinstance(universe, int)
    assert len(str(universe)) == 1

    time = steam_api.get_server_real_time()
    assert isinstance(time, int)
    assert len(str(time)) == 10

    country = steam_api.get_ip_country()
    assert isinstance(country, str)
    assert len(country) == 2

    battery = steam_api.get_current_battery_power()
    assert isinstance(battery, int)
    assert (0 < battery < 100) or battery == 255

    appid = steam_api.get_appid()
    assert isinstance(appid, int)

    ipc_call = steam_api.get_ipc_call_count()
    assert isinstance(ipc_call, int)

    is_vr = steam_api.is_steam_running_in_vr()
    assert isinstance(is_vr, bool)

    is_big_picture = steam_api.is_steam_in_big_picture_mode()
    assert isinstance(is_big_picture, bool)

    is_china = steam_api.is_steam_china_launcher()
    assert isinstance(is_china, bool)

    is_steam_deck = steam_api.is_steam_running_on_steam_deck()
    assert isinstance(is_steam_deck, bool)

    steam_api.shutdown()
    debug("SteamAPI shutdown", wait_for=6)


@requires_manual_testing
def test_steam_gameserver() -> None:
    steam_gameserver = steamworks.SteamGameServer(480, 0, 0)
    assert isinstance(steam_gameserver, steamworks.SteamGameServer)

    steamid = steam_gameserver.get_steamid()
    assert isinstance(steamid, int)
    assert len(str(steamid)) == 17

    seconds = steam_gameserver.get_seconds_since_app_active()
    assert isinstance(seconds, int)

    seconds = steam_gameserver.get_seconds_since_computer_active()
    assert isinstance(seconds, int)

    universe = steam_gameserver.get_connected_universe()
    assert isinstance(universe, int)
    assert len(str(universe)) == 1

    time = steam_gameserver.get_server_real_time()
    assert isinstance(time, int)
    assert len(str(time)) == 10

    country = steam_gameserver.get_ip_country()
    assert isinstance(country, str)
    assert len(country) == 2

    battery = steam_gameserver.get_current_battery_power()
    assert isinstance(battery, int)
    assert (0 < battery < 100) or battery == 255

    appid = steam_gameserver.get_appid()
    assert isinstance(appid, int)

    ipc_call = steam_gameserver.get_ipc_call_count()
    assert isinstance(ipc_call, int)

    is_vr = steam_gameserver.is_steam_running_in_vr()
    assert isinstance(is_vr, bool)

    is_big_picture = steam_gameserver.is_steam_in_big_picture_mode()
    assert isinstance(is_big_picture, bool)

    is_china = steam_gameserver.is_steam_china_launcher()
    assert isinstance(is_china, bool)

    is_steam_deck = steam_gameserver.is_steam_running_on_steam_deck()
    assert isinstance(is_steam_deck, bool)

    steam_gameserver.shutdown()
