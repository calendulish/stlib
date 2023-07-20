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
`login` interface is used to interact with undocumented steam login methods
it supports both desktop and mobile login at steam services
"""

import logging
import random
from enum import Enum
from typing import Any, Dict, NamedTuple, Optional, List

import rsa

from . import universe, utils

log = logging.getLogger(__name__)


class TransferInfo(NamedTuple):
    url: str
    """url associated"""
    nonce: str
    """Nonce key"""
    auth: str
    """Auth token"""


class LoginData(NamedTuple):
    steamid: int
    """Steam ID"""
    client_id: str
    """Client ID"""
    sessionid: str
    """Session ID"""
    refresh_token: str
    """Refresh token"""
    access_token: str
    """Access token"""
    transfer_info: List[TransferInfo]
    """List of `TransferInfo` associated"""


class AuthCodeType(Enum):
    email = 2
    """email code"""
    device = 3
    """device code"""
    machine = 6
    """machine token"""


class LoginError(ValueError):
    """Raised when login can`t be completed"""

    def __init__(self, message: str, captcha_requested: bool = False) -> None:
        super().__init__(message)

        self.captcha_requested = captcha_requested


class LoginBlockedError(LoginError):
    """Raised when user is temporarily blocked from login session"""
    pass


class CaptchaError(LoginError):
    """Raised when captcha is requested"""

    def __init__(self, message: str) -> None:
        super().__init__(message, captcha_requested=True)


class MailCodeError(LoginError):
    """Raised when mail code is requested"""
    pass


class TwoFactorCodeError(LoginError):
    """Raised when two-factor code is requested"""
    pass


# Don't instantiate this class directly!
# Use get_session to support multiple sessions!
class Login(utils.Base):
    def __init__(
            self,
            *,
            login_url: str = 'https://login.steampowered.com',
            steamguard_url: str = 'https://steamcommunity.com/steamguard',
            api_url: str = 'https://api.steampowered.com',
            **kwargs: Any,
    ) -> None:
        """
        Main login class used to login a user on steam session

        Example:

            ```
            login_session = await Login.new_session(0)
            login_session.username = 'SteamUserName'
            login_session.password = 'SteamPassword'
            await login_session.do_login()
            ```
        """
        super().__init__(**kwargs)
        self._username: Optional[str] = None
        self.__password: Optional[str] = None
        self.login_url = login_url
        self.steamguard_url = steamguard_url
        self.api_url = api_url
        self.login_trial = 3

    @property
    def username(self) -> str:
        """Steam username"""
        if not self._username:
            raise AttributeError('Username is required to login')

        return self._username

    @username.setter
    def username(self, username: str) -> None:
        self._username = username

    @property
    def password(self) -> None:
        """Protected steam password"""
        raise PermissionError('Passwords are protected')

    @password.setter
    def password(self, __password: str) -> None:
        self.__password = __password

    async def _new_login_data(self, mobile_login: bool = False) -> Dict[str, Any]:
        steam_key = await self.get_steam_key(self.username)

        if not self.__password:
            raise AttributeError('Password is required to login')

        encrypted_password = universe.encrypt_password(steam_key, self.__password)

        return {
            "account_name": self.username,
            "encrypted_password": encrypted_password.decode(),
            "encryption_timestamp": steam_key.timestamp,
            "device_friendly_name": "stlib",
            "persistence": 1,
            "platform_type": "3" if mobile_login else "2",
            "website_id": "Mobile" if mobile_login else "Community",
        }

    async def get_steam_key(self, username: str) -> universe.SteamKey:
        """
        Get `SteamKey`
        :param username: Steam username as string
        :return: `SteamKey`
        """
        params = {'account_name': username}
        json_data = await self.request_json(
            f'{self.api_url}/IAuthenticationService/GetPasswordRSAPublicKey/v1',
            params=params,
        )

        if not json_data['response']:
            raise ValueError('Failed to get public key.')

        public_mod = int(json_data['response']['publickey_mod'], 16)
        public_exp = int(json_data['response']['publickey_exp'], 16)
        timestamp = int(json_data['response']['timestamp'])
        return universe.SteamKey(rsa.PublicKey(public_mod, public_exp), timestamp)

    async def get_captcha(self, gid: int) -> bytes:
        """
        Get captcha image
        :param gid: Captcha GID
        :return: Image
        """
        params = {'gid': str(gid)}
        response = await self.request(f'{self.login_url}/rendercaptcha/', params=params, raw_data=True)
        assert isinstance(response.content, bytes), "rendercaptcha response is not bytes"
        return response.content

    async def has_phone(self, sessionid: str) -> bool:
        """
        Check if user has a phone registered on steam account
        :param sessionid: steam session id
        :return: True if success
        """
        data = {
            'op': "has_phone",
            'sessionid': sessionid,
        }

        json_data = await self.request_json(f'{self.steamguard_url}/phoneajax', data=data)

        if not json_data['success']:
            if 'error_text' in json_data:
                raise LoginError(json_data['error_text'])

            raise LoginError("Current session is invalid")

        log.debug("User has phone? %s", json_data["has_phone"])

        return json_data["has_phone"]

    async def do_login(
            self,
            shared_secret: str = '',
            auth_code: str = '',
            auth_code_type: AuthCodeType = AuthCodeType.device,
            mobile_login: bool = False,
    ) -> LoginData:
        """
        Login a user on Steam
        :param shared_secret: User shared secret
        :param auth_code: optional auth code to login
        :param auth_code_type: auth code type
        :param mobile_login: True to request mobile session instead desktop one
        :return: Updated `LoginData`
        """
        _original_fargs = locals().copy()
        _original_fargs.pop('self')

        data = await self._new_login_data(mobile_login)

        json_data = await self.request_json(
            f'{self.api_url}/IAuthenticationService/BeginAuthSessionViaCredentials/v1',
            data=data,
        )

        if 'steamid' not in json_data['response']:
            raise LoginError('Unable to log-in. Check your username and password.')

        client_id = json_data['response']['client_id']
        request_id = json_data['response']['request_id']
        steamid = json_data['response']['steamid']

        if shared_secret:
            server_data = await self.request_json(f'{self.api_url}/ISteamWebAPIUtil/GetServerInfo/v1')
            server_time = server_data['servertime']
            auth_code = universe.generate_steam_code(server_time, shared_secret)

        if auth_code:
            log.warning("Using external auth code to log-in")
        elif not shared_secret:
            log.warning("Logging without two-factor authentication.")

        if auth_code:
            data = {
                "client_id": client_id,
                "steamid": steamid,
                "code": auth_code,
                "code_type": auth_code_type.value,
            }

            auth_data = await self.request_json(
                f'{self.api_url}/IAuthenticationService/UpdateAuthSessionWithSteamGuardCode/v1',
                data=data,
                raise_for_status=False,
            )

            if not auth_data['response']:
                raise LoginError('SteamGuard code is wrong')
        else:
            captcha_requested = len(json_data['response']['allowed_confirmations']) > 1
            auth_code_type = json_data['response']['allowed_confirmations'][0]['confirmation_type']

            if auth_code_type == 2:
                raise MailCodeError("Mail code requested", captcha_requested)

            if auth_code_type == 3:
                raise TwoFactorCodeError("Authenticator code requested", captcha_requested)

            if auth_code_type == 6:
                raise CaptchaError("Captcha code requested")

        data = {
            "client_id": client_id,
            "request_id": request_id,
        }

        json_data = await self.request_json(
            f'{self.api_url}/IAuthenticationService/PollAuthSessionStatus/v1',
            data=data,
        )

        if 'refresh_token' not in json_data['response']:
            raise LoginError('Tokens are not received. Try again.')

        refresh_token = json_data['response']['refresh_token']
        access_token = json_data['response']['access_token']
        sessionid = ''.join(random.choices('0123456789abcdef', k=24))

        data = {
            "nonce": refresh_token,
            "sessionid": sessionid,
        }

        json_data = await self.request_json(f'{self.login_url}/jwt/finalizelogin', data=data)
        transfer_info = []

        for item in json_data['transfer_info']:
            data = {
                'nonce': item['params']['nonce'],
                'auth': item['params']['auth'],
                'steamID': steamid,
            }

            response = await self.request(item['url'], data=data)

            if 'steamLoginSecure' not in response.cookies:
                raise LoginError('Error setting login cookies')

            transfer_info.append(TransferInfo(item['url'], data['nonce'], data['auth']))

        return LoginData(steamid, client_id, sessionid, refresh_token, access_token, transfer_info)

    async def is_logged_in(self) -> bool:
        """
        Check if user is logged in
        :return: bool
        """
        try:
            response = await self.request(
                'https://store.steampowered.com/account', allow_redirects=False
            )
        except LoginError:
            return False

        return response.status == 200
