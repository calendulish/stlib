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

import glob
import importlib.machinery
import importlib.util
import logging
import os
import sys
from types import ModuleType
from typing import Tuple, Dict

log = logging.getLogger(__name__)

default_search_paths: Tuple[str, ...]

if hasattr(sys, 'frozen') or os.name == 'nt':
    default_search_paths = (
        os.path.join(os.getcwd(), 'plugins'),
        os.path.join(os.environ["LOCALAPPDATA"], 'stlib', 'plugins'),
    )
else:
    default_search_paths = (
        os.path.join(os.getcwd(), 'plugins'),
        os.path.abspath(os.path.join(os.path.sep, 'usr', 'share', 'stlib', 'plugins')),
        os.path.join(os.environ['HOME'], '.local', 'share', 'stlib', 'plugins'),
    )


class PluginError(Exception): pass


class PluginNotFoundError(PluginError): pass


class PluginLoaderError(PluginError): pass


class Manager:
    def __init__(self, plugin_search_paths: Tuple[str, ...] = default_search_paths) -> None:
        self._plugin_search_paths = plugin_search_paths
        self._available_plugins: Dict[str, importlib.machinery.ModuleSpec] = {}
        self._loaded_plugins: Dict[str, ModuleType] = {}

        for plugin_directory in self._plugin_search_paths:
            if not os.path.isdir(plugin_directory):
                log.debug(f"Unable to find plugin directory in:\n{plugin_directory}")
                continue

            for full_path in glob.glob(os.path.join(plugin_directory, '*.py*')):
                plugin_name = os.path.basename(full_path).split('.')[0]
                plugin_spec = importlib.util.spec_from_file_location(plugin_name, full_path)
                self._available_plugins[plugin_name] = plugin_spec
                log.debug(f'Plugin {plugin_name} registered.')

    @property
    def available_plugins(self) -> Tuple[str, ...]:
        return tuple(self._available_plugins.keys())

    @property
    def loaded_plugins(self) -> Tuple[str, ...]:
        return tuple(self._loaded_plugins.keys())

    def has_plugin(self, plugin_name: str) -> bool:
        if plugin_name in self._available_plugins.keys():
            return True
        else:
            return False

    def load_plugin(self, plugin_name: str) -> ModuleType:
        if plugin_name in self._loaded_plugins.keys():
            log.warning(f"Plugin {plugin_name} is already loaded. Skipping.")
            return self._loaded_plugins[plugin_name]

        elif plugin_name in self._available_plugins.keys():
            plugin_spec = self._available_plugins[plugin_name]
            module_ = importlib.util.module_from_spec(plugin_spec)
            plugin_spec.loader.exec_module(module_)  # type: ignore
            self._loaded_plugins[plugin_name] = module_
        else:
            raise PluginNotFoundError(f"Unable to find a plugin named {plugin_name}.")

        return module_

    def unload_plugin(self, plugin_name: str) -> None:
        if plugin_name in self._loaded_plugins.keys():
            del self._loaded_plugins[plugin_name]
        else:
            raise PluginLoaderError(f"Plugin {plugin_name} is not loaded.")
