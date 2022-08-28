#!/usr/bin/env python
#
# Lara Maia <dev@lara.monster> 2015 ~ 2022
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

import logging
import time
from typing import Any, Dict, List, NamedTuple, Optional

import aiohttp

from . import universe, login, utils

log = logging.getLogger(__name__)


class Game(NamedTuple):
    name: str
    appid: int
    playtime_forever: int
    img_icon_url: str
    has_dlc: bool
    has_market: bool
    has_workshop: bool


class PhoneNotRegistered(Exception):
    """Raised when no phone number is registered on account"""
    pass


class AuthenticatorExists(Exception):
    """Raised when an authenticator is already active for the account"""
    pass


class RevocationError(Exception):
    """Raised when user can't use revocation codes anymore"""
    pass


class SMSCodeError(ValueError):
    """Raised when a sms code is requested"""
    pass


# Don't instantiate this class directly!
# Use get_session to support multiple sessions!
class SteamWebAPI(utils.Base):
    def __init__(
            self,
            *,
            api_url: str = 'https://api.steampowered.com',
            api_key: str = '',
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.api_url = api_url
        self.api_key = api_key

    @staticmethod
    async def _new_mobile_query(oauth_data: Dict[str, Any], token_type: str = 'mobileapp') -> Dict[str, Any]:
        current_time = int(time.time())

        params = {
            'steamid': oauth_data['steamid'],
            'access_token': oauth_data['oauth_token'],
            'authenticator_time': current_time,
            'authenticator_type': universe._TOKEN_TYPE[token_type],
        }

        return params

    async def get_server_time(self) -> int:
        json_data = await self.request_json(f'{self.api_url}/ISteamWebAPIUtil/GetServerInfo/v1')
        log.debug("server time found: %s", json_data['servertime'])
        return int(json_data['servertime'])

    async def get_custom_profile_url(self, steamid: universe.SteamId) -> str:
        params = {'steamids': str(steamid.id64)}
        json_data = await self.request_json(f'{self.api_url}/ISteamUser/GetPlayerSummaries/v2', params)

        if not json_data['response']['players']:
            raise ValueError('Failed to get profile url.')

        profile_url = str(json_data['response']['players'][0]['profileurl'])
        log.debug("profile url found: %s (from %s)", profile_url, steamid.id_string)
        return profile_url

    async def get_steamid(self, profile_url: str) -> universe.SteamId:
        params = {'vanityurl': profile_url.split('/')[4]}
        json_data = await self.request_json(f'{self.api_url}/ISteamUser/ResolveVanityURL/v1', params)

        if json_data['response']['success'] != 1:
            raise ValueError('Failed to get user id.')

        log.debug("steamid found: %s (from %s)", json_data['response']['steamid'], profile_url)
        return universe.generate_steamid(json_data['response']['steamid'])

    async def get_personaname(self, steamid: universe.SteamId) -> str:
        params = {'steamids': str(steamid.id64)}
        json_data = await self.request_json(f'{self.api_url}/ISteamUser/GetPlayerSummaries/v2', params)

        if not json_data['response']['players']:
            raise ValueError('Failed to get personaname.')

        nickname = str(json_data['response']['players'][0]['personaname'])
        log.debug("personaname found: %s (from %s)", nickname, steamid.id_string)
        return nickname

    async def get_owned_games(
            self,
            steamid: universe.SteamId,
            *,
            appids_filter: Optional[List[int]] = None,
    ) -> List[Game]:
        params = {
            'steamid': str(steamid.id64),
            'include_appinfo': "1",
            'skip_unvetted_apps': "0",
        }

        if appids_filter:
            for index, appid in enumerate(appids_filter):
                params[f"appids_filter[{index}]"] = str(appid)

        json_data = await self.request_json(f'{self.api_url}/IPlayerService/GetOwnedGames/v1', params)
        games = []

        if 'games' not in json_data['response']:
            raise ValueError('Failed to get owned games.')

        for game in json_data['response']['games']:
            game_params = {
                'name': game['name'],
                'appid': game['appid'],
                'playtime_forever': game['playtime_forever'],
                'img_icon_url': game['img_icon_url'],
                'has_dlc': game['has_dlc'],
                'has_market': game['has_market'],
                'has_workshop': game['has_workshop'],
            }

            games.append(**game_params)

        log.debug(f"{json_data['response']['game_count']} owned games found.")

        return games

    async def new_authenticator(
            self,
            login_data: login.LoginData,
            phone_id: int = 1,
    ) -> login.LoginData:
        data = await self._new_mobile_query(login_data.oauth)
        data['device_identifier'] = universe.generate_device_id(login_data.auth['shared_secret'])
        data['sms_phone_id'] = phone_id

        json_data = await self.request_json(f'{self.api_url}/ITwoFactorService/AddAuthenticator/v1', data=data)
        response: Dict[str, Any] = json_data['response']

        if response['status'] == 29:
            raise AuthenticatorExists('An Authenticator is already active for that account.')
        elif response['status'] == 84 or response['status'] == 2:
            raise PhoneNotRegistered('Phone not registered on Steam Account.')
        elif response['status'] != 1:
            raise NotImplementedError(f"add_authenticator is returning status {response['status']}")

        return login_data._replace(auth=response)

    async def add_authenticator(
            self,
            login_data: login.LoginData,
            sms_code: str,
            email_type: int = 2,
            time_offset: int = 0,
    ) -> bool:
        data = await self._new_mobile_query(login_data.oauth)
        server_time = int(time.time()) - time_offset
        data['authenticator_code'] = universe.generate_steam_code(server_time, login_data.auth['shared_secret'])
        data['activation_code'] = sms_code
        json_data = await self.request_json(f'{self.api_url}/ITwoFactorService/FinalizeAddAuthenticator/v1', data=data)

        if json_data['response']['status'] == 89:
            raise SMSCodeError("Invalid sms code")

        if json_data['response']['status'] == 2:
            data.pop('authenticator_code')
            data.pop('activation_code')
            data['email_type'] = email_type

            try:
                await self.request_json(f'{self.api_url}/ITwoFactorService/SendEmail/v1', data=data)
            except aiohttp.ContentTypeError:
                return False
            else:
                return True

        return False

    async def remove_authenticator(
            self,
            login_data: login.LoginData,
            revocation_code: str,
            scheme: int = 2,
    ) -> bool:
        data = await self._new_mobile_query(login_data.oauth)
        data['revocation_code'] = revocation_code
        data['steamguard_scheme'] = scheme

        try:
            json_data = await self.request_json(f'{self.api_url}/ITwoFactorService/RemoveAuthenticator/v1', data=data)
        except aiohttp.ClientResponseError:
            return False

        if json_data['response']['revocation_attempts_remaining'] == 0:
            raise RevocationError('No more attempts')

        if 'success' in json_data['response'] and json_data['response']['success'] is True:
            return True
        else:
            return False
