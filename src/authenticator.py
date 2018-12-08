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

import base64
import hashlib
import hmac
import logging
from typing import Optional, Union

log = logging.getLogger(__name__)

__STEAM_ALPHABET = ['2', '3', '4', '5', '6', '7', '8', '9',
                    'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K',
                    'M', 'N', 'P', 'Q', 'R', 'T', 'V', 'W',
                    'X', 'Y']


def get_code(server_time: int, shared_secret: Union[str, bytes]) -> str:
    msg = int(server_time / 30).to_bytes(8, 'big')
    key = base64.b64decode(shared_secret)
    auth = hmac.new(key, msg, hashlib.sha1)
    digest = auth.digest()
    start = digest[19] & 0xF
    code = digest[start:start + 4]
    auth_code_raw = int.from_bytes(code, byteorder='big') & 0x7FFFFFFF

    auth_code = []
    for _ in range(5):
        auth_code.append(__STEAM_ALPHABET[int(auth_code_raw % len(__STEAM_ALPHABET))])
        auth_code_raw //= len(__STEAM_ALPHABET)

    return ''.join(auth_code)


def generate_device_id(identity_secret: Optional[str] = None, token: Optional[str] = None) -> str:
    if identity_secret:
        data = identity_secret.encode()
    elif token:
        data = token.encode()
    else:
        raise AttributeError("You must provide at least one argument")

    digest = hashlib.sha1(data).hexdigest()
    device_id = ['android:']

    for start, end in ([0, 8], [8, 12], [12, 16], [16, 20], [20, 32]):
        device_id.append(digest[start:end])
        device_id.append('-')

    device_id.pop(-1)
    return ''.join(device_id)
