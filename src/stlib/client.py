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

"""
`client` interface is used to interact directly with SteamWorks SDK
it's an optional module and can be disabled when building stlib.
"""

import asyncio
import logging
import os
from concurrent.futures.process import ProcessPoolExecutor
from types import TracebackType
from typing import Any, Optional, Type

try:
    from stlib import steam_api  # type: ignore
except ImportError:
    raise ImportError(
        'stlib has been built without steam_api support. '
        'Client interface is unavailable'
    )

log = logging.getLogger(__name__)


class SteamGameServerError(Exception):
    """Raised when SteamGameServer can't be initialized"""
    pass


class SteamAPIError(Exception):
    """Raised when SteamAPI can't be initialized"""
    pass


class SteamGameServer:
    """
    Create and run a steam game server.

    Example:

    ```
        with SteamGameServer() as server:
            server_time = server.get_server_time()
    ```
    """
    def __init__(self, ip: int = 0x0100007f, port: int = 27016,
                 appid: int = 480) -> None:
        log.debug('Set SteamAppId to %s', appid)
        os.environ["SteamAppId"] = str(appid)

        result = steam_api.server_init(ip, port)
        log.debug('server init returns %s', result)

        if result is False:
            raise SteamGameServerError("Unable to initialize SteamGameServer")

    def __enter__(self) -> Any:
        return steam_api.SteamGameServer()

    def __exit__(self,
                 exception_type: Optional[Type[BaseException]],
                 exception_value: Optional[Exception],
                 traceback: Optional[TracebackType]) -> None:
        log.debug('Closing GameServer')
        steam_api.server_shutdown()

        try:
            os.environ.pop('SteamAppId')
        except KeyError:
            log.warning("Tried to unset SteamAppId but it's already unset")


class SteamApiExecutor(ProcessPoolExecutor):
    """
    Create a isolated steam app process.

    Example:

    ```
        async with SteamApiExecutor() as executor:
            steam_user = executor.submit(steam_api.SteamUser).result()
            steamid = executor.submit(steam_user.get_steam_id).result()
    ```
    """
    def __init__(self, appid: int = 480, loop: Optional[Any] = None) -> None:
        """
        :param appid: owned steam appid.
        :param loop: current event loop.
        """
        super().__init__()
        self.appid = appid
        self.loop = loop if loop else asyncio.get_event_loop()

    async def __aenter__(self) -> Any:
        await self.init()
        return self

    async def __aexit__(self,
                        exception_type: Optional[Type[BaseException]],
                        exception_value: Optional[Exception],
                        traceback: Optional[TracebackType]) -> None:
        await self.shutdown()

    async def init(self) -> None:
        """
        Initialize steam app process and populate steam_api pointers.
        """
        log.debug("Set SteamAppId to %s", self.appid)
        os.environ["SteamAppId"] = str(self.appid)
        result = await self.loop.run_in_executor(self, steam_api.init)

        log.debug("SteamAPI init returns %s", result)

        if result is False:
            raise SteamAPIError("Unable to initialize SteamAPI (Invalid game id?)")

    async def soft_shutdown(self) -> None:
        """
        Request steam_api to shutdown and clean-up resources associated with steam app.
        """
        log.debug("Soft Shutdown SteamAPI")
        await self.loop.run_in_executor(self, steam_api.shutdown)

    async def shutdown(self, wait: bool = True, **kwargs) -> None:
        log.debug("Shutdown SteamAPI")
        await self.loop.run_in_executor(self, steam_api.shutdown)
        super().shutdown(wait)

        try:
            os.environ.pop("SteamAppId")
        except KeyError:
            log.warning("Tried to unset SteamAppId but it's already unset")
