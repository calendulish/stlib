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

import steam_api

class TestSteamAPI():
    def test__init(self):
        assert isinstance(steam_api.init(), bool)

    def test_is_steam_running(self):
        assert isinstance(steam_api.is_steam_running(), bool)

    def test_shutdown(self):
        steam_api.shutdown()
        assert True  # if shutdown doesn't throw an exception, it's ok