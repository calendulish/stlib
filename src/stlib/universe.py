#!/usr/bin/env python
#
# Lara Maia <dev@lara.monster> 2015 ~ 2024
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

"""
`universe` interface is a low level interface that imitate structure
and functionality from internal SteamAPI universe. The main use of this
interface is to generate necessary parameters to other stlib interfaces
"""

import base64
import hashlib
import hmac
import locale
import logging
from functools import total_ordering
from typing import NamedTuple, Type, Self, Tuple

import rsa

log = logging.getLogger(__name__)

__STEAM_ALPHABET = ['2', '3', '4', '5', '6', '7', '8', '9',
                    'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K',
                    'M', 'N', 'P', 'Q', 'R', 'T', 'V', 'W',
                    'X', 'Y']

STEAM_UNIVERSE = {
    'public': 'DE45CD61',
    'private': '7DC60112',
    'alpha': 'E77327FA',
}

TOKEN_TYPE = {
    'none': 0,
    'mobileapp': 1,
    'thirdparty': 2,
}


class SteamKey(NamedTuple):
    key: rsa.PublicKey
    """Steam key"""
    timestamp: int
    """Timestamp"""


class SteamId(NamedTuple):
    """Conversible steam ID"""
    type: int
    """Account type"""
    id: int
    """Account ID"""

    @classmethod
    def id_base(cls) -> int:
        """Base ID used to generate steam ID"""
        return 76561197960265728

    @property
    def id3(self) -> int:
        """Steam ID3"""
        return (self.id + self.type) * 2 - self.type

    @property
    def id64(self) -> int:
        """Steam ID64"""
        return self.id_base() + (self.id * 2) + self.type

    @property
    def id_string(self) -> str:
        """Steam ID as string"""
        return f"STEAM_0:{self.type}:{self.id}"

    @property
    def id3_string(self) -> str:
        """Steam ID3 as string"""
        return f"[U:1:{self.id3}]"

    @property
    def profile_url(self) -> str:
        """Profile url"""
        return f'https://steamcommunity.com/profiles/{self.id64}'


