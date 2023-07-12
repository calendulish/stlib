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

import asyncio
import configparser
import inspect
import os
import time
from pathlib import Path
from typing import Optional

import pytest

MANUAL_TESTING = int(os.environ.get('MANUAL_TESTING', 0))
LIMITED_ACCOUNT = int(os.environ.get('LIMITED_ACCOUNT', 0))

requires_manual_testing = pytest.mark.skipif(MANUAL_TESTING == False,  # noqa
                                             reason="This test can't run without MANUAL_TESTING")

requires_unlimited_account = pytest.mark.skipif(LIMITED_ACCOUNT == True,  # noqa
                                                reason="This test ccan't run using a limited account")

config_file = Path(__file__).parent.resolve() / 'conftest.ini'
parser = configparser.RawConfigParser()


def debug(msg: Optional[str] = None, wait_for: int = 5) -> None:
    if MANUAL_TESTING:
        current_frame = inspect.currentframe()
        outer_frame = inspect.getouterframes(current_frame, 2)

        if msg:
            print(f'   -> {outer_frame[1][3]}:{msg}')
            time.sleep(wait_for)
        else:
            print('\n')


async def wait_sms_code():
    debug("waiting sms code")

    while True:
        parser.read(config_file)
        sms_code = parser.get('Test', 'sms_code')

        if len(sms_code) == 5:
            break

        await asyncio.sleep(2)

    return sms_code


async def wait_mail_code():
    debug("waiting mail code")

    while True:
        parser.read(config_file)
        mail_code = parser.get('Test', 'mail_code')

        if len(mail_code) == 5:
            break

        await asyncio.sleep(2)

    return mail_code
