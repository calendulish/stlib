import configparser
import os

import aiohttp
import pytest
from stlib import authenticator, webapi

from tests import MANUAL_TESTING, requires_manual_testing


class TestWebApi:
    if MANUAL_TESTING:
        config_parser = configparser.RawConfigParser()
        config_parser.read(os.path.join(os.path.dirname(__file__), '..', 'conftest.ini'))
        adb_path = config_parser.get("Test", "adb_path")
        adb = authenticator.AndroidDebugBridge(adb_path)
        username = config_parser.get("Test", "username")
        password = config_parser.get("Test", "password")

    @requires_manual_testing
    @pytest.mark.asyncio
    async def test_do_login(self) -> None:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            steam_webapi = webapi.SteamWebAPI(session, 'https://lara.click/api')
            steam_key = await steam_webapi.get_steam_key(self.username)
            encrypted = webapi.encrypt_password(steam_key, self.password)
            json_data = await self.adb.get_json('shared_secret')
            server_time = await steam_webapi.get_server_time()
            code = authenticator.get_code(server_time, json_data['shared_secret'])

            json_data = await steam_webapi.do_login(self.username, encrypted, steam_key.timestamp, code.code)
            assert isinstance(json_data['success'], bool)
            assert json_data['success'] is True

            secret = await self.adb.get_json('identity_secret')
            deviceid = await self.adb.get_device_id()
            steamid = json_data["transfer_parameters"]["steamid"]

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
