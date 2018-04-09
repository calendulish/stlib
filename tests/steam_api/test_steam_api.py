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

from stlib import steam_api
from tests import requires_manual_testing


class TestSteamAPI:
    @requires_manual_testing
    def test__init(self) -> None:
        assert isinstance(steam_api.init(), bool)

    def test__is_steam_running(self) -> None:
        assert isinstance(steam_api._is_steam_running(), bool)

    def test_shutdown(self) -> None:
        steam_api.shutdown()
        assert True  # if shutdown doesn't throw an exception, it's ok
