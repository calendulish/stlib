#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015 ~ 2018
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
import multiprocessing
import os
import sys
from multiprocessing import connection
from types import TracebackType
from typing import Any, Callable, Optional, Type, TypeVar

try:
    from stlib import steam_api  # type: ignore
except ImportError:
    raise ImportError(
        'stlib has been built without steam_api support. '
        'Client interface is unavailable'
    )

SteamApiExecutorType = TypeVar('SteamApiExecutorType', bound='SteamApiExecutor')
PipeType = connection.Connection
log = logging.getLogger(__name__)


class SteamGameServerError(Exception): pass


class SteamAPIError(Exception): pass


class _CaptureSTD:
    def __init__(self) -> None:
        self.old_stdout = os.dup(1)
        self.old_stderr = os.dup(2)
        self.devnull = os.open(os.path.devnull, os.O_WRONLY)

    def __enter__(self) -> None:
        os.dup2(self.devnull, 1)
        os.dup2(self.devnull, 2)

    def __exit__(self,
                 exception_type: Optional[Type[BaseException]],
                 exception_value: Optional[Exception],
                 traceback: Optional[TracebackType]) -> None:
        os.dup2(self.old_stdout, 1)
        os.dup2(self.old_stderr, 2)
        os.close(self.devnull)


class SteamGameServer:
    def __init__(self, ip: int = 0x0100007f, steam_port: int = 27015, game_port: int = 27016,
                 game_id: int = 480) -> None:
        log.debug('Set SteamAppId to %s', game_id)
        os.environ["SteamAppId"] = str(game_id)

        with _CaptureSTD():
            result = steam_api.server_init(ip, steam_port, game_port)
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
        os.environ.pop('SteamAppId')


class SteamApiExecutor(multiprocessing.Process):
    def __init__(self: SteamApiExecutorType, game_id: int = 480) -> None:
        super().__init__()
        self.game_id = game_id

        self.exit_now = multiprocessing.Event()

        self._init_return, self.__child_init_return = multiprocessing.Pipe(False)
        self._init_exception, self.__child_init_exception = multiprocessing.Pipe(False)

        self.__child_interface, self._interface = multiprocessing.Pipe(False)
        self._interface_return, self.__child_interface_return = multiprocessing.Pipe(False)
        self._interface_exception, self.__child_interface_exception = multiprocessing.Pipe(False)

    def __enter__(self: SteamApiExecutorType) -> SteamApiExecutorType:
        result = self.init()
        log.debug("SteamAPI init returns %s", result)

        if result is False:
            raise SteamAPIError("Unable to initialize SteamAPI (Invalid game id?)")

        return self

    def __exit__(self: SteamApiExecutorType,
                 exception_type: Optional[Type[BaseException]],
                 exception_value: Optional[Exception],
                 traceback: Optional[TracebackType]) -> None:
        self.shutdown()

    @staticmethod
    def _wait_return(return_pipe: PipeType, exception_pipe: PipeType) -> Any:
        if return_pipe.poll(timeout=5):
            log.debug("Returning result from pipe")
            return return_pipe.recv()
        else:
            if exception_pipe.poll():
                log.debug("Raise custom exception from pipe")
                raise exception_pipe.recv()
            else:
                log.debug("Raise TimeoutError when waiting `Process' return")
                raise multiprocessing.TimeoutError("No return from `Process' in SteamAppExecutor")

    def init(self: SteamApiExecutorType) -> Any:
        self.exit_now.clear()
        self.start()

        return self._wait_return(self._init_return, self._init_exception)

    def shutdown(self: SteamApiExecutorType) -> None:
        self.exit_now.set()
        self.join(5)

        if sys.version_info >= (3, 7):
            self.close()

    def call(self: SteamApiExecutorType, method: Callable[..., Any]) -> Any:
        self._interface.send(method)

        return self._wait_return(self._interface_return, self._interface_exception)

    def run(self: SteamApiExecutorType) -> None:
        log.debug("Set SteamAppId to %s", self.game_id)
        os.environ["SteamAppId"] = str(self.game_id)

        try:
            with _CaptureSTD():
                result = steam_api.init()
                log.debug("SteamAPI init returns %s", result)
        except Exception as exception:
            log.debug("Send exception to child process")
            self.__child_init_exception.send(exception)
            return None
        else:
            log.debug("Send result to child process")
            self.__child_init_return.send(result)

        while not self.exit_now.is_set():
            if self.__child_interface.poll():
                interface_class = self.__child_interface.recv()
                try:
                    result = interface_class()
                    log.debug("interface_class returns %s", result)
                except Exception as exception:
                    log.debug("Send interface_class exception to child interface")
                    self.__child_interface_exception.send(exception)
                    return None
                else:
                    log.debug("Send interface_class return to child interface")
                    self.__child_interface_return.send(result)

        log.debug("Shutdown SteamAPI")
        steam_api.shutdown()
        os.environ.pop("SteamAppId")
