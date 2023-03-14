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
import pytest

from stlib import universe, webapi, login
from tests import debug, LIMITED_ACCOUNT

if LIMITED_ACCOUNT:
    pytest.skip("requires unlimited account", allow_module_level=True)


async def test_server_time(webapi_session) -> None:
    server_time = await webapi_session.get_server_time()
    assert isinstance(server_time, int)
    assert len(str(server_time)) == 10


async def test_get_custom_profile_url(webapi_session, steamid) -> None:
    profile_url = await webapi_session.get_custom_profile_url(steamid)
    assert isinstance(profile_url, str)
    assert 'https://steamcommunity.com/id/' in profile_url
    debug(profile_url, wait_for=0)


async def test_get_steamid(webapi_session, steamid) -> None:
    profile_url = await webapi_session.get_custom_profile_url(steamid)
    steamid_2 = await webapi_session.get_steamid(profile_url)
    assert isinstance(steamid, universe.SteamId)
    assert steamid == steamid_2


async def test_get_personaname(webapi_session, steamid) -> None:
    persona = await webapi_session.get_personaname(steamid)
    isinstance(persona, str)
    debug(persona, wait_for=0)


async def test_get_owned_games(webapi_session, steamid) -> None:
    owned_games = await webapi_session.get_owned_games(steamid)
    assert isinstance(owned_games, list)
    assert all(isinstance(game, webapi.Game) for game in owned_games)

    owned_games_filtered = await webapi_session.get_owned_games(steamid, appids_filter=[220])
    assert isinstance(owned_games_filtered, list)
    assert all(isinstance(game, webapi.Game) for game in owned_games_filtered)
    debug(str(owned_games_filtered[0]), wait_for=0)


async def test_new_authenticator(webapi_session, steamid, oauth_token) -> None:
    login_data = webapi_session.new_authenticator(steamid, oauth_token)
    isinstance(login_data, login.LoginData)
    # TODO
