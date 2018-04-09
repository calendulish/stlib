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

import os
import sys
from distutils.core import Extension, setup
from distutils.sysconfig import get_python_lib
from typing import List, Mapping, Tuple

if sys.maxsize > 2 ** 32:
    arch = 64
else:
    arch = 32

PACKAGE_PATH = os.path.join(get_python_lib(), 'stlib')
SOURCES_PATH = os.path.join('stlib', 'steam_api')
SDK_PATH = os.path.join(SOURCES_PATH, 'steamworks_sdk')
HEADERS_PATH = os.path.join(SDK_PATH, 'public')

if os.name == 'nt':
    if arch == 64:
        REDIST_PATH = os.path.join(SDK_PATH, 'redistributable_bin', 'win64')
        API_NAME = 'steam_api64'
    else:
        REDIST_PATH = os.path.join(SDK_PATH, 'redistributable_bin')
        API_NAME = 'steam_api'
elif os.name == 'posix':
    API_NAME = 'libsteam_api'

    if arch == 64:
        REDIST_PATH = os.path.join(SDK_PATH, 'redistributable_bin', 'linux64')
    else:
        REDIST_PATH = os.path.join(SDK_PATH, 'redistributable_bin', 'linux32')
else:
    print('Your system is currently not supported.')
    sys.exit(1)


def fix_runtime_path() -> Mapping[str, List[str]]:
    if os.name == 'posix':
        return {'runtime_library_dirs': [PACKAGE_PATH]}
    else:
        return {}


def fix_linker() -> Mapping[str, List[str]]:
    if os.name == 'nt':
        return {'libraries': [API_NAME]}
    else:
        return {}


def include_extra_libraries() -> Mapping[str, List[Tuple[str, List[str]]]]:
    if os.name == 'nt':
        library = [os.path.join(REDIST_PATH, f'{API_NAME}.dll')]
    else:
        library = [os.path.join(REDIST_PATH, f'{API_NAME}.so')]

    return {'data_files': [(PACKAGE_PATH, library)]}


steam_api = Extension(
    'stlib.steam_api',
    sources=[os.path.join(SOURCES_PATH, 'steam_api.cpp')],
    include_dirs=[SOURCES_PATH, HEADERS_PATH],
    library_dirs=[REDIST_PATH],
    extra_compile_args=['-D_CRT_SECURE_NO_WARNINGS'],
    **fix_runtime_path(),
    **fix_linker()
)

setup(
    name='stlib',
    version='0.0.0-DEV',
    description="Async library that provides features related to Steam client and compatible stuffs",
    author='Lara Maia',
    author_email='dev@lara.click',
    url='http://github.com/ShyPixie/stlib',
    license='GPL',
    packages=['stlib'],
    ext_modules=[steam_api],
    requires=['aiodns',
              'aiohttp',
              'asyncio',
              'beautifulsoup4',
              'cchardet',
              'ujson',
              ],
    **include_extra_libraries()
)
