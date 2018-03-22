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

if sys.maxsize > 2 ** 32:
    arch = 64
else:
    arch = 32

SDK_PATH = os.path.join('steam_api', 'steamworks_sdk')
HEADERS_PATH = os.path.join(SDK_PATH, 'public', 'steam')

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

steam_api = Extension(
        'steam_api',
        sources=[os.path.join('steam_api', 'steam_api.cpp')],
        include_dirs=[HEADERS_PATH],
        library_dirs=[REDIST_PATH],
        libraries=[API_NAME],
        extra_compile_args=['-D_CRT_SECURE_NO_WARNINGS'],
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
        data_files=[(get_python_lib(), [os.path.join(REDIST_PATH, f'{API_NAME}.dll')])],
        ext_modules=[steam_api],
        requires=['aiodns',
                  'aiohttp',
                  'asyncio',
                  'beautifulsoup4',
                  'cchardet',
                  'ujson',
                  ],
)
