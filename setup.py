#!/usr/bin/env python
#
# Lara Maia <dev@lara.monster> 2015 ~ 2023
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
import platform
import shutil
import sys

from setuptools import Extension, setup, find_packages
from setuptools.command.build_ext import build_ext
from pathlib import Path

SOURCES_PATH = Path(os.getenv("SOURCES_PATH", Path('src', 'steamworks')))
SDK_PATH = Path(os.getenv("SDK_PATH", Path(SOURCES_PATH, 'sdk')))
HEADERS_PATH = Path(os.getenv("HEADERS_PATH", Path(SDK_PATH, 'public')))

arch = '64' if sys.maxsize > 2 ** 32 else ''
if os.name == 'nt':
    REDIST_PATH = f'win{arch}'
    API_NAME = f'steam_api{arch}'
    EXTRA_NAME = f'{API_NAME}.dll'
elif os.name == 'posix':
    REDIST_PATH = f'linux{arch}' if arch else '32'
    API_NAME = 'steam_api'
    EXTRA_NAME = f'lib{API_NAME}.so'
else:
    print('Your system is currently not supported.')
    sys.exit(1)


class OptionalBuild(build_ext):
    def run(self):
        bin_path = SDK_PATH / 'redistributable_bin'
        output_dir = Path(self.build_lib) / 'stlib'
        output_dir.mkdir(parents=True, exist_ok=True)
        compatible = platform.machine().lower() in ['x86_64', 'amd64', 'i386', 'x86']

        if compatible and HEADERS_PATH.exists():
            shutil.copy(
                bin_path / REDIST_PATH / EXTRA_NAME,
                output_dir,
            )
            super().run()
        else:
            self.warn("build of steam_api C extension has been disabled")


all_sources = [
    str(file) for file in SOURCES_PATH.iterdir() if file.suffix == ".cpp"
]
steamworks = Extension(
    'stlib.steamworks',
    sources=all_sources,
    include_dirs=[SOURCES_PATH, HEADERS_PATH],
    library_dirs=[str(SDK_PATH / 'redistributable_bin' / REDIST_PATH)],
    libraries=[API_NAME],
    extra_compile_args=['-D_CRT_SECURE_NO_WARNINGS', '/std:c++17' if 'MSC' in sys.version else '-std=c++17'],
)

setup(
    ext_modules=[steamworks],
    cmdclass={"build_ext": OptionalBuild},  # type: ignore
)
