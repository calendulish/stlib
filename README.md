stlib
-----

[![windows build status](https://badges.lara.monster/ShyPixie/.github/stlib-windows-build)](https://github.com/ShyPixie/stlib/actions/workflows/build.yml)
[![linux build status](https://badges.lara.monster/ShyPixie/.github/stlib-linux-build)](https://github.com/ShyPixie/stlib/actions/workflows/build.yml)
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

Dependencies to build SteamWorks Python Extension (Optional)
-----------------------------------------------------

WARNING: SteamWorks Python Extension is incomplete, but it's easy to implement. if you need a feature that is not present,
send a pull request or open an issue.

- Python and headers >= 3.9
- Microsoft Visual C++ compiler (MSVC) or GNU Compiler (GCC)
- Steamworks SDK >= v1.55

Dependencies to run
-------------------

- Python >= 3.9
- asyncio
- beautifulsoup4
- rsa
- aiohttp


API Reference & Documentation
-----------------------------

[Current Version (>=1.0)](https://lara.monster/stlib)

:warning: **If you are using the legacy version** please update.
The legacy version isn't maintained or supported and docs are
available only to help you in the upgrade process to latest version.
[Legacy Version (<=0.14)](https://lara.monster/stlib.legacy)

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
