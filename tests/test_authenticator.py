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
# noinspection PyPackageRequirements
import pytest
import sys

from stlib import authenticator


def get_event_loop() -> asyncio.AbstractEventLoop:
    if sys.platform == 'win32':
        return asyncio.ProactorEventLoop()  # on windows IO needs this
    return asyncio.new_event_loop()  # default on UNIX is fine


@pytest.yield_fixture()
def event_loop():
    """pytest-asyncio customization"""
    if sys.platform != "win32":
        asyncio.set_event_loop(None)  # see https://github.com/pytest-dev/pytest-asyncio/issues/73
    loop = get_event_loop()
    if sys.platform != "win32":
        # on UNIX we also need to attach the loop to the child watcher for asyncio.subprocess
        policy = asyncio.get_event_loop_policy()
        watcher = asyncio.SafeChildWatcher()
        watcher.attach_loop(loop)
        policy.set_child_watcher(watcher)
    try:
        yield loop
    finally:
        loop.close()


# noinspection PyProtectedMember
class TestAuthenticator:
    adb = authenticator.AndroidDebugBridge(os.path.join('C:\\', 'platform-tools', 'adb.exe'),
                                           '/data/data/com.valvesoftware.android.steam.community/')

    @pytest.mark.asyncio
    async def test__do_checks(self):
        for field in authenticator.Checks._fields:
            assert getattr(authenticator.CHECKS_RESULT, field) == False

        await self.adb._do_checks()

        for field in authenticator.Checks._fields:
            assert getattr(authenticator.CHECKS_RESULT, field) == True

    @pytest.mark.asyncio
    async def test__run(self):
        result = await self.adb._run(['shell', 'echo', 'hello'])
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test__get_data(self):
        result = await self.adb._get_data('shared_prefs/steam.uuid.xml')
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_get_secret(self):
        tasks = [
            self.adb.get_secret('shared'),
            self.adb.get_secret('identity'),
            self.adb.get_secret('dummy'),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert isinstance(results[0], (str, bytes))
        assert isinstance(results[1], (str, bytes))
        assert isinstance(results[2], KeyError)
