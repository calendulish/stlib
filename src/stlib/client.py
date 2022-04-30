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
    def __init__(self, ip: int = 0x0100007f, game_port: int = 27016,
                 game_id: int = 480) -> None:
        log.debug('Set SteamAppId to %s', game_id)
        os.environ["SteamAppId"] = str(game_id)

        result = steam_api.server_init(ip, game_port)
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
    def __init__(self, game_id: int = 480, loop: Optional[Any] = None) -> None:
        super().__init__()
        self.game_id = game_id
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
        log.debug("Set SteamAppId to %s", self.game_id)
        os.environ["SteamAppId"] = str(self.game_id)
        result = await self.loop.run_in_executor(self, steam_api.init)

        log.debug("SteamAPI init returns %s", result)

        if result is False:
            raise SteamAPIError("Unable to initialize SteamAPI (Invalid game id?)")

    async def soft_shutdown(self) -> None:
        log.debug("Soft Shutdown SteamAPI")
        await self.loop.run_in_executor(self, steam_api.shutdown)

    async def shutdown(self, wait: bool = True) -> None:
        log.debug("Shutdown SteamAPI")
        await self.loop.run_in_executor(self, steam_api.shutdown)
        super().shutdown(wait)

        try:
            os.environ.pop("SteamAppId")
        except KeyError:
            log.warning("Tried to unset SteamAppId but it's already unset")
