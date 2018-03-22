#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015 ~ 2018
#
# The Steam Tools is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# The Steam Tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#

import multiprocessing
import os
import signal
import time

import steam_api


class _CaptureSTD(object):
    def __init__(self):
        self.old_descriptor = os.dup(1)

    def __enter__(self):
        new_descriptor = os.open(os.devnull, os.O_WRONLY)
        os.dup2(new_descriptor, 2)

    def __exit__(self, exc_type, exc_value, traceback):
        os.dup2(self.old_descriptor, 1)


class _Wrapper(multiprocessing.Process):
    def __init__(self, game_id, queue):
        super().__init__()
        os.environ["SteamAppId"] = str(game_id)
        self.queue = queue

    def run(self) -> None:
        stop = False

        self.queue.put(steam_api.init())

        def raised(signum, frame):
            nonlocal stop
            stop = True
            steam_api.shutdown()

        signal.signal(signal.SIGINT, raised)
        signal.signal(signal.SIGTERM, raised)

        while not stop:
            time.sleep(1)


class Overlay():
    def __init__(self):
        self.process = None
        self.queue = multiprocessing.Queue()

    def hook(self, game_id: int = None) -> bool:
        self.process = _Wrapper(game_id, self.queue)
        self.process.start()
        time.sleep(0.2)
        return self.queue.get()

    def unhook(self) -> None:
        steam_api.shutdown()
        self.process.terminate()
        self.process.join()
