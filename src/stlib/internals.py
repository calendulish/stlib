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

import logging
from typing import List, NamedTuple, Dict, Tuple

from . import utils

log = logging.getLogger(__name__)


class Package(NamedTuple):
    name: str
    """Package name"""
    packageid: int
    """Package ID"""
    page_image: str
    """Page image"""
    small_logo: str
    """Small logo"""
    apps: List[int]
    """List of appids associated with current Package"""
    platforms: Dict[str, bool]
    """List of platforms supported from [windows, mac, linux]"""
    release_date: str
    """Release date"""
    coming_soon: bool
    """True if isn't released yet"""
    discount_percent: int
    """Discount percent if on sale"""
    price: float
    """Current price"""


class Game(NamedTuple):
    name: str
    """App name"""
    appid: int
    """App ID"""
    type: str
    """App type from [game, dlc, demo, advertising, mod, video]"""
    dlcs: List[int]
    """List of available dlcs for current game"""
    packages: List[int]
    """List of available packages for current game"""
    is_free: int
    """True if it's a free game"""
    developers: List[str]
    """List of developers"""
    publishers: List[str]
    """List of publishers"""
    platforms: Dict[str, bool]
    """List of platforms supported from [windows, mac, linux]"""
    header_image: str
    """Header image"""
    background: str
    """Background image"""
    release_date: str
    """Release date"""
    coming_soon: bool
    """True if isn't released yet"""
    score: int
    """metacritic score"""
    discount_percent: int
    """Discount percent if on sale"""
    price: float
    """Current price"""


class Internals(utils.Base):
    def __init__(
            self,
            *,
            store_url: str = 'https://store.steampowered.com',
            **kwargs,
    ) -> None:
        """
        Main class to access steam web api internals

        Example:

            ```
            internals = Internals.get_session(0)
            game = await internals.get_game(480)
            ```
        """
        super().__init__(**kwargs)
        self.store_url = store_url

    # Despite this apparently accepts comma-separated parameters
    # actualy isn't working without price_overview filter
    async def get_game(self, appid: int) -> Game:
        """Get game details. See `Game`"""
        appid = str(appid)
        params = {'appids': appid}
        json_data = await self.request_json(f'{self.store_url}/api/appdetails', params=params)

        if not json_data[appid]['success']:
            raise ValueError("Failed to get details for app %s", appid)

        game_params = {
            'name': json_data[appid]['data']['name'],
            'type': json_data[appid]['data']['type'],
            'appid': json_data[appid]['data']['steam_appid'],
            'is_free': json_data[appid]['data']['is_free'],
            'dlc': json_data[appid]['data']['dlc'],
            'header_image': json_data[appid]['data']['header_image'],
            'developers': json_data[appid]['data']['developers'],
            'publishers': json_data[appid]['data']['publishers'],
            'packages': json_data[appid]['data']['packages'],
            'platforms': json_data[appid]['data']['platforms'],
            'score': json_data[appid]['data']['metacritic']['score'],
            'release_date': json_data[appid]['data']['release_date']['date'],
            'coming_soon': json_data[appid]['data']['release_date']['coming_soon'],
            'background': json_data[appid]['data']['background'],
        }

        if 'price_overview' in json_data[appid]['data']:
            game_params['discount_percent'] = json_data[appid]['data']['price_overview']['discount_percent']
            price_raw = json_data[appid]['data']['price_overview']['initial']
            game_params['price'] = float(f"{str(price_raw)[:-2]}.{str(price_raw)[-2:]}")

        return Game(**game_params)

    # Despite this apparently accepts comma-separated parameters, actually isn't working
    async def get_package(self, packageid: int) -> Package:
        """Get package details. See `Package`"""
        packageid = str(packageid)
        params = {'packageids': packageid}
        json_data = await self.request_json(f'{self.store_url}/api/packagedetails', params=params)

        if not json_data[packageid]['success']:
            raise ValueError("Failed to get details for package %s", packageid)

        package_params = {
            'name': json_data[packageid]['data']['name'],
            'page_image': json_data[packageid]['data']['page_image'],
            'small_logo': json_data[packageid]['data']['small_logo'],
            'apps': [app['id'] for app in json_data[packageid]['data']['apps']],
            'platforms': json_data[packageid]['data']['platforms'],
            'release_date': json_data[packageid]['data']['release_date']['date'],
            'coming_soon': json_data[packageid]['data']['release_date']['coming_soon'],
        }

        if 'price' in json_data[packageid]['data']:
            package_params['discount_percent'] = json_data[packageid]['data']['price']['discount_percent']
            price_raw = json_data[packageid]['data']['price']['initial']
            package_params['price'] = float(f"{str(price_raw)[:-2]}.{str(price_raw)[-2:]}")

        return Package(**package_params)

    async def get_prices(self, appids: List[int]) -> Dict[int, Tuple[float, int]]:
        """
        Get current prices for appids
        :param appids: list of appids
        :return: {appid: (price, discount)}
        """
        assert isinstance(appids, List), "appids must be a list"
        assert all([isinstance(id_, int) for id_ in appids]), "each appid must be a number"

        appids = map(str, appids)
        params = {'appids': ','.join(appids), 'filters': 'price_overview'}
        json_data = await self.request_json(f'{self.store_url}/api/appdetails', params=params)

        prices = {}
        for appid in appids:
            if not json_data[appid]['success']:
                log.error("Failed to get details for app %s", appid)
                continue

            discount_percent = json_data[appid]['data']['price_overview']['discount_percent']
            price_raw = json_data[appid]['data']['price_overview']['initial']
            price = float(f"{str(price_raw)[:-2]}.{str(price_raw)[-2:]}")
            prices[int(appid)] = (price, discount_percent)

        return prices
