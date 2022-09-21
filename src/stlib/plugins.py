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
`plugins` interface is used to import and use stlib plugins

Example:

```
from stlib import plugins

if plugins.has_plugin('indiegala'):
    indiegala = plugins.get_plugin('indiegala')
    indiegala.do_login()
```
"""

import glob
import importlib.machinery
import importlib.util
import logging
import os
import sys
from types import ModuleType
from typing import Tuple, Dict, Optional, Callable, Any, List, Union

log = logging.getLogger(__name__)
manager: Optional['_Manager'] = None
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


class _Plugin:
    def __init__(self, headers: Optional[Dict[str, str]] = None) -> None:
        self._headers = headers
        self._session_index = 0

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init__(cls, **kwargs)
        _Manager.plugins[cls.__module__] = [None, cls.__name__]

    def __getattr__(self, item: str) -> Any:
        module = _Manager.plugins[self.__module__][0]

        if hasattr(module, item):
            return getattr(module, item)

        raise AttributeError(f"{self} object has no attribute {item}")

    @property
    def headers(self) -> Dict[str, str]:
        if not self._headers:
            self._headers = self.session.headers

        assert isinstance(self._headers, dict)
        return self._headers


class _Manager:
    plugins: Dict[str, List[Union[Optional[ModuleType], str]]] = {}

    def __init__(self, module_search_paths: Tuple[str, ...] = default_search_paths) -> None:
        self._module_search_paths = module_search_paths

        for plugin_directory in self._module_search_paths:
            if not os.path.isdir(plugin_directory):
                log.debug("Unable to find plugin directory in:\n%s", plugin_directory)
                continue

            for full_path in glob.glob(os.path.join(plugin_directory, '*.py*')):
                module_name = os.path.basename(full_path).split('.')[0]
                log.debug("%s found at %s", module_name, full_path)
                plugin_spec = importlib.util.spec_from_file_location(module_name, full_path)
                assert isinstance(plugin_spec, importlib.machinery.ModuleSpec), "No module spec?"
                module_ = importlib.util.module_from_spec(plugin_spec)

                try:
                    plugin_spec.loader.exec_module(module_)  # type: ignore
                except ImportError as exception:
                    raise PluginLoaderError(exception)

                log.debug("Plugin %s loaded.", module_name)
                self.plugins[module_.__name__][0] = module_

    def has_plugin(self, plugin_name: str) -> bool:
        return plugin_name in self.plugins

    def get_plugin(self, plugin_name: str, *args: Any, **kwargs: Any) -> Any:
        _module = self.plugins[plugin_name][0]
        _name = self.plugins[plugin_name][1]
        assert isinstance(_module, ModuleType), "Wrong module type"
        assert isinstance(_name, str), "Wrong module name"
        plugin = getattr(_module, _name)
        return plugin(*args, **kwargs)


def _plugin_manager(
        function: Callable[..., Any],
        plugin_search_paths: Tuple[str, ...] = default_search_paths,
) -> Callable[..., Any]:
    global manager

    if not manager:
        log.debug("Creating a new plugin manager")
        manager = _Manager(plugin_search_paths)
    else:
        log.debug("Using existent plugin manager")

    return function


@_plugin_manager
def has_plugin(plugin_name: str) -> bool:
    """
    Check if plugin is available by name
    :param plugin_name: Plugin name to look up
    :return: True if available
    """
    assert isinstance(manager, _Manager), "Plugin manager not initialized"
    return manager.has_plugin(plugin_name)


@_plugin_manager
def get_plugin(plugin_name: str) -> Any:
    """
    Get plugin from plugin name
    :param plugin_name: Plugin name to look up
    :return: `_Plugin`
    """
    assert isinstance(manager, _Manager), "Plugin manager not initialized"
    return manager.get_plugin(plugin_name)
