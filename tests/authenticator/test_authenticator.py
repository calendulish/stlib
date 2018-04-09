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

import asyncio
import os

import pytest
from stlib import authenticator

# noinspection PyUnresolvedReferences
from tests import MANUAL_TESTING, debug, event_loop, requires_manual_testing


class TestAuthenticator:
    # noinspection PySimplifyBooleanCheck
    if MANUAL_TESTING == True:
        adb = authenticator.AndroidDebugBridge(os.path.join('C:\\', 'platform-tools', 'adb.exe'),
                                               '/data/data/com.valvesoftware.android.steam.community/')

    @requires_manual_testing
    @pytest.mark.asyncio
    async def test__do_checks(self) -> None:
        for field in authenticator.Checks._fields:
            assert getattr(authenticator.CHECKS_RESULT, field) == False

        await self.adb._do_checks()

        for field in authenticator.Checks._fields:
            assert getattr(authenticator.CHECKS_RESULT, field) == True

        debug(authenticator.CHECKS_RESULT)

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
    async def test_get_secret(self) -> None:
        tasks = [
            self.adb.get_secret('shared'),
            self.adb.get_secret('identity'),
            self.adb.get_secret('dummy'),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        debug(f'secrets: {results}')

        assert isinstance(results[0], (str, bytes))
        assert isinstance(results[1], (str, bytes))
        assert isinstance(results[2], KeyError)

    @requires_manual_testing
    @pytest.mark.asyncio
    async def test_get_code(self) -> None:
        secret = await self.adb.get_secret('shared')
        code = authenticator.get_code(secret)
        debug(f'result:{code}')
        assert isinstance(code, tuple)
        assert isinstance(code[0], list)
        assert isinstance(code[1], int)
        assert len(code[0]) == 5
        assert len(str(code[1])) == 10
