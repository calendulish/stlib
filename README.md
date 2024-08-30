stlib
-----

[![windows build status](https://badges.lara.monster/calendulish/.github/stlib-windows-build)](https://github.com/calendulish/stlib/actions/workflows/build.yml)
[![linux build status](https://badges.lara.monster/calendulish/.github/stlib-linux-build)](https://github.com/calendulish/stlib/actions/workflows/build.yml)
[![Coverage](https://codecov.io/gh/calendulish/stlib/branch/master/graph/badge.svg?token=DMKFKEUUZP)](https://codecov.io/gh/calendulish/stlib)
[![GitHub license](https://img.shields.io/badge/license-GPLv3-brightgreen.svg?style=flat)](https://www.gnu.org/licenses/gpl-3.0.html)
[![GitHub release](https://img.shields.io/github/release/calendulish/stlib.svg?style=flat)](https://github.com/calendulish/stlib/releases)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/8033/badge)](https://www.bestpractices.dev/projects/8033)

Async library that provides features related to Steam client and compatible stuff.

stlib isn't a library intended for game development like SteamWorksPy, instead you should use it for console, gui, and web applications that need to gather Steam data in some way, including the ones from current logged in user. In addition to the SteamWorks methods, stlib also implements access to SteamWebAPI and some internal community APIs, and works both on Linux and Windows.

There's also support for plugins that interact with third-party platforms, as an example we have the SteamGifts plugin that can login into the service using the Steam account configured on the stlib and access the user data from the third-party website. You can also write your own plugin for your favorite service using the stlib helpers.

For more info about plugins, see the [stlib-plugins](https://github.com/calendulish/stlib-plugins) repo. a stlib [documentation](https://lara.monster/stlib) is also available.

I'm programming this library as a personal project, so the functions are added according to my needs, otherwise it would be impossible to do it alone. If you need anything else, send a pull request or open an issue.

stlib now supports plugins!
---------------------------
See more at: [stlib-plugins](https://github.com/calendulish/stlib-plugins)

Dependencies to build SteamWorks Python Extension (Optional)
-----------------------------------------------------

- Python and headers >= 3.10
- Microsoft Visual C++ compiler (MSVC) or GNU Compiler (GCC)
- Steamworks SDK >= v1.55

Dependencies to run
-------------------

- Python >= 3.10
- asyncio
- beautifulsoup4
- rsa
- aiohttp


API Reference & Documentation
-----------------------------

[Current Version (>=2.0)](https://lara.monster/stlib)

Made with stlib
---------------

[Steam Tools NG](https://github.com/calendulish/steam-tools-ng)

___________________________________________________________________________________________

This is a work in progress. You can request new features.

The stlib is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

The stlib is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

Lara Maia <dev@lara.monster> 2015 ~ 2024

[![OpenSSF Best Practices](https://www.bestpractices.dev/assets/openssf_bestpracticesbadge-bcc69832741d2cb3979607a9d713f9e8f83987653caa7b982d75ad1362cd575b.svg)](https://www.bestpractices.dev/projects/8033)  
[![Made with](https://img.shields.io/badge/made%20with-girl%20power-f070D0.svg?longCache=true&style=for-the-badge)](https://lara.monster)
