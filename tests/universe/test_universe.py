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

import base64

import rsa

from stlib import universe


class TestUniverse:
    def test_generate_otp_code(self) -> None:
        otp_code = universe.generate_otp_code(b'A', b'A')
        assert isinstance(otp_code, int)
        assert len(str(otp_code)) == 10

    def test_generate_steam_code(self) -> None:
        steam_code = universe.generate_steam_code(0, 'AAAAAAAA')
        assert isinstance(steam_code, str)
        assert len(steam_code) == 5

        for character in steam_code:
            assert character in [
                '2', '3', '4', '5', '6', '7', '8', '9',
                'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K',
                'M', 'N', 'P', 'Q', 'R', 'T', 'V', 'W',
                'X', 'Y'
            ]

    def test_generate_device_id(self) -> None:
        device_id = universe.generate_device_id('A')
        assert isinstance(device_id, str)
        assert device_id.split(':')[0] == 'android'
        assert len(device_id.split('-')) == 5

    def test_generate_time_hash(self) -> None:
        time_hash = universe.generate_time_hash(0, 'A', 'AAAAAAAA')
        base64.b64decode(time_hash)

    def test_encrypt_password(self) -> None:
        public_key, private_key = rsa.newkeys(512)
        steam_key = universe.SteamKey(public_key, 0)
        password_encrypted = universe.encrypt_password(steam_key, '0000')

        assert isinstance(password_encrypted, bytes)
        password_encrypted_raw = base64.b64decode(password_encrypted)

        password = rsa.decrypt(password_encrypted_raw, private_key)
        assert password.decode() == '0000'
