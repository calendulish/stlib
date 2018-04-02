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

        self.process_return, self.__return = multiprocessing.Pipe(False)
        self.process_exception, self.__exception = multiprocessing.Pipe(False)

    def __enter__(self):
        self.exit_now.clear()
        self.start()

        if self.process_return.poll(timeout=5):
            return self
        else:
            if self.process_exception.poll():
                raise self.process_exception.recv()
            else:
                raise AssertionError("No return from `Process' in SteamAppExecutor")

    def __exit__(self, exc_type, exc_value, traceback):
        steam_api.shutdown()
        self.exit_now.set()
        self.join(5)
        self.close()

    def run(self) -> None:
        os.environ["SteamAppId"] = str(self.game_id)

        try:
            with _CaptureSTD():
                result = steam_api.init()
        except Exception as exception:
            self.__exception.send(exception)
        else:
            self.__return.send(result)
            self.exit_now.wait()
