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

import asyncio
import configparser
from pathlib import Path

import pytest
import pytest_asyncio

from stlib import login, webapi, universe, community

config_file = Path(__file__).parent.resolve() / 'conftest.ini'
parser = configparser.RawConfigParser()
parser.read(config_file)


def pytest_assertion_pass(item, lineno, orig, expl):
    print(f"{item}:{lineno} -> {orig} resolves to {expl}")


@pytest_asyncio.fixture(scope='session')
def event_loop():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.new_event_loop()


@pytest.fixture(scope='session')
def steamid() -> universe.SteamId:
    steamid_ = universe.generate_steamid(parser.get('Test', 'steamid'))
    return steamid_

@pytest.fixture(scope='session')
def oauth_token() -> str:
    oauth_token_ = parser.get('Test', 'oauth_token')
    return oauth_token_


# noinspection PyShadowingNames
@pytest_asyncio.fixture(scope='session')
async def do_login(steamid) -> None:
    token = parser.get('Test', 'token')
    token_secure = parser.get('Test', 'token_secure')
    shared_secret = parser.get('Test', 'shared_secret')

    try:
        login_session = await login.Login.new_session(0)
    except IndexError:
        login_session = login.Login.get_session(0)

    login_session.restore_login(steamid, token, token_secure)

    if not await login_session.is_logged_in(steamid):
        login_session.username = parser.get('Test', 'account_name')
        login_session.password = parser.get('Test', 'password_raw')

        login_data = await login_session.do_login(shared_secret, mobile_login=True)
        parser.set('Test', 'token', login_data.oauth['wgtoken'])
        parser.set('Test', 'token_secure', login_data.oauth['wgtoken_secure'])
        parser.set('Test', 'oauth_token', login_data.oauth['oauth_token'])

        with open(config_file, 'w', encoding="utf8") as config_file_object:
            parser.write(config_file_object)

    return None


# noinspection PyShadowingNames, PyUnusedLocal
@pytest_asyncio.fixture(scope='module')
async def community_session(do_login) -> community.Community:
    try:
        community_session_ = await community.Community.new_session(0)
    except IndexError:
        community_session_ = community.Community.get_session(0)

    return community_session_


# noinspection PyShadowingNames, PyUnusedLocal
@pytest_asyncio.fixture(scope='module')
async def webapi_session(do_login, community_session) -> webapi.SteamWebAPI:
    api_key = await community_session.get_api_key()

    try:
        webapi_session_ = await webapi.SteamWebAPI.new_session(0, api_key=api_key)
    except IndexError:
        webapi_session_ = webapi.SteamWebAPI.get_session(0)

    return webapi_session_
