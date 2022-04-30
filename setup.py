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
import shutil
import sys

import logging
import os
import sysconfig
from setuptools import Extension, setup, find_packages
from setuptools.command.build_ext import build_ext
from typing import List, Mapping

SOURCES_PATH = os.getenv("SOURCES_PATH", os.path.join('src', 'steam_api'))
SDK_PATH = os.getenv("SDK_PATH", os.path.join(SOURCES_PATH, 'steamworks_sdk', 'sdk'))
HEADERS_PATH = os.getenv("HEADERS_PATH", os.path.join(SDK_PATH, 'public'))

if sys.maxsize > 2 ** 32:
    arch = '64'
else:
    arch = ''

if os.name == 'nt':
    REDIST_PATH = 'win' + arch
    API_NAME = 'steam_api' + arch
    EXTRA_NAME = API_NAME + '.dll'
elif os.name == 'posix':
    REDIST_PATH = 'linux' + arch if arch else '32'
    API_NAME = 'steam_api'
    EXTRA_NAME = 'lib' + API_NAME + '.so'
else:
    print('Your system is currently not supported.')
    sys.exit(1)


class OptionalBuild(build_ext):
    def run(self):
        bin_path = os.path.join(SDK_PATH, 'redistributable_bin')
        output_dir = os.path.join(self.build_lib, 'stlib')
        os.makedirs(output_dir, exist_ok=True)

        if os.path.exists(HEADERS_PATH):
            shutil.copy(
                os.path.join(bin_path, REDIST_PATH, EXTRA_NAME),
                output_dir,
            )
            super().run()
        else:
            self.warn("build of steam_api C extension has been disabled")


steam_api = Extension(
    'stlib.steam_api',
    sources=[os.path.join(SOURCES_PATH, 'steam_api.cpp')],
    include_dirs=[SOURCES_PATH, HEADERS_PATH],
    library_dirs=[os.path.join(SDK_PATH, 'redistributable_bin', REDIST_PATH)],
    libraries=[API_NAME],
    extra_compile_args=['-D_CRT_SECURE_NO_WARNINGS'],
)

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Games/Entertainment',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Microsoft :: Windows',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Typing :: Typed',
]

setup(
    name='stlib',
    version='0.14.1',
    description="Async library that provides features related to Steam client and compatible stuffs",
    author='Lara Maia',
    author_email='dev@lara.monster',
    url='http://github.com/ShyPixie/stlib',
    license='GPLv3',
    classifiers=classifiers,
    keywords='steam valve',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    ext_modules=[steam_api],
    install_requires=[
        'aiohttp',
        'beautifulsoup4',
        'rsa',
    ],
    python_requires='>=3.7',
    cmdclass={"build_ext": OptionalBuild},
    zip_safe=False,
)
