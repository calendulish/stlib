#!/usr/bin/env python
#
# Lara Maia <dev@lara.monster> 2015 ~ 2021
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
import sys
from typing import Generator

import pytest


@pytest.fixture()
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    try:
        yield loop
    finally:
        loop.run_until_complete(asyncio.sleep(3))  # see https://github.com/aio-libs/aiohttp/issues/1925
        loop.close()
