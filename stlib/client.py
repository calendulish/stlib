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


class _Wrapper(multiprocessing.Process):
    def __init__(self, game_id, queue, started, exit_now):
        super().__init__()
        os.environ["SteamAppId"] = str(game_id)
        self.queue = queue
        self.started = started
        self.exit_now = exit_now

    def run(self) -> None:
        with _CaptureSTD():
            result = steam_api.init()

        self.queue.put(result)
        self.started.set()

        if result:
            self.exit_now.clear()
        else:
            self.exit_now.set()

        self.exit_now.wait()
        steam_api.shutdown()


class Overlay(object):
    def __init__(self):
        self.process = None
        self.queue = multiprocessing.Queue()
        self.exit_now = multiprocessing.Event()
        self.started = multiprocessing.Event()

    def hook(self, game_id: int = None) -> bool:
        self.process = _Wrapper(game_id, self.queue, self.started, self.exit_now)
        self.process.start()
        self.started.wait()

        return self.queue.get()

    def unhook(self) -> None:
        self.exit_now.set()
        self.process.join()
