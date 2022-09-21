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
stlib
-----

Async library that provides features related to Steam client and compatible stuff

WARNING: stlib is not intended to be used in game development.
There is no support to callbacks and I'll not work on that.
stlib is intended to develop console or GUI applications that need interaction with SteamAPI or SteamWebAPI.

stlib now supports plugins!
---------------------------
See more at: [stlib-plugins](https://github.com/ShyPixie/stlib-plugins)

Dependencies to build SteamWorks Python Extension (Optional)
-----------------------------------------------------

WARNING: SteamWorks Python Extension is incomplete, but it's easy to implement.
If you need a feature that is not present, send a pull request or open an issue.

- Python and headers >= 3.9
- Microsoft Visual C++ compiler (MSVC) or GNU Compiler (GCC)
- Steamworks SDK >= v1.55

Dependencies to run
-------------------

- Python >= 3.9
- asyncio
- beautifulsoup4
- rsa
- aiohttp

Made with stlib
---------------

Steam Tools NG - https://github.com/ShyPixie/steam-tools-ng

___________________________________________________________________________________________

This is an work in progress. You can request new features.

The stlib is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

The stlib is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.
If not, see http://www.gnu.org/licenses/.

Lara Maia <dev@lara.monster> 2015 ~ 2022

"""

import os
import site
import sys
from contextlib import suppress

from ctypes import cdll

# noinspection PyUnresolvedReferences
__all__ = ["steamworks"]

try:
    # noinspection PyUnresolvedReferences
    from stlib import steamworks
except ImportError:
    steamworks_available = False
else:
    steamworks_available = True


class NoSteamWorksError(ImportError):
    """Raised when stlib was compiled without SteamWorks support"""
    pass


if sys.platform == 'win32' and sys.version_info > (3, 7):
    for site_packages in site.getsitepackages():
        os.add_dll_directory(site_packages)

if sys.platform == 'linux':
    with suppress(OSError):
        cdll.LoadLibrary(os.path.join(site.getusersitepackages(), 'stlib', 'libsteam_api.so'))

    for site_packages in site.getsitepackages():
        with suppress(OSError):
            cdll.LoadLibrary(os.path.join(site_packages, 'stlib', 'libsteam_api.so'))
