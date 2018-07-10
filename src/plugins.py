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

import contextlib
from types import ModuleType

import pkg_resources


class PluginNotFoundError(KeyError): pass


__plugins__ = {}

for entry_point in pkg_resources.iter_entry_points("stlib_plugins"):
    with contextlib.suppress(pkg_resources.VersionConflict):
        __plugins__[entry_point.name] = entry_point.load()


def get_plugin(name: str) -> ModuleType:
    try:
        _module = __plugins__[name]
    except KeyError:
        raise PluginNotFoundError() from None

    return _module
