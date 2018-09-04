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
import sys
from typing import Any

import pkg_resources

log = logging.getLogger(__name__)


class PluginNotFoundError(KeyError): pass


class IncompatiblePluginError(AttributeError): pass


__plugins__ = {}

for entry_point in pkg_resources.iter_entry_points("stlib_plugins"):
    try:
        __plugins__[entry_point.name] = entry_point.load()
        setattr(sys.modules[__name__], entry_point.name, __plugins__[entry_point.name])
        log.info("Plugin loaded: %s", entry_point.name)
    except pkg_resources.VersionConflict:
        log.warning("Incompatible plugin: %s", entry_point.name)


def get_plugin(name: str, *args: Any, **kwargs: Any) -> Any:
    try:
        _module = __plugins__[name]
    except KeyError:
        raise PluginNotFoundError() from None

    try:
        return _module.Main(*args, **kwargs)
    except AttributeError:
        raise IncompatiblePluginError() from None


def has_plugin(name: str) -> bool:
    if name in __plugins__:
        return True
    else:
        return False
