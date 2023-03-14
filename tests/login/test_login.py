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


class TestLogin:
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

    # noinspection PyUnusedLocal
    async def test_is_logged_in(self, do_login, steamid) -> None:
        login_session = login.Login.get_session(0)
        is_logged_in = await login_session.is_logged_in(steamid)
        assert is_logged_in is True

        login_session = await login.Login.new_session(1)
        is_logged_in = await login_session.is_logged_in(steamid)
        assert is_logged_in is False

    async def test_session(self) -> None:
        login_session_1 = await login.Login.new_session(2)
        login_session_2 = await login.Login.new_session(3)

        try:
            await login.Login.new_session(0)
        except IndexError:
            pass

        login_session_3 = login.Login.get_session(2)
        login_session_4 = login.Login.get_session(3)
        login_session_5 = login.Login.get_session(2)

        try:
            login.Login.get_session(4)
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
