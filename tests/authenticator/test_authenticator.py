#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015 ~ 2018
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

import configparser
import os

import pytest
from stlib import authenticator

# noinspection PyUnresolvedReferences
from tests import MANUAL_TESTING, debug, event_loop, requires_manual_testing


class TestAuthenticator:
    if MANUAL_TESTING:
        config_parser = configparser.RawConfigParser()
        config_parser.read(os.path.join(os.path.dirname(__file__), '..', 'conftest.ini'))
        adb_path = config_parser.get("Test", "adb_path")
        adb = authenticator.AndroidDebugBridge(adb_path)

    @requires_manual_testing
    @pytest.mark.asyncio
    async def test__do_checks(self) -> None:
        await self.adb._do_checks()
        assert True  # if _do_checks doesn't throw an exception, it's ok

    @requires_manual_testing
    @pytest.mark.asyncio
    async def test__run(self) -> None:
        result = await self.adb._run(['shell', 'echo', 'hello'])
        debug(f'process_return:{result}')
        assert result == 'hello'

    @requires_manual_testing
    @pytest.mark.asyncio
    async def test__get_data(self) -> None:
        result = await self.adb._get_data('shared_prefs/steam.uuid.xml')
        debug(f'data:{result}')
        assert isinstance(result, str)

    @requires_manual_testing
    @pytest.mark.asyncio
    async def test_get_secret(self) -> bool:
        secrets = await self.adb.get_json('shared_secret', 'identity_secret')

        debug(f'secrets: {secrets}')

        assert isinstance(secrets['shared_secret'], str)
        assert isinstance(secrets['identity_secret'], str)

        try:
            await self.adb.get_json('dummy_secret')
        except KeyError:
            pass
        else:
            return False

    @requires_manual_testing
    @pytest.mark.asyncio
    async def test_get_code(self) -> None:
        secret = await self.adb.get_json('shared_secret')
        code = authenticator.get_code(secret['shared_secret'])

        debug(f'result:{code}')

        assert isinstance(code, authenticator.AuthenticatorCode)

        assert isinstance(code.code, str)
        assert len(code.code) == 5

        assert isinstance(code.server_time, int)
        assert len(str(code.server_time)) == 10
