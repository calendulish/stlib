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
from typing import List, NamedTuple, Dict

from . import utils

log = logging.getLogger(__name__)


class Package(NamedTuple):
    name: str
    packageid: int
    page_image: str
    small_logo: str
    apps: List[int]
    platforms: Dict[str, bool]
    release_date: str
    coming_soon: bool
    discount_percent: int
    price: float


class Game(NamedTuple):
    name: str
    appid: int
    type: str
    dlcs: List[int]
    packages: List[int]
    is_free: int
    developers: List[str]
    publishers: List[str]
    platforms: Dict[str, bool]
    header_image: str
    background: str
    release_date: str
    coming_soon: bool
    score: int
    discount_percent: int
    price: float


class Internals(utils.Base):
    def __init__(
            self,
            *,
            store_url: str = 'https://store.steampowered.com',
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.store_url = store_url

    # Despite this apparently accepts comma-separated parameters
    # actualy isn't working without price_overview filter
    async def get_game(self, appid: int) -> Game:
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
            'release_date': json_data[appid]['data']['release_data']['date'],
            'coming_soon': json_data[appid]['data']['release_data']['coming_soon'],
            'background': json_data[appid]['data']['background'],
        }

        if 'price_overview' in json_data[appid]['data']:
            game_params['discount_percent'] = json_data[appid]['data']['price_overview']['discount_percent']
            price_raw = json_data[appid]['data']['price_overview']['initial']
            game_params['price'] = float(f"{str(price_raw)[:-2]}.{str(price_raw)[-2:]}")

        return Game(**game_params)

    # Despite this apparently accepts comma-separated parameters, actually isn't working
    async def get_package(self, packageid: int) -> Package:
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
            'release_date': json_data[packageid]['data']['release_data']['date'],
            'coming_soon': json_data[packageid]['data']['release_data']['coming_soon'],
        }

        if 'price' in json_data[packageid]['data']:
            package_params['discount_percent'] = json_data[packageid]['data']['price']['discount_percent']
            price_raw = json_data[packageid]['data']['price']['initial']
            package_params['price'] = float(f"{str(price_raw)[:-2]}.{str(price_raw)[-2:]}")

        return Package(**package_params)

    async def get_prices(self, appids: List[int]) -> Dict[int, List[float, int]]:
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
            prices[int(appid)] = [price, discount_percent]

        return prices
