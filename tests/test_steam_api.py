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

import signal

import steam_api
from stlib import client


# noinspection PyProtectedMember

class TestSteamAPI():
    def test__init(self):
        assert isinstance(steam_api.init(), bool)

    def test_is_steam_running(self):
        assert isinstance(steam_api.is_steam_running(), bool)

    def test_shutdown(self):
        steam_api.shutdown()
        assert True # if shutdown doesn't throw an exception, it's ok


class TestOverlay():
    overlay = client.Overlay()

    def test_hook(self):
        assert self.overlay.process is None
        result = self.overlay.hook(269670)
        assert result
        assert isinstance(self.overlay.process.pid, int)
        assert self.overlay.process.exitcode is None
        assert self.overlay.process.is_alive

    def test_unhook(self):
        self.overlay.unhook()
        assert self.overlay.process.exitcode == -signal.SIGTERM
