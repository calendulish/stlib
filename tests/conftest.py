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

import pytest
import pytest_asyncio

from stlib import webapi, universe, community
from . import do_login, config, config_file, debug

debug("authenticating user", 0)
loop = asyncio.new_event_loop()
login_task = loop.create_task(do_login())
loop.run_until_complete(login_task)


def pytest_assertion_pass(item, lineno, orig, expl):
    print(f"{item}:{lineno} -> {orig} resolves to {expl}")


@pytest_asyncio.fixture(scope='session')
def event_loop():
    try:
        yield loop
    finally:
        loop.close()


@pytest.fixture(scope='session')
def steamid() -> universe.SteamId:
    return universe.generate_steamid(config.get('Test', 'steamid'))


@pytest.fixture(scope='session')
def access_token() -> str:
    return config.get('Test', 'access_token')


@pytest.fixture(scope='session')
def shared_secret() -> str:
    return config.get('Test', 'shared_secret')


@pytest.fixture(scope='session')
def revocation_code() -> str:
    return config.get('Test', 'revocation_code')


# noinspection PyShadowingNames, PyUnusedLocal
@pytest_asyncio.fixture(scope='module')
async def community_session() -> community.Community:
    try:
        community_session_ = await community.Community.new_session(0)
    except IndexError:
        community_session_ = community.Community.get_session(0)

    return community_session_


# noinspection PyShadowingNames, PyUnusedLocal
@pytest_asyncio.fixture(scope='module')
async def webapi_session(community_session) -> webapi.SteamWebAPI:
    try:
        api_key = await community_session.get_api_key()
    except PermissionError:
        api_key = ''

    try:
        webapi_session_ = await webapi.SteamWebAPI.new_session(0, api_key=api_key)
    except IndexError:
        webapi_session_ = webapi.SteamWebAPI.get_session(0)

    return webapi_session_