@total_ordering
class SteamPrice:
    def __init__(self, price: float) -> None:
        """Create a SteamPrice Object"""
        self._price = price

    def __add__(self, value: int | float) -> 'SteamPrice':
        return SteamPrice(round(self._price + value, 2))

    def __sub__(self, value: int | float) -> 'SteamPrice':
        return SteamPrice(round(self._price - value, 2))

    def __lt__(self, other: Self) -> bool:
        return self._price < other._price

    def __eq__(self, other: Self) -> bool:
        return self._price == other._price

    @staticmethod
    def __calc_fee(price: int) -> Tuple[int, int]:
        return max(int(price * 0.10), 1), max(int(price * 0.05), 1)

    @staticmethod
    def __calc_fee_inverse(price: int) -> Tuple[int, int]:
        return max(int(price // 23), 1), max(int(price // 11.5), 1)

    def __calc_price_offset(self, price: int) -> Tuple[int, int]:
        fee = sum(self.__calc_fee_inverse(price))
        fee_inverse = sum(self.__calc_fee(price - fee))
        fixed_price = price

        while (price - fee) + fee_inverse != price:
            fixed_price -= 1
            fee = sum(self.__calc_fee_inverse(fixed_price))
            fee_inverse = sum(self.__calc_fee(fixed_price - fee))

            if (price - fee) + fee_inverse == fixed_price:
                break

        return fixed_price, fee

    @staticmethod
    def __check_language() -> None:
        if not locale.getlocale(locale.LC_MONETARY)[0]:
            locale_info = locale.getlocale()
            locale.setlocale(locale.LC_MONETARY, f"{locale_info[0]}.{locale_info[1]}")

    @staticmethod
    def get_language() -> str:
        """Get current language used to show monetary price"""
        lang_info = locale.getlocale(locale.LC_MONETARY)
        return f"{lang_info[0]}.{lang_info[1]}"

    @staticmethod
    def set_language(value: str) -> None:
        """Set the language used to show monetary price"""
        locale.setlocale(locale.LC_MONETARY, value)

    @property
    def fees_as_integer(self) -> Tuple[int, int]:
        """Return fees as integer"""
        return self.__calc_fee(self.as_integer)

    @property
    def fees(self) -> Tuple[float, float]:
        """Return fees"""
        steam_fee, developer_fee = self.fees_as_integer
        return round(steam_fee / 100, 2), round(developer_fee / 100, 2)

    @property
    def with_fees_subtracted(self) -> float:
        """Return price with fees subtracted"""
        fixed_price, fee = self.__calc_price_offset(self.as_integer)

        return round((fixed_price - fee) / 100, 2)

    @property
    def with_fees_added(self) -> float:
        """Return price with fees added"""
        return self._price + sum(self.fees)

    @property
    def as_float(self) -> float:
        """Return price as float type"""
        return self._price

    @property
    def as_integer(self) -> int:
        """Return price as integer type for compatibility with some Steam APIs"""
        return round(self._price * 100)

    @property
    def as_integer_with_fees_added(self) -> int:
        """Return price as integer type with fees added"""
        return round(self.with_fees_added * 100)

    @property
    def as_integer_with_fees_subtracted(self) -> int:
        """Return price as integer type with fees subtracted"""
        return round(self.with_fees_subtracted * 100)

    @property
    def as_monetary_string(self) -> str:
        """Return price as monetary string"""
        self.__check_language()
        return locale.currency(self._price)

    @property
    def as_monetary_string_with_fees_added(self) -> str:
        """Return price as monetary string with fees added"""
        self.__check_language()
        return locale.currency(self.with_fees_added)

    @property
    def as_monetary_string_with_fees_subtracted(self) -> str:
        """Return price as monetary string with fees removed"""
        self.__check_language()
        return locale.currency(self.with_fees_subtracted)

    @classmethod
    def new_from_integer(cls: Type[Self], price: int) -> Self:
        """Create an instance using integer price returned by some Steam APIs"""
        return cls(round(price / 100, 2))

    @classmethod
    def new_from_monetary_price(cls: Type[Self], price: str) -> Self:
        """Create an instance using monetary price"""
        no_comma = price.replace(',', '.')
        price_list = no_comma.split('.')
        big = ''.join(char for char in price_list[0] if char.isdigit())
        minor = ''.join(char for char in price_list[1] if char.isdigit())
        price_float = float(f'{big}.{minor}')

        return cls(price_float)


def generate_otp_code(msg: bytes, key: bytes) -> int:
    """
    Generate OTP code
    :param msg: offset
    :param key: seed
    :return: OTP
    """
    auth = hmac.new(key, msg, hashlib.sha1)
    digest = auth.digest()
    start = digest[19] & 0xF
    code = digest[start:start + 4]

    return int.from_bytes(code, byteorder='big') & 0x7FFFFFFF


def generate_otp_seed(shared_secret: str | bytes) -> str:
    """
    Generate OTP seed from user shared secret
    :param shared_secret: User shared secret
    :return: seed
    """
    key = base64.b64decode(shared_secret)
    return base64.b32encode(key).decode()


# noinspection PyUnboundLocalVariable
def generate_steamid(steamid: str | int) -> SteamId:
    """
    Generate `SteamId` from any steam ID string or number
    :param steamid: Any steam ID format as string or number
    :return: `SteamId`
    """
    if isinstance(steamid, str):
        steamid_parts = steamid.strip('[]').split(':')

        if steamid_parts[0][:5] == 'STEAM':
            type_ = int(steamid_parts[1])
            id_ = int(steamid_parts[2])
        elif steamid_parts[0][0] == 'U':
            type_ = 0 if int(steamid_parts[2]) % 2 == 0 else 1
            id_ = int((int(steamid_parts[2]) - type_) / 2)
        elif steamid.isdigit() and len(steamid) == 17:
            steamid = int(steamid)
        else:
            raise ValueError('Invalid steamid')

    if isinstance(steamid, int):
        offset = steamid - SteamId.id_base()
        type_ = 0 if offset % 2 == 0 else 1
        id_ = int((offset - type_) / 2)

    return SteamId(type_, id_)


def generate_steam_code(server_time: int, shared_secret: str | bytes) -> str:
    """
    Generate steam code
    :param server_time: Server Time
    :param shared_secret: User shared secret
    :return: Steam OTP
    """
    msg = (server_time // 30).to_bytes(8, 'big')
    key = base64.b64decode(shared_secret)
    auth_code_raw = generate_otp_code(msg, key)

    auth_code = []
    for _ in range(5):
        auth_code.append(__STEAM_ALPHABET[int(auth_code_raw % len(__STEAM_ALPHABET))])
        auth_code_raw //= len(__STEAM_ALPHABET)

    return ''.join(auth_code)


def generate_device_id(base: str) -> str:
    """
    Generate device ID from base string
    :param base: Base string
    :return: Device ID
    """
    digest = hashlib.sha256(base.encode()).hexdigest()
    device_id = ['android:']

    for start, end in ([0, 8], [8, 12], [12, 16], [16, 20], [20, 32]):
        device_id.extend((digest[start:end], '-'))
    device_id.pop(-1)
    return ''.join(device_id)


def generate_time_hash(server_time: int, tag: str, secret: str) -> str:
    """Generate steam time hash"""
    key = base64.b64decode(secret)
    msg = server_time.to_bytes(8, 'big') + tag.encode()
    auth = hmac.new(key, msg, hashlib.sha1)
    code = base64.b64encode(auth.digest())

    return code.decode()


def encrypt_password(steam_key: SteamKey, password: str) -> bytes:
    """
    Encrypt user password
    :param steam_key: `SteamKey`
    :param password: Raw user password
    :return: Encrypted password
    """
    encrypted_password = rsa.encrypt(password.encode(), steam_key.key)

    return base64.b64encode(encrypted_password)
