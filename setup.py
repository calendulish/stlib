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
import os
import sys
from distutils.command.build import build
from distutils.command.install_data import install_data
from distutils.sysconfig import get_python_lib
from typing import List, Mapping

from setuptools import Extension, setup
from setuptools.command.install import install

if sys.maxsize > 2 ** 32:
    arch = 64
else:
    arch = 32

PACKAGE_PATH = os.path.join(get_python_lib(), 'stlib')
SOURCES_PATH = os.path.join('src', 'steam_api')
SDK_PATH = os.path.join(SOURCES_PATH, 'steamworks_sdk')
HEADERS_PATH = os.path.join(SDK_PATH, 'public')

DISABLE_STEAM_API = False

if os.name == 'nt':
    DATA_DIR = PACKAGE_PATH

    if arch == 64:
        REDIST_PATH = os.path.join(SDK_PATH, 'redistributable_bin', 'win64')
        API_NAME = 'steam_api64'
    else:
        REDIST_PATH = os.path.join(SDK_PATH, 'redistributable_bin')
        API_NAME = 'steam_api'

    EXTRA_PREBUILT = (PACKAGE_PATH, [os.path.join(REDIST_PATH, f'{API_NAME}.dll')])
elif os.name == 'posix':
    DATA_DIR = os.path.abspath(os.path.join(os.path.sep, 'opt', 'stlib'))
    API_NAME = 'steam_api'

    if arch == 64:
        REDIST_PATH = os.path.join(SDK_PATH, 'redistributable_bin', 'linux64')
    else:
        REDIST_PATH = os.path.join(SDK_PATH, 'redistributable_bin', 'linux32')

    EXTRA_PREBUILT = (os.path.join(DATA_DIR, 'lib'), [os.path.join(REDIST_PATH, f'lib{API_NAME}.so')])
else:
    print('Your system is currently not supported.')
    sys.exit(1)


def fix_runtime_path() -> Mapping[str, List[str]]:
    if os.name == 'posix':
        return {'runtime_library_dirs': [os.path.join(DATA_DIR, 'lib')]}
    else:
        return {}


steam_api = Extension(
    'stlib.steam_api',
    sources=[os.path.join(SOURCES_PATH, 'steam_api.cpp')],
    include_dirs=[SOURCES_PATH, HEADERS_PATH],
    library_dirs=[REDIST_PATH],
    libraries=[API_NAME],
    extra_compile_args=['-D_CRT_SECURE_NO_WARNINGS'],
    **fix_runtime_path()
)

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Games/Entertainment',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3.6',
]


class OptionalBuild(build):
    build.user_options.append(('disable-steam-api', None, 'disable SteamAPI C Extension'))

    # noinspection PyAttributeOutsideInit
    def initialize_options(self):
        build.initialize_options(self)
        self.disable_steam_api = DISABLE_STEAM_API

    def run(self):
        global DISABLE_STEAM_API
        DISABLE_STEAM_API = self.disable_steam_api

        for cmd_name in self.get_sub_commands():
            if cmd_name == 'build_ext':
                if DISABLE_STEAM_API:
                    self.warn('You disable build of SteamAPI C Extension by command line parameters')
                    continue
                elif not os.path.isfile(os.path.join(SDK_PATH, 'public', 'steam', 'steam_api.h')):
                    raise FileNotFoundError(
                        f'Unable to find a valid Steamworks SDK in {SDK_PATH}\n'
                        '(Did you want to use --disable-steam-api?)'
                    )

            self.run_command(cmd_name)


class OptionalData(install_data):
    def run(self):
        if glob.glob(os.path.join('build', '**', '*.o'), recursive=True):
            install_data.run(self)


class InstallWithoutBuild(install):
    # noinspection PyAttributeOutsideInit
    def initialize_options(self):
        install.initialize_options(self)
        self.skip_build = True

    def run(self):
        install.run(self)


setup(
    name='stlib',
    version='0.8.0',
    description="Async library that provides features related to Steam client and compatible stuffs",
    author='Lara Maia',
    author_email='dev@lara.click',
    url='http://github.com/ShyPixie/stlib',
    license='GPL',
    classifiers=classifiers,
    keywords='steam valve',
    packages=['stlib'],
    package_dir={'stlib': 'src'},
    ext_modules=[steam_api],
    data_files=[EXTRA_PREBUILT],
    requires=['aiohttp',
              'asyncio',
              'beautifulsoup4',
              'rsa',
              'setuptools',
              ],
    python_requires='>=3.6',
    zip_safe=False,
    cmdclass={
        'build': OptionalBuild,
        'install_data': OptionalData,
        'install': InstallWithoutBuild,
    },
)
