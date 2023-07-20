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

"""
`webapi` interface is used to interact with the official SteamWebAPI.
"""

import logging
import time
from typing import Any, Dict, List, NamedTuple, Optional

import aiohttp

from . import universe, utils

log = logging.getLogger(__name__)


class Game(NamedTuple):
    name: str
    """Name"""
    appid: int
    """App ID"""
    playtime_forever: int
    """Total playtime for game in all platforms"""
    img_icon_url: str
    """Icon image"""
    has_dlc: bool
    """True if game has dlc"""
    has_market: bool
    """True if game has market items"""
    has_workshop: bool
    """True if game has workshop"""


class AuthenticatorData(NamedTuple):
    shared_secret: str
    """shared secret"""
    identity_secret: str
    """identity secret"""
    serial_number: int
    """serial number"""
    revocation_code: str
    """revocation code"""
    uri: str
    """otpauth uri e.g.: otpauth://totp/Steam:<user>?secret=<secret>&issuer=Steam"""
    token_gid: str
    """token gid"""
    account_name: str
    """account name associated"""
    server_time: int
    """server time in unix format"""
    phone_number_hint: int
    """last 4 digits of phone number linked"""


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


class SteamWebAPI(utils.Base):
    def __init__(
            self,
            *,
            api_url: str = 'https://api.steampowered.com',
            api_key: str = '',
            **kwargs: Any,
    ) -> None:
        """
        Main class to access steam web api methods

        Example:

            ```
            webapi = await SteamWebAPI.new_session(0, api_key='SteamAPIKey')
            owned_games = await webapi.get_owned_games(steamid)
            ```
        """
        super().__init__(**kwargs)
        self.api_url = api_url
        self.api_key = api_key

    @staticmethod
    async def _new_mobile_data(
            steamid: universe.SteamId,
            token_type: str = 'mobileapp',
    ) -> Dict[str, Any]:
        current_time = int(time.time())

        return {
            'steamid': steamid.id64,
            'authenticator_time': current_time,
            'authenticator_type': universe.TOKEN_TYPE[token_type],
        }

    async def get_server_time(self) -> int:
        """Get server time"""
        json_data = await self.request_json(f'{self.api_url}/ISteamWebAPIUtil/GetServerInfo/v1')
        log.debug("server time found: %s", json_data['servertime'])
        return int(json_data['servertime'])

    async def get_custom_profile_url(self, steamid: universe.SteamId) -> str:
        """
        Get custom profile url
        :param steamid: `SteamId`
        :return: custom profile url as string
        """
        params = {'steamids': str(steamid.id64), 'key': self.api_key}
        json_data = await self.request_json(f'{self.api_url}/ISteamUser/GetPlayerSummaries/v2', params=params)

        if not json_data['response']['players']:
            raise ValueError('Failed to get profile url.')

        profile_url = str(json_data['response']['players'][0]['profileurl'])
        log.debug("profile url found: %s (from %s)", profile_url, steamid.id_string)
        return profile_url

    async def get_steamid(self, custom_profile_url: str) -> universe.SteamId:
        """
        Get `SteamId` from profile url
        :param custom_profile_url: Steam profile url
        :return: `SteamId`
        """
        params = {'vanityurl': custom_profile_url.split('/')[4], 'key': self.api_key}
        json_data = await self.request_json(f'{self.api_url}/ISteamUser/ResolveVanityURL/v1', params=params)

        if json_data['response']['success'] != 1:
            raise ValueError('Failed to get user id.')

        log.debug("steamid found: %s (from %s)", json_data['response']['steamid'], custom_profile_url)
        return universe.generate_steamid(json_data['response']['steamid'])

    async def get_personaname(self, steamid: universe.SteamId) -> str:
        """
        Get persona name from `SteamId`
        :param steamid: `SteamId`
        :return: Persona name as string
        """
        params = {'steamids': str(steamid.id64), 'key': self.api_key}
        json_data = await self.request_json(f'{self.api_url}/ISteamUser/GetPlayerSummaries/v2', params=params)

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
        """
        Get a list of owned games
        :param steamid: `SteamId`
        :param appids_filter: List of appids to look up
        :return: List of `Game`
        """
        params = {
            'steamid': str(steamid.id64),
            'include_appinfo': "1",
            'include_extended_appinfo': "1",
            'skip_unvetted_apps': "0",
            'key': self.api_key,
        }

        if appids_filter:
            for index, appid in enumerate(appids_filter):
                params[f"appids_filter[{index}]"] = str(appid)

        json_data = await self.request_json(f'{self.api_url}/IPlayerService/GetOwnedGames/v1', params=params)
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

            games.append(Game(**game_params))

        log.debug("%s owned games found.", json_data['response']['game_count'])

        return games

    async def new_authenticator(
            self,
            steamid: universe.SteamId,
            access_token: str,
            phone_id: int = 1,
    ) -> AuthenticatorData:
        """
        Initialize process to add a new authenticator to account
        :param steamid: `SteamId`
        :param access_token: user access token
        :param phone_id: Index of phone number
        :return: Updated account login data
        """
        data = await self._new_mobile_data(steamid)
        data['device_identifier'] = universe.generate_device_id(access_token)
        data['sms_phone_id'] = phone_id

        params = {'access_token': access_token}

        json_data = await self.request_json(
            f'{self.api_url}/ITwoFactorService/AddAuthenticator/v1',
            data=data,
            params=params,
        )

        response: Dict[str, Any] = json_data['response']

        if response['status'] == 29:
            raise AuthenticatorExists('An Authenticator is already active for that account.')

        if response['status'] in [84, 2]:
            raise PhoneNotRegistered('Phone not registered on Steam Account.')

        if response['status'] != 1:
            raise NotImplementedError(f"add_authenticator is returning status {response['status']}")

        return AuthenticatorData(
            response['shared_secret'],
            response['identity_secret'],
            int(response['serial_number']),
            response['revocation_code'],
            response['uri'],
            response['token_gid'],
            response['account_name'],
            int(response['server_time']),
            int(response['phone_number_hint']),
        )

    async def add_authenticator(
            self,
            steamid: universe.SteamId,
            access_token: str,
            shared_secret: str,
            sms_code: str,
            email_type: int = 2,
    ) -> bool:
        """
        Finalize process to add a new authenticator to account
        :param steamid: User SteamID
        :param access_token: User access token
        :param shared_secret: User shared secret
        :param sms_code: OTP received by SMS
        :param email_type: Email type
        :return: True if success
        """
        data = await self._new_mobile_data(steamid)
        server_time = await self.get_server_time()
        data['authenticator_code'] = universe.generate_steam_code(server_time, shared_secret)
        data['activation_code'] = sms_code
        data['validate_sms_code'] = 1

        params = {'access_token': access_token}

        json_data = await self.request_json(
            f'{self.api_url}/ITwoFactorService/FinalizeAddAuthenticator/v1',
            data=data,
            params=params,
        )

        if json_data['response']['status'] == 89:
            raise SMSCodeError("Invalid sms code")

        if json_data['response']['status'] == 2:
            data.pop('authenticator_code')
            data.pop('activation_code')
            data['email_type'] = email_type

            try:
                await self.request_json(
                    f'{self.api_url}/ITwoFactorService/SendEmail/v1',
                    data=data,
                    params=params,
                )
            except aiohttp.ContentTypeError:
                return False
            else:
                return True

        return False

    async def remove_authenticator(
            self,
            steamid: universe.SteamId,
            access_token: str,
            revocation_code: str,
            scheme: int = 2,
    ) -> bool:
        """
        Remove authenticator from account
        :param steamid: User SteamID
        :param access_token: User access token
        :param revocation_code: Steam auth revocation code
        :param scheme: Steam scheme
        :return: True if success
        """
        data = await self._new_mobile_data(steamid)
        data['revocation_code'] = revocation_code
        data['revocation_reason'] = 1
        data['steamguard_scheme'] = scheme

        params = {'access_token': access_token}

        json_data = await self.request_json(
            f'{self.api_url}/ITwoFactorService/RemoveAuthenticator/v1',
            data=data,
            params=params,
        )

        if json_data['response']['revocation_attempts_remaining'] == 0:
            raise RevocationError('No more attempts')

        return 'success' in json_data['response'] and json_data['response']['success'] is True
