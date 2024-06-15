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
import codecs
import configparser
import inspect
import os
import time
from pathlib import Path
from typing import Optional

import pytest
from stlib import login

MANUAL_TESTING = int(os.environ.get('MANUAL_TESTING', 0))
LIMITED_ACCOUNT = int(os.environ.get('LIMITED_ACCOUNT', 0))

requires_manual_testing = pytest.mark.skipif(MANUAL_TESTING == False,  # noqa
                                             reason="This test can't run without MANUAL_TESTING")

requires_unlimited_account = pytest.mark.skipif(LIMITED_ACCOUNT == True,  # noqa
                                                reason="This test ccan't run using a limited account")

config_file = Path(__file__).parent.resolve() / 'conftest.ini'
cookies_file = Path(__file__).parent.resolve() / 'cookiejar'
config = configparser.RawConfigParser()

if os.getenv("GITHUB_ACTIONS"):
    config.add_section('Test')
    config.set('Test', 'steamid', os.getenv("steamid"))
    config.set('Test', 'account_name', os.getenv("account_name"))
    config.set('Test', 'password_raw', os.getenv("password_raw"))
    config.set('Test', 'shared_secret', os.getenv("shared_secret"))
    config.set('Test', 'identity_secret', os.getenv("identity_secret"))
    config.set('Test', 'api_key', os.getenv("api_key"))

    with open(config_file, 'w', encoding="utf8") as config_file_object:
        config.write(config_file_object)

config.read(config_file)


async def do_login() -> None:
    shared_secret = config.get('Test', 'shared_secret')

    try:
        login_session = await login.Login.new_session(0)
    except IndexError:
        login_session = login.Login.get_session(0)

    if cookies_file.is_file():
        login_session.http_session.cookie_jar.load(cookies_file)

    if await login_session.is_logged_in():
        return None

    login_session.username = config.get('Test', 'account_name')

    try:
        login_session.password = config.get('Test', 'password_raw')
    except configparser.NoOptionError:
        encrypted_pass = config.get('Test', 'password')
        key = codecs.decode(encrypted_pass, 'rot13')
        raw = codecs.decode(key.encode(), 'base64')
        login_session.password = raw.decode()

    try:
        login_data = await login_session.do_login(shared_secret, mobile_login=True)
    except login.MailCodeError:
        login_data = await login_session.do_login(
            shared_secret,
            auth_code=await wait_mail_code(),
            auth_code_type=login.AuthCodeType.email,
            mobile_login=True,
        )
    except login.TwoFactorCodeError as exception:
        debug("waiting login request be accepted", 0)

        while True:
            login_data = await login_session.poll_login(exception.steamid, exception.client_id, exception.request_id)

            if not login_data:
                await asyncio.sleep(2)
                continue

            break

    login_session.http_session.cookie_jar.save(cookies_file)

    return None


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
        config.read(config_file)
        sms_code = config.get('Test', 'sms_code')

        if len(sms_code) == 5:
            break

        await asyncio.sleep(2)

    return sms_code


async def wait_mail_code():
    debug("waiting mail code")

    while True:
        config.read(config_file)
        mail_code = config.get('Test', 'mail_code')

        if len(mail_code) == 5:
            break

        await asyncio.sleep(2)

    return mail_code
