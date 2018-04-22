stlib
-----

[![Linux Build Status](https://img.shields.io/travis/ShyPixie/stlib/master.svg?label=Linux%20build)](https://travis-ci.org/ShyPixie/stlib)
[![Windows Build status](https://img.shields.io/appveyor/ci/ShyPixie/stlib/master.svg?label=Windows%20build)](https://ci.appveyor.com/project/ShyPixie/stlib)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/ShyPixie/stlib/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/ShyPixie/stlib/?branch=master)
[![Code Coverage](https://scrutinizer-ci.com/g/ShyPixie/stlib/badges/coverage.png?b=master)](https://scrutinizer-ci.com/g/ShyPixie/stlib/?branch=master)
[![GitHub license](https://img.shields.io/badge/license-GPLv3-green.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![GitHub release](https://img.shields.io/github/release/ShyPixie/stlib.svg)](https://github.com/ShyPixie/stlib/releases)
[![GitHub Test release](https://img.shields.io/badge/testing-0.0.0_DEV-orange.svg)](https://github.com/ShyPixie/stlib/releases)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=WVQ5XM935XNLN&item_name=stlib)

Async library that provides features related to Steam client and compatible stuffs

WORK IN PROGRESS


Dependencies to build
----------------------

- Steamworks SDK >= v1.42 (put contents on src/steam_api/steamworks_sdk folder)
- Python and headers >= 3.6
- Microsoft Visual C++ compiler (MSVC) or GNU Compiler (GCC)

Dependencies to run
-------------------

- aiodns
- ujson
- asyncio
- beautifulsoup4

Examples
--------

- **steam_api (low-level)**

```
from stlib import steam_api

steam_api.init()            # SteamAPI_Init
steam_api.shutdown()        # SteamAPI_Shutdown

steam_api.server_init()     # SteamGameServer_Init
steam_api.server_shutdown() # SteamGameServer_Shutdown
```

- **Client**

```
from stlib import client

# SteamGameServer can accept parameters (read the sources)
with client.SteamGameServer() as server:
    server_time = server.get_server_time()
```

```
from stlib import client, steam_api

# SteamApiExecutor will run commands in a protected
# environment using multiprocessing module
with client.SteamApiExecutor() as executor:
    # use `call' method to call functions inside
    # the protected environment and return the result.
    # Exceptions will be reraised
    result = executor.call(steam_api.init)

    # also will work for classes
    steam_utils = executor.call(steam_api.SteamUtils)
```

```
# It'll work without context manager as well
executor = client.SteamApiExecutor()
# start protected environment
executor.init()
<your code here>
# stop protected environment
executor.shutdown()
```

- **Authenticator**

```
from stlib import authenticator

# It'll return an tuple:
# First argument is the steam guard code (E.g.: ['A', 'B', 'C', 'D', 'E'])
# Second argument is the timestamp received from server in unix format (E.g.: 0123456789)
steam_guard_code = authenticator.get_code(<your secret here>)

# If you don't have the secret already, you can use the
# AndroidDebugBridge method. See bellow
```

```
from stlib import authenticator

# You can use AndroidDebugBridge method for get user info from
# a phone with Steam Guard enabled.
# Requirements:
# - adb tool from google
# - a "rooted" Android phone with adb debugging enabled
adb = authenticator.AndroidDebugBridge(<path where adb tool is located>, <path to Steam Mobile App>)

secret = adb.get_secret(<secret type>)
```
___________________________________________________________________________________________

This is an work in progress. You can request new features.

The stlib is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

The stlib is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

Lara Maia <dev@lara.click>

[![Made with](https://img.shields.io/badge/made%20with-girl%20power-f070D0.svg?longCache=true&style=for-the-badge)](http://lara.click)
