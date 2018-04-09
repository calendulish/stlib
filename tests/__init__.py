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

import asyncio
import inspect
import os
import sys
import time
from typing import Generator, Optional

import pytest

MANUAL_TESTING = int(os.environ.get('MANUAL_TESTING'))

@pytest.fixture(autouse=True)
def debug(msg: Optional[str] = None, wait_for: int = 5) -> None:
    # noinspection PySimplifyBooleanCheck
    if MANUAL_TESTING == True:
        current_frame = inspect.currentframe()
        outer_frame = inspect.getouterframes(current_frame, 2)

        if msg:
            print(f'   -> {outer_frame[1][3]}:{msg}')
            time.sleep(wait_for)
        else:
            print('\n')


def get_event_loop() -> asyncio.AbstractEventLoop:
    if sys.platform == 'win32':
        return asyncio.ProactorEventLoop()  # on windows IO needs this
    return asyncio.new_event_loop()  # default on UNIX is fine


@pytest.yield_fixture(autouse=True)
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    if sys.platform != "win32":
        asyncio.set_event_loop(None)  # type: ignore # see https://github.com/pytest-dev/pytest-asyncio/issues/73
    loop = get_event_loop()
    if sys.platform != "win32":
        # on UNIX we also need to attach the loop to the child watcher for asyncio.subprocess
        policy = asyncio.get_event_loop_policy()
        watcher = asyncio.SafeChildWatcher()  # type: ignore # undocumented?
        watcher.attach_loop(loop)
        policy.set_child_watcher(watcher)
    try:
        yield loop
    finally:
        loop.close()


requires_manual_testing = pytest.mark.skipif(MANUAL_TESTING == False,
                                        reason="This test can't run without MANUAL_TESTING")
