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

I recommend you to check if SteamWorks is available prior using
the client interface:

```
import stlib

if stlib.steamworks_available:
    from stlib import client
else:
    # not available
```
"""

import logging
from concurrent.futures.process import ProcessPoolExecutor
from types import TracebackType
from typing import Optional, Type

from . import NoSteamWorksError

try:
    from stlib import steamworks  # type: ignore
except ImportError:
    raise NoSteamWorksError(
        'stlib has been built without SteamWorks support. '
        'Client interface is unavailable'
    )

log = logging.getLogger(__name__)


class SteamGameServer:
    """
    Create and run a SteamGameServer.
    It will raise ProcessLookupError if Steam Client isn't running.

    Example:

    ```
        with SteamGameServer() as game_server:
            server_time = game_server.get_server_time()
    ```
    """

    def __init__(self, appid: int = 480, ip: int = 0x0100007f, port: int = 27016) -> None:
        self.game_server = steamworks.SteamGameServer(appid, ip, port)

    def __enter__(self) -> steamworks.SteamGameServer:
        return self.game_server

    def __exit__(self,
                 exception_type: Optional[Type[BaseException]],
                 exception_value: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> None:
        log.debug('Closing SteamGameServer')
        self.game_server.shutdown()


class SteamAPIExecutor(ProcessPoolExecutor):
    """
    Create an isolated process to access SteamAPI.
    It will raise ProcessLookupError if Steam Client isn't running.

    Example:

    ```
        with SteamAPIExecutor() as steam_api:
            steamid = steam_api.get_steamid()
    ```
    """

    def __init__(self, appid: int = 480, max_workers: int = 1) -> None:
        """
        :param appid: owned steam appid.
        :param max_workers: max workers processes
        """
        super().__init__(max_workers=max_workers)
        self.appid = appid
        self._steam_api_handle = self.submit(steamworks.SteamAPI, self.appid)

    @property
    def steam_api(self) -> steamworks.SteamAPI:
        return self._steam_api_handle.result()

    def __enter__(self) -> steamworks.SteamAPI:
        return self.steam_api

    def __exit__(self,
                 exception_type: Optional[Type[BaseException]],
                 exception_value: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> None:
        log.debug('Closing SteamAPI')
        self.shutdown()
