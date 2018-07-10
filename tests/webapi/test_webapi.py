import asyncio
import configparser
import json
import os

import aiohttp
import pytest
from stlib import authenticator, webapi

from tests import MANUAL_TESTING, debug, requires_manual_testing


class TestWebApi:
    if MANUAL_TESTING:
        config_parser = configparser.RawConfigParser()
        config_parser.read(os.path.join(os.path.dirname(__file__), '..', 'conftest.ini'))
        adb_path = config_parser.get("Test", "adb_path")
        adb = authenticator.AndroidDebugBridge(adb_path)
        username = config_parser.get("Test", "username")
        password = config_parser.get("Test", "password")

    async def simple_login(self, session: aiohttp.ClientSession, mobile_login):
        login = webapi.Login(session, self.username, self.password)
        steam_webapi = webapi.SteamWebAPI(session, 'https://lara.click/api')
        mail_code = ''
        authenticator_code = ''

        while True:
            try:
                login_data = await login.do_login(
                    emailauth=mail_code,
                    authenticator_code=authenticator_code,
                    mobile_login=mobile_login
                )
                debug(str(login_data))
            except webapi.MailCodeError:
                mail_code = input("Write code received by email: ")
                await asyncio.sleep(5)
                continue
            except webapi.TwoFactorCodeError:
                secret_data = await self.adb.get_json('shared_secret')
                debug(str(secret_data))
                server_time = await steam_webapi.get_server_time()
                debug(str(server_time))
                authenticator_code = authenticator.get_code(server_time, secret_data['shared_secret'])
                await asyncio.sleep(5)
                continue
            else:
                assert isinstance(login_data['success'], bool)
                assert login_data['success'] is True
                break

        return login_data

    @requires_manual_testing
    @pytest.mark.asyncio
    async def test_confirmations(self) -> None:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            steam_webapi = webapi.SteamWebAPI(session, 'https://lara.click/api')
            login_data = await self.simple_login(session, False)

            secret = await self.adb.get_json('identity_secret')
            deviceid = await self.adb.get_device_id()
            steamid = login_data["steamid"]

            confirmations = await steam_webapi.get_confirmations(secret['identity_secret'], steamid, deviceid)

            for confirmation in confirmations:
                assert isinstance(confirmation, webapi.Confirmation)

                # await steam_webapi.finalize_confirmation(
                #    secret['identity_secret'],
                #    steamid,
                #    deviceid,
                #    confirmation.id,
                #    confirmation.key,
                #    "cancel",
                # )

    @requires_manual_testing
    @pytest.mark.asyncio
    async def test_add_authenticator(self) -> None:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            login = webapi.Login(session, self.username, self.password)
            steam_webapi = webapi.SteamWebAPI(session, 'https://lara.click/api')

            secret = await self.adb.get_json('identity_secret')

            login_data = await self.simple_login(session, True)

            oauth_data = json.loads(login_data['oauth'])
            debug(str(oauth_data))
            assert isinstance(oauth_data, dict)

            async with session.get('https://steamcommunity.com') as response:
                print(response.cookies)
                sessionid = response.cookies['sessionid'].value

            assert await login.has_phone(sessionid) is True

            deviceid = authenticator.generate_device_id(secret['identity_secret'])
            debug(str(deviceid))

            auth_data = await steam_webapi.add_authenticator(
                oauth_data['steamid'],
                deviceid,
                oauth_data['oauth_token']
            )

            debug(str(auth_data))
            assert isinstance(auth_data, dict)
            assert auth_data['status'] == 1

            sms_code = input('Write code received by sms: ')

            authenticator_code = authenticator.get_code(int(auth_data['server_time']), auth_data['shared_secret'])
            debug(authenticator_code.code)

            auth_add_complete = await steam_webapi.finalize_add_authenticator(
                oauth_data['steamid'],
                oauth_data['oauth_token'],
                authenticator_code.code,
                sms_code,
            )

            assert auth_add_complete is True
