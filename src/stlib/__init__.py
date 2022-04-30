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

import os
import site
import sys
from contextlib import suppress

from ctypes import cdll

__all__ = ["steam_api"]

if os.name == 'nt' and sys.version_info.minor > 7:
    for site_packages in site.getsitepackages():
        os.add_dll_directory(site_packages)

if sys.platform == 'linux':
    with suppress(OSError):
        cdll.LoadLibrary(os.path.join(site.getusersitepackages(), 'stlib', 'libsteam_api.so'))

    for site_packages in site.getsitepackages():
        with suppress(OSError):
            cdll.LoadLibrary(os.path.join(site_packages, 'stlib', 'libsteam_api.so'))