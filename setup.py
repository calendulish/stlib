#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015 ~ 2018
#
# The Steam Tools is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# The Steam Tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#
# FIXME: STUB

import os
import sys
from distutils.core import setup

if sys.maxsize > 2 ** 32:
    libdir = 'lib64'
else:
    libdir = 'lib32'

if os.name == 'nt':
    data_files = [('', [os.path.join('redist', libdir, 'libsteam_api.dll')])]
else:
    data_files = [('', [os.path.join('redist', libdir, 'libsteam_api.so')])]

setup(
        name='Steam Tools',
        version='0.0.0-DEV',
        description="Async library that provides features related to steam client and compatible stuffs",
        author='Lara Maia',
        author_email='dev@lara.click',
        url='http://github.com/ShyPixie/stlib',
        license='GPL',
        data_files=data_files,
        packages=['stlib'],
        requires=['aiodns',
                  'aiohttp',
                  'asyncio',
                  'beautifulsoup4',
                  'cchardet',
                  'ujson',
                  ],
)
