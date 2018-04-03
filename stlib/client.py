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

import multiprocessing
import os
import steam_api


class _CaptureSTD(object):
    def __init__(self):
        self.old_descriptor = os.dup(1)

    def __enter__(self):
        new_descriptor = os.open(os.devnull, os.O_WRONLY)
        os.dup2(new_descriptor, 2)

    def __exit__(self, exc_type, exc_value, traceback):
        os.dup2(self.old_descriptor, 1)


class SteamApiExecutor(multiprocessing.Process):
    def __init__(self, game_id: int = 480):
        super().__init__()
        self.game_id = game_id

        self.exit_now = multiprocessing.Event()

        self._init_return, self.__child_init_return = multiprocessing.Pipe(False)
        self._init_exception, self.__child_init_exception = multiprocessing.Pipe(False)

        self.__child_interface, self._interface = multiprocessing.Pipe(False)
        self._interface_return, self.__child_interface_return = multiprocessing.Pipe(False)
        self._interface_exception, self.__child_interface_exception = multiprocessing.Pipe(False)

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.shutdown()

    @staticmethod
    def _wait_return(return_pipe, exception_pipe):
        if return_pipe.poll(timeout=5):
            return return_pipe.recv()
        else:
            if exception_pipe.poll():
                raise exception_pipe.recv()
            else:
                raise TimeoutError("No return from `Process' in SteamAppExecutor")

    def init(self):
        self.exit_now.clear()
        self.start()

        return self._wait_return(self._init_return, self._init_exception)

    def shutdown(self):
        steam_api.shutdown()
        self.exit_now.set()
        self.join(5)
        self.close()

    def call(self, method):
        self._interface.send(method)

        return self._wait_return(self._interface_return, self._interface_exception)

    def run(self) -> None:
        os.environ["SteamAppId"] = str(self.game_id)

        try:
            with _CaptureSTD():
                result = steam_api.init()
        except Exception as exception:
            self.__child_init_exception.send(exception)
            return None
        else:
            self.__child_init_return.send(result)

        while not self.exit_now.is_set():
            if self.__child_interface.poll():
                interface_class = self.__child_interface.recv()
                try:
                    result = interface_class()
                except Exception as exception:
                    self.__child_interface_exception.send(exception)
                    return None
                else:
                    self.__child_interface_return.send(result)
