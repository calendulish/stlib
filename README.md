stlib
-----

[![windows build status](https://badges.lara.monster/ShyPixie/badge-metadata/stlib-windows-build)](https://github.com/ShyPixie/stlib/actions/workflows/build.yml)
[![linux build status](https://badges.lara.monster/ShyPixie/badge-metadata/stlib-linux-build)](https://github.com/ShyPixie/stlib/actions/workflows/build.yml)
[![Coverage](https://codecov.io/gh/ShyPixie/stlib/branch/master/graph/badge.svg?token=DMKFKEUUZP)](https://codecov.io/gh/ShyPixie/stlib)
[![Quality](https://api.codiga.io/project/33228/score/svg)](https://app.codiga.io/project/33228/dashboard)
[![GitHub license](https://img.shields.io/badge/license-GPLv3-brightgreen.svg?style=flat)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Donate](https://img.shields.io/badge/Donate-PayPal-brightgreen.svg?style=flat)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=WVQ5XM935XNLN&item_name=python-template)

Async library that provides features related to Steam client and compatible stuff

WARNING: stlib is not intended to be used in game development, there is no support to callbacks and I'll not work on that.
stlib is intended to develop console or GUI applications that need interaction with SteamAPI or SteamWebAPI.

stlib now supports plugins!
---------------------------
See more at: [stlib-plugins](https://github.com/ShyPixie/stlib-plugins)

Dependencies to build SteamAPI C Extension (Optional)
-----------------------------------------------------

WARNING: SteamAPI C Extension is incomplete, but it's easy to implement. if you need a feature that is not present,
send a pull request or open an issue.

- Python and headers >= 3.6
- Microsoft Visual C++ compiler (MSVC) or GNU Compiler (GCC)
- Steamworks SDK >= v1.51

Dependencies to run
-------------------

- Python >= 3.6
- asyncio
- beautifulsoup4
- rsa
- aiohttp


API Reference
-------------

https://lara.monster/stlib

Made with stlib
---------------

Steam Tools NG - https://github.com/ShyPixie/steam-tools-ng

___________________________________________________________________________________________

This is an work in progress. You can request new features.

The stlib is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

The stlib is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

Lara Maia <dev@lara.monster> 2015 ~ 2022

[![Made with](https://img.shields.io/badge/made%20with-girl%20power-f070D0.svg?longCache=true&style=for-the-badge)](https://lara.monster)
