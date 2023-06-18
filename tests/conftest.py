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

import asyncio
import codecs
import configparser
import os
from pathlib import Path

import pytest
import pytest_asyncio

from stlib import login, webapi, universe, community

config_file = Path(__file__).parent.resolve() / 'conftest.ini'
parser = configparser.RawConfigParser()

if os.getenv("GITHUB_ACTIONS"):
    parser.add_section('Test')
    parser.set('Test', 'steamid', os.getenv("steamid"))
    parser.set('Test', 'account_name', os.getenv("account_name"))
    parser.set('Test', 'password_raw', os.getenv("password_raw"))
    parser.set('Test', 'shared_secret', os.getenv("shared_secret"))
    parser.set('Test', 'identity_secret', os.getenv("identity_secret"))
    parser.set('Test', 'api_key', os.getenv("api_key"))
    parser.set('Test', 'token', "0")
    parser.set('Test', 'token_secure', "0")
    parser.set('Test', 'oauth_token', "0")

    with open(config_file, 'w', encoding="utf8") as config_file_object:
        parser.write(config_file_object)

parser.read(config_file)


def pytest_assertion_pass(item, lineno, orig, expl):
    print(f"{item}:{lineno} -> {orig} resolves to {expl}")


@pytest_asyncio.fixture(scope='session')
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    try:
        yield loop
    finally:
        loop.close()


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

        try:
            login_session.password = parser.get('Test', 'password_raw')
        except configparser.NoOptionError:
            encrypted_pass = parser.get('Test', 'password')
            key = codecs.decode(encrypted_pass, 'rot13')
            raw = codecs.decode(key.encode(), 'base64')
            login_session.password = raw.decode()

        login_data = await login_session.do_login(shared_secret, mobile_login=True)

        if login_data.oauth:
            parser.set('Test', 'token', login_data.oauth['wgtoken'])
            parser.set('Test', 'token_secure', login_data.oauth['wgtoken_secure'])
            parser.set('Test', 'oauth_token', login_data.oauth['oauth_token'])
        else:
            parser.set('Test', 'token', login_data.auth['transfer_parameters']['webcookie'])
            parser.set('Test', 'token_secure', login_data.auth['transfer_parameters']['token_secure'])

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
