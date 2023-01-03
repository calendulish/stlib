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

from stlib import login
from tests import requires_manual_testing, MANUAL_TESTING


class TestLogin:
    if MANUAL_TESTING:
        config_parser = configparser.RawConfigParser()
        config_parser.read(os.path.join(os.path.dirname(__file__), '..', 'conftest.ini'))
        username = config_parser.get("Test", "username")
        password = config_parser.get("Test", "password")
        api_url = config_parser.get("Test", "api_url")
        api_key = config_parser.get("Test", "api_key")
        steamid_raw = config_parser.getint("Test", "steamid")

    @requires_manual_testing
    def test_login(self) -> None:
        # TODO
        pass

    def test_restore_login(self) -> None:
        # TODO
        pass

    def test_get_captcha(self) -> None:
        # TODO
        pass

    def test_get_steam_key(self) -> None:
        # TODO
        pass

    def test_has_phone(self) -> None:
        # TODO
        pass

    @requires_manual_testing
    async def test_is_logged_in(self) -> None:
        login_session = await login.Login.new_session(0)
        steamid = await universe.generate_steamid(steamid_raw)
        is_logged_in = await login_session.is_logged_in(steamid)
        assert is_logged_in is False

    async def test_session(self) -> None:
        login_session_1 = await login.Login.new_session(0)
        login_session_2 = await login.Login.new_session(1)

        try:
            await login.Login.new_session(0)
        except IndexError:
            pass

        login_session_3 = login.Login.get_session(0)
        login_session_4 = login.Login.get_session(1)
        login_session_5 = login.Login.get_session(0)

        try:
            login.Login.get_session(2)
        except IndexError:
            pass

        assert isinstance(login_session_1, login.Login)
        assert isinstance(login_session_2, login.Login)
        assert isinstance(login_session_3, login.Login)
        assert isinstance(login_session_4, login.Login)
        assert isinstance(login_session_5, login.Login)
        assert login_session_1 != login_session_2
        assert login_session_1 != login_session_4
        assert login_session_3 != login_session_4
        assert login_session_1 == login_session_3 == login_session_5
