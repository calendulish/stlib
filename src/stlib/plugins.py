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
import functools
import glob
import importlib.machinery
import importlib.util
import logging
import os
import sys
from types import ModuleType, MappingProxyType
from typing import Tuple, Dict, Optional, Callable, Any, List

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


class _Manager:
    def __init__(self, custom_search_paths: Tuple[str, ...] = ()) -> None:
        self._module_search_paths = custom_search_paths + default_search_paths
        self._plugins: Dict[str, ModuleType] = {}

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
                self._plugins[module_.__name__] = module_

    @property
    def plugins(self) -> MappingProxyType[str, ModuleType]:
        return MappingProxyType(self._plugins)

    def has_plugin(self, plugin_name: str) -> bool:
        return plugin_name in self._plugins

    def get_plugin(self, plugin_name: str) -> ModuleType:
        _module = self._plugins[plugin_name]
        assert isinstance(_module, ModuleType), "Wrong module type"
        return _module


def _plugin_manager(function: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        global manager

        if not manager:
            log.debug("Creating a new plugin manager")
            manager = _Manager()
        else:
            log.debug("Using existent plugin manager")

        return function(*args, **kwargs)

    return wrapper


def add_search_paths(*paths: str) -> None:
    """
    Add `paths` to plugin search paths.
    Must be called before use any method from `plugins` module.
    The custom search paths will take precedence over default search paths.
    :param paths: The paths you want to include
    :return: None
    """
    global manager

    if manager:
        raise RuntimeError("Can't change search path after plugin manager initialization")

    manager = _Manager(tuple(paths))


@_plugin_manager
def get_available_plugins() -> List[str]:
    """
    Return a list of available plugins
    :return: list of available plugins
    """
    return list(manager.plugins.keys())


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
    :return: plugin module requested
    """
    assert isinstance(manager, _Manager), "Plugin manager not initialized"
    return manager.get_plugin(plugin_name)
