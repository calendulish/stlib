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
import os
import shutil
import sys

from setuptools import Extension, setup, find_packages
from setuptools.command.build_ext import build_ext
from pathlib import Path

SOURCES_PATH = Path(os.getenv("SOURCES_PATH", Path('src', 'steamworks')))
SDK_PATH = Path(os.getenv("SDK_PATH", Path(SOURCES_PATH, 'sdk')))
HEADERS_PATH = Path(os.getenv("HEADERS_PATH", Path(SDK_PATH, 'public')))

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
        bin_path = SDK_PATH / 'redistributable_bin'
        output_dir = Path(self.build_lib) / 'stlib'
        output_dir.mkdir(parents=True, exist_ok=True)

        if HEADERS_PATH.exists():
            shutil.copy(
                bin_path / REDIST_PATH / EXTRA_NAME,
                output_dir,
            )
            super().run()
        else:
            self.warn("build of steam_api C extension has been disabled")


all_sources = []
for file in SOURCES_PATH.iterdir():
    if file.suffix == ".cpp":
        all_sources.append(str(file))

steamworks = Extension(
    'stlib.steamworks',
    sources=all_sources,
    include_dirs=[SOURCES_PATH, HEADERS_PATH],
    library_dirs=[str(SDK_PATH / 'redistributable_bin' / REDIST_PATH)],
    libraries=[API_NAME],
    extra_compile_args=['-D_CRT_SECURE_NO_WARNINGS', '/std:c++17' if 'MSC' in sys.version else '-std=c++17'],
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
    version='1.0',
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
    ext_modules=[steamworks],
    install_requires=[
        'aiohttp',
        'beautifulsoup4',
        'rsa',
    ],
    python_requires='>=3.9',
    cmdclass={"build_ext": OptionalBuild},  # type: ignore
    zip_safe=False,
)
