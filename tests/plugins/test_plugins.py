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

from stlib import plugins

with contextlib.suppress(ImportError):
    pass

# noinspection PyUnresolvedReferences
from tests import debug


class TestPlugins:
    manager = plugins.Manager()

    def test_plugins(self) -> None:
        for plugin in self.manager.available_plugins:
            debug(f"Testing plugin {plugin}")

            assert self.manager.has_plugin(plugin) is True

            assert isinstance(self.manager.load_plugin(plugin), ModuleType)

            assert plugin in self.manager.loaded_plugins

            assert self.manager.unload_plugin(plugin) is None
