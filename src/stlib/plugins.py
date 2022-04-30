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

import glob
import importlib.machinery
import importlib.util
import logging
import os
import sys
from types import ModuleType
from typing import Tuple, Dict, Optional, Callable, Any, List, Union

from . import webapi

log = logging.getLogger(__name__)
manager: Optional['Manager'] = None
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


class PluginError(Exception):
    """Base exception for plugin exceptions"""
    pass


class PluginNotFoundError(PluginError):
    """Raised when a plugin can't be found"""
    pass


class PluginLoaderError(PluginError):
    """Raised when a plugin can't be loaded"""
    pass


class Plugin:
    def __init__(self, headers: Optional[Dict[str, str]] = None) -> None:
        self._headers = headers
        self._session_index = 0

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init__(cls, **kwargs)
        Manager.plugins[cls.__module__] = [None, cls.__name__]

    def __getattr__(self, item: str) -> Any:
        module = Manager.plugins[self.__module__][0]

        if hasattr(module, item):
            return getattr(module, item)

        raise AttributeError(f"{self} object has no attribute {item}")

    @property
    def headers(self) -> Dict[str, str]:
        if not self._headers:
            self._headers = self.session.headers

        return self._headers

    @property
    def session(self) -> webapi.SteamWebAPI:
        return webapi.get_session(self._session_index)

    @session.setter
    def session(self, index: int) -> None:
        self._session_index = index


class Manager:
    plugins: Dict[str, List[Union[Optional[ModuleType], str]]] = {}

    def __init__(self, module_search_paths: Tuple[str, ...] = default_search_paths) -> None:
        self._module_search_paths = module_search_paths

        for plugin_directory in self._module_search_paths:
            if not os.path.isdir(plugin_directory):
                log.debug(f"Unable to find plugin directory in:\n{plugin_directory}")
                continue

            for full_path in glob.glob(os.path.join(plugin_directory, '*.py*')):
                module_name = os.path.basename(full_path).split('.')[0]
                log.debug(f"{module_name} found at {full_path}")
                plugin_spec = importlib.util.spec_from_file_location(module_name, full_path)
                module_ = importlib.util.module_from_spec(plugin_spec)

                try:
                    plugin_spec.loader.exec_module(module_)  # type: ignore
                except ImportError as exception:
                    raise PluginLoaderError(exception)

                log.debug(f"Plugin {module_name} loaded.")
                self.plugins[module_.__name__][0] = module_

    def has_plugin(self, plugin_name: str) -> bool:
        if plugin_name in self.plugins.keys():
            return True
        else:
            return False

    def get_plugin(self, plugin_name: str, *args, **kwargs) -> Any:
        plugin = getattr(self.plugins[plugin_name][0], self.plugins[plugin_name][1])
        return plugin(*args, **kwargs)


def plugin_manager(
        function: Callable[..., Any],
        plugin_search_paths: Tuple[str, ...] = default_search_paths,
) -> Callable[..., Any]:
    global manager

    if not manager:
        log.debug("Creating a new plugin manager")
        manager = Manager(plugin_search_paths)
    else:
        log.debug(f"Using existent plugin manager")

    return function


@plugin_manager
def has_plugin(plugin_name: str) -> bool:
    return manager.has_plugin(plugin_name)


@plugin_manager
def get_plugin(plugin_name: str) -> Any:
    return manager.get_plugin(plugin_name)
