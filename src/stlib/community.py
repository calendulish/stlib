#!/usr/bin/env python
#
# Lara Maia <dev@lara.monster> 2015 ~ 2024
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

"""
`community` interface is used to access entry points available at steamcommunity.com
"""
import asyncio
import json
import logging
from typing import List, Tuple, Any, Dict, NamedTuple

from bs4 import BeautifulSoup
from stlib import universe, login, utils

log = logging.getLogger(__name__)


class Item(NamedTuple):
    name: str
    """Item name"""
    type: str
    """Item type"""
    amount: int
    """Item amount"""
    marketable: int
    """True if marketable"""
    tradable: int
    """True if tradable"""
    commodity: int
    """True if commodity"""
    appid: int
    """App ID"""
    classid: int
    """Class ID"""
    instanceid: int
    """Instance ID"""
    assetid: int
    """Asset ID"""
    icon_url: str
    """Icon url"""
    icon_url_large: str
    """Large icon url"""
    expiration: str
    """Expiration"""
    actions: List[Dict[str, str]]
    """List with custom actions for `Item`"""


class Order(NamedTuple):
    name: str
    """Item Name"""
    appid: int
    """App ID"""
    hash_name: str
    """Hash name"""
    type: str
    """Item type"""
    price: universe.SteamPrice
    """Item price"""
    currency: int
    """Wallet currency"""
    amount: int
    """Item amount"""
    assetid: int | None
    """Asset ID"""
    orderid: int | None
    """Order ID"""
    contextid: int | None
    """Context ID"""
    actions: List[Dict[str, str]]
    """List of available actions"""
    icon_url: str
    """Small icon url"""
    icon_url_large: str
    """Large icon url"""


class PriceInfo(NamedTuple):
    price: universe.SteamPrice
    """Price"""
    quantity: int
    """Quantity"""


class Histogram(NamedTuple):
    sell_order_count: int
    """Sell Order Count"""
    sell_order_price: universe.SteamPrice
    """Sell Order Price"""
    sell_order_table: List[PriceInfo]
    """Sell Order Table"""
    buy_order_count: int
    """Buy Order Count"""
    buy_order_price: universe.SteamPrice
    "Buy Order Price"
    buy_order_table: List[PriceInfo]
    """Buy Order Table"""
    highest_buy_order: int
    """Highest buy order price as integer"""
    lowest_sell_order: int
    """Lowest sell order price as integer"""
    buy_order_graph: List[List[float | int | str]]
    """Buy Order Graph"""
    sell_order_graph: List[List[float | int | str]]
    """Sell Order Graph"""
    price_prefix: str
    """Price Prefix"""
    price_suffix: str
    """Price Suffix"""


class Confirmation(NamedTuple):
    mode_accept: str
    """Confirmation mode for accept action"""
    mode_cancel: str
    """Confirmation mode for cancel action"""
    id: int
    """Confirmation ID"""
    creatorid: int
    """Creator ID"""
    nonce: int
    """Nonce key"""
    time: int
    """Creation time"""
    icon: str
    """Icon"""
    type: int
    """Confirmation type"""
    summary: List[str]
    """Trade summary"""
    to: str
    """Trade partner"""
    give: List[str]
    """List of items to give"""
    receive: List[str]
    """List of items to receive"""


class Badge(NamedTuple):
    name: str
    """Name"""
    appid: int
    """App ID"""
    cards: int
    """Cards remaining to drop"""


class BadgeError(AttributeError):
    """Raised when can`t find stats for the badge"""
    pass


class MarketError(ValueError):
    """Raised when can't find market orders"""
    pass


class InventoryEmptyError(ValueError):
    """Raised when inventory is empty"""

    def __init__(self, steamid: universe.SteamId, appid: int, contextid: int, message: str) -> None:
        super().__init__(message)

        self.steamid = steamid
        self.appid = appid
        self.contextid = contextid


class Community(utils.Base):
    def __init__(
            self,
            *,
            community_url: str = 'https://steamcommunity.com',
            economy_url: str = 'https://steamcommunity.com/economy',
            mobileconf_url: str = 'https://steamcommunity.com/mobileconf',
            api_url: str = 'https://api.steampowered.com',
            **kwargs: Any,
    ) -> None:
        """
        Main class to access community api methods

        Example:

            ```
            community = await Community.new_session(0)
            item_name = await community.get_item_name(appid, classid)
            ```
        """
        super().__init__(**kwargs)
        self.community_url = community_url
        self.economy_url = economy_url
        self.mobileconf_url = mobileconf_url
        self.api_url = api_url

    async def _new_mobileconf_query(
            self,
            deviceid: str,
            steamid: universe.SteamId,
            identity_secret: str,
            tag: str,
    ) -> Dict[str, Any]:
        json_data = await self.request_json(f'{self.api_url}/ISteamWebAPIUtil/GetServerInfo/v1')
        server_time = json_data['servertime']

        return {
            'p': deviceid,
            'a': steamid.id64,
            'k': universe.generate_time_hash(server_time, tag, identity_secret),
            't': server_time,
            'm': 'android',
            'tag': tag,
        }

    async def get_steam_session_id(self) -> str:
        """Get steam session id"""
        response = await self.request(self.community_url)

        if 'sessionid' in response.cookies:
            return str(response.cookies['sessionid'].value)

        html = response.content
        for line in html.splitlines():
            if 'g_sessionID' in line:
                assert isinstance(line, str), "line was wrong type (bytes?)"
                _, raw_value = line.split('= "')
                return raw_value[:-2]

        raise KeyError

    async def get_inventory(
            self,
            steamid: universe.SteamId,
            appid: int,
            contextid: int,
            count: int = 5000,
    ) -> List[Item]:
        """
        Get inventory
        :param steamid: `SteamId`
        :param appid: App ID to filter
        :param contextid:  Context ID to filter
        :param count: Max item count per page
        :return: List of `Item`
        """
        params = {'l': 'english', 'count': count}
        json_data: Dict[str, Any] = {}

        while True:
            json_data |= await self.request_json(
                f"{self.community_url}/inventory/{steamid.id64}/{appid}/{contextid}",
                params=params,
                auto_recovery=False,
            )

            if not json_data['success']:
                raise AttributeError("Unable to get inventory details")

            if json_data['total_inventory_count'] == 0:
                raise InventoryEmptyError(steamid, appid, contextid, "Inventory is empty")

            if 'last_assetid' not in json_data:
                break

            params['start_assetid'] = json_data['last_assetid']
            await asyncio.sleep(10)
        items = []
        for item in json_data['descriptions']:
            if 'market_name' in item:
                name = item['market_name']

                if item['type']:
                    name += f" - {item['type']}"
            else:
                name = item['name']

            for asset in json_data['assets']:
                if asset['classid'] == item['classid']:
                    amount = asset['amount']
                    assetid = asset['assetid']
                    break

            # noinspection PyUnboundLocalVariable
            kwargs = {
                'name': name,
                'type': item['type'],
                'amount': amount,
                'marketable': item['marketable'],
                'tradable': item['tradable'],
                'commodity': item['commodity'],
                'appid': item['appid'],
                'classid': item['classid'],
                'instanceid': item['instanceid'],
                'assetid': assetid,
                'icon_url': item['icon_url'],
                'icon_url_large': item['icon_url_large'],
                'expiration': item['item_expiration'],
                'actions': item['actions'],
            }

            items.append(Item(**kwargs))

        return items

    async def get_badges(self, steamid: universe.SteamId, show_no_drops: bool = False) -> List[Badge]:
        """
        Get badges
        :param steamid: `SteamId`
        :param show_no_drops: If true, get badges with no drops as well
        :return: List of `Badge`
        """
        badges = []
        params: Dict[str, str | int] = {'l': 'english'}
        html = await self.request_html(f"{steamid.profile_url}/badges/", params=params)
        badges_raw = html.find_all('div', class_='badge_title_row')

        try:
            pages = int(html.find_all('a', class_='pagelink')[-1].text)
        except IndexError:
            pages = 1

        for page in range(1, pages):
            params['p'] = page + 1
            html = await self.request_html(f"{steamid.profile_url}/badges/", params=params)
            badges_raw += html.find_all('div', class_='badge_title_row')

        for badge_raw in badges_raw:
            title = badge_raw.find('div', class_='badge_title')
            name = title.text.split('\t\t\t\t\t\t\t\t\t', 2)[1]

            try:
                appref = badge_raw.find('a')['href']
            except TypeError:
                # FIXME: It's a foil badge. The game id is above the badge_title_row
                appid = 000000
            else:
                try:
                    appid = int(appref.split('/', 3)[3])
                except IndexError:
                    # Possibly a game without cards
                    appid = int(appref.split('_', 6)[4])

            progress = badge_raw.find('span', class_='progress_info_bold')

            if not progress or "No" in progress.text:
                cards = 0
            else:
                cards = int(progress.text.split(' ', 3)[0])

            if cards != 0 or show_no_drops:
                badges.append(Badge(name, appid, cards))

        return badges

    async def get_item_name(
            self,
            appid: str,
            classid: str,
    ) -> str:
        """Get item name from app ID"""
        params = {'content_only': 1}

        json_data = await self.request_json_from_js_func(
            f"{self.economy_url}/itemclasshover/{appid}/{classid}",
            target="BuildHover",
            params=params,
        )

        if json_data:
            if 'market_name' in json_data and json_data['market_name']:
                item_name = f"{json_data['market_name']}"
                log.debug("Using `market_name' for %s:%s (%s)", appid, classid, item_name)
            else:
                item_name = json_data['name']
                log.debug("Using `name' for %s:%s (%s)", appid, classid, item_name)

            if 'type' in json_data and json_data['type']:
                item_name += f" ({json_data['type']})"
        else:
            log.debug("Unable to find human readable name for %s:%s", appid, classid)
            item_name = ''

        return item_name

    async def get_confirmations(
            self,
            identity_secret: str,
            steamid: universe.SteamId,
            deviceid: str,
    ) -> List[Confirmation]:
        """
        Get confirmations for logged user
        :param identity_secret: User identity secret
        :param steamid: `SteamId`
        :param deviceid: Device ID
        :return: List of `Confirmation`
        """
        params = await self._new_mobileconf_query(deviceid, steamid, identity_secret, 'conf')
        json_data = await self.request_json(f'{self.mobileconf_url}/getlist', params=params)

        if not json_data['success']:
            raise login.LoginError('User is not logged in')

        confirmations = []
        for confirmation in json_data['conf']:
            details_params = await self._new_mobileconf_query(
                deviceid,
                steamid,
                identity_secret,
                f"details{confirmation['id']}",
            )

            log.debug(
                "Getting human readable information from %s as type %s (%s)",
                confirmation['id'],
                confirmation['type'],
                "Market" if confirmation['type'] == 3 else 'Trade Item',
            )

            json_data = await self.request_json(
                f"{self.mobileconf_url}/details/{confirmation['id']}",
                params=details_params,
            )

            if not json_data['success']:
                raise AttributeError(f"Unable to get details for confirmation {confirmation['id']}")

            html = BeautifulSoup(json_data["html"], 'html.parser')

            if confirmation['type'] in (1, 2):
                try:
                    offer_friend = html.find('div', class_="mobileconf_offer_friend")
                    to = offer_friend.find_next('span').text.strip()
                except AttributeError:
                    trade_partner = html.find('span', class_="trade_partner_headline_sub")
                    to = trade_partner.get_text().strip()

                item_list = html.find_all('div', class_="tradeoffer_item_list")

                give = []
                for item in item_list[0].find_all('div', class_='trade_item'):
                    appid, classid = item['data-economy-item'].split('/')[1:3]
                    name = await self.get_item_name(appid, classid)
                    give.append(name)

                receive = []
                for item in item_list[1].find_all('div', class_='trade_item'):
                    appid, classid = item['data-economy-item'].split('/')[1:3]
                    name = await self.get_item_name(appid, classid)
                    receive.append(name)
            elif confirmation['type'] == 3:
                to = "Market"

                listing_prices = html.find('div', class_="mobileconf_listing_prices")
                final_price = listing_prices.find(text=lambda element: 'You receive' in element.text).next.next.strip()
                sell_price = listing_prices.find(text=lambda element: 'Buyer pays' in element.text).next.next.strip()
                receive = [f"{final_price} ({sell_price})"]

                javascript = html.find_all("script")[2]
                json_data = self.get_json_from_js_func(javascript, target="BuildHover")

                if 'market_name' in json_data and json_data['market_name']:
                    give = [json_data['market_name']]

                    if json_data['type']:
                        give[0] += f" - {json_data['type']}"
                else:
                    give = [json_data['type']]

                if quantity := listing_prices.find(
                        text=lambda element: 'Quantity' in element.text
                ):
                    give[0] = f'{quantity.next.next.strip()} {give[0]}'
            elif confirmation['type'] == 5:
                to = "Steam"
                give = ["Change phone number"]
                receive = ["Phone number has not been entered yet"]
            elif confirmation['type'] == 6:
                to = "Steam"
                give = ["Make changes to your account"]
                receive = [f"Number to match: {html.find_all('div')[3].text.strip()}"]
            else:
                to = "NotImplemented"
                give = [f"{confirmation['id']}"]
                receive = [f"{confirmation['nonce']}"]

            confirmations.append(
                Confirmation(
                    confirmation['accept'],
                    confirmation['cancel'],
                    confirmation['id'],
                    confirmation['creator_id'],
                    confirmation['nonce'],
                    confirmation['creation_time'],
                    confirmation['icon'],
                    confirmation['type'],
                    confirmation['summary'],
                    to, give, receive,
                )
            )

        return confirmations

    async def get_card_drops_remaining(self, steamid: universe.SteamId, appid: int) -> int:
        """
        Get card drops remaining for `appid`
        :param steamid: `SteamId`
        :param appid: App ID
        :return: Card drop count
        """
        params = {'l': 'english'}

        html = await self.request_html(f"{steamid.profile_url}/gamecards/{appid}", params=params)
        stats = html.find('div', class_='badge_title_stats_drops')

        if stats is None:
            raise BadgeError(f"Unable to get card count for {appid}")

        progress = stats.find('span', class_='progress_info_bold')

        return (
            0
            if not progress or "No" in progress.text
            else int(progress.text.split(' ', 3)[0])
        )

    async def get_last_played_game(self, steamid: universe.SteamId) -> int | None:
        """
        Get last played game
        :param steamid: `SteamId`
        :return: gameid or None
        """
        html = await self.request_html(f"{steamid.profile_url}")
        game_list = html.find('div', class_="recent_games")

        if not game_list:
            return None

        gameid = game_list.find('a')['href'].split('/')[-1]

        return int(gameid)

    async def get_my_orders(self) -> Tuple[List[Order], List[Order]]:
        """
        Get list of orders for current logged user
        :return: sell orders (`Order`) and buy orders (`Order`)
        """
        params = {"start": 0, "count": 100, "norender": 1, "l": "english"}
        json_data: Dict[str, Any] = {}

        while True:
            json_data |= await self.request_json(
                f"{self.community_url}/market/mylistings", params=params
            )

            if not json_data['success']:
                raise AttributeError("Unable to get order details")

            if json_data['total_count'] <= 100:
                break

            params['start'] += 100
            await asyncio.sleep(5)
        my_sell_orders = []

        for order in json_data['listings']:
            asset = order['asset']
            price = universe.SteamPrice.new_from_integer(int(order['price']))

            my_sell_orders.append(
                Order(
                    asset['name'],
                    int(asset['appid']),
                    asset['market_hash_name'],
                    asset['type'],
                    price,
                    0,
                    int(asset['amount']),
                    int(asset['unowned_id']),
                    int(order['listingid']),
                    int(asset['unowned_contextid']),
                    asset['owner_actions'] if 'owner_actions' in asset else [],
                    asset['icon_url'],
                    asset['icon_url_large'],
                )
            )

        my_buy_orders = []
        for order in json_data['buy_orders']:
            description = order['description']
            price = universe.SteamPrice.new_from_integer(int(order['price']))

            my_buy_orders.append(
                Order(
                    description['name'],
                    int(order['appid']),
                    order['hash_name'],
                    description['type'],
                    price,
                    int(order['wallet_currency']),
                    int(order['quantity']),
                    None,
                    int(order['buy_orderid']),
                    None,
                    order['owner_actions'] if 'owner_actions' in order else [],
                    description['icon_url'],
                    description['icon_url_large'],
                )
            )

        return my_sell_orders, my_buy_orders

    async def get_item_histogram(self, appid: int, hash_name: str) -> Histogram:
        """
        get item histogram
        :param appid: appid
        :param hash_name: item hash name
        :return: histogram data
        """

        html = await self.request_html(f"{self.community_url}/market/listings/{appid}/{hash_name}")
        scripts = html.find_all("script")

        try:
            item_activity_func = str(scripts[-1])
            start = item_activity_func.index("LoadOrderSpread") + 17
            end = item_activity_func[start:].index(" );") + start
            item_nameid = item_activity_func[start:end]
        except ValueError as exception:
            raise MarketError("Unable to load market orders") from exception

        wallet_vars = self.get_vars_from_js(scripts[-2])

        if 'g_rgWalletInfo' in wallet_vars:
            currency = wallet_vars['g_rgWalletInfo']['wallet_currency']
            country = wallet_vars['g_rgWalletInfo']['wallet_country']
        else:
            currency = 0
            country = wallet_vars['g_strCountryCode']

        params = {
            'language': 'english',
            'currency': currency,
            'country': country,
            'item_nameid': item_nameid,
            'norender': 1,
        }

        json_data = await self.request_json(
            f"{self.community_url}/market/itemordershistogram", params=params
        )

        sell_order_table: List[PriceInfo] = []
        buy_order_table: List[PriceInfo] = []

        if 'sell_order_table' in json_data and json_data['sell_order_table']:
            sell_order_table.extend(
                PriceInfo(
                    universe.SteamPrice.new_from_monetary_price(order['price']),
                    int(order['quantity'].replace(',', '')),
                )
                for order in json_data['sell_order_table']
            )
        else:
            json_data['sell_order_count'] = "0"
            json_data['sell_order_price'] = "0"
            json_data['lowest_sell_order'] = "0"

        if 'buy_order_table' in json_data and json_data['buy_order_table']:
            buy_order_table.extend(
                PriceInfo(
                    universe.SteamPrice.new_from_monetary_price(order['price']),
                    int(order['quantity'].replace(',', '')),
                )
                for order in json_data['buy_order_table']
            )
        else:
            json_data['buy_order_count'] = "0"
            json_data['buy_order_price'] = "0"
            json_data['highest_buy_order'] = "0"

        return Histogram(
            int(json_data['sell_order_count'].replace(',', '')),
            universe.SteamPrice.new_from_monetary_price(json_data['sell_order_price']),
            sell_order_table,
            int(json_data['buy_order_count'].replace(',', '')),
            universe.SteamPrice.new_from_monetary_price(json_data['buy_order_price']),
            buy_order_table,
            int(json_data['highest_buy_order']),
            int(json_data['lowest_sell_order']),
            json_data['buy_order_graph'],
            json_data['sell_order_graph'],
            json_data['price_prefix'],
            json_data['price_suffix'],
        )

    async def get_goo_value(self, steamid: universe.SteamId, appid: int, item_type: int, border_color: int = 0) -> int:
        """
        Get goo value
        :param steamid: universe.SteamId,
        :param appid: AppID
        :param item_type: Item type
        :param border_color: card border color
        :return: Goo value
        """

        params = {
            "appid": appid,
            "item_type": item_type,
            "border_color": border_color,
        }

        headers = {
            "Referer": f"{self.community_url}/profiles/{steamid.id64}/inventory",
        }

        response = await self.request_json(
            f"{self.community_url}/auction/ajaxgetgoovalueforitemtype", headers=headers, params=params,
        )

        if 'success' not in response or response['success'] != 1:
            raise MarketError("Unable to get goo value")

        return int(response['goo_value'])

    async def cancel_sell_order(self, order_id: int) -> None:
        """
        Remove market sell order
        :param order_id: order id
        :return: None
        """

        data = {
            "sessionid": await self.get_steam_session_id(),
        }

        headers = {
            "Referer": f"{self.community_url}/market",
        }

        await self.request(
            f"{self.community_url}/market/removelisting/{order_id}", headers=headers, data=data,
        )

        return None

    async def cancel_buy_order(self, order_id: int) -> None:
        """
        Remove market buy order
        :param order_id: order id
        :return: None
        """

        data = {
            "sessionid": await self.get_steam_session_id(),
            "buy_orderid": order_id,
        }

        headers = {
            "Referer": f"{self.community_url}/market",
            "X-Requested-With": "XMLHttpRequest",
        }

        response = await self.request_json(
            f"{self.community_url}/market/cancelbuyorder", headers=headers, data=data,
        )

        if 'success' not in response or response['success'] != 1:
            raise MarketError("Unable to cancel buy order")

        return None

    async def sell_item(
            self,
            steamid: universe.SteamId,
            appid: int,
            contextid: int,
            assetid: int,
            price: universe.SteamPrice,
            amount: int = 1,
    ) -> Dict[str, Any]:
        """
        Sell an item on market
        :param steamid: `universe.SteamId`,
        :param appid: AppID
        :param contextid: ContextID
        :param assetid: AssetID
        :param price: Sell price
        :param amount: Amount to sell
        :return: Json data
        """

        data = {
            "appid": str(appid),
            "contextid": str(contextid),
            "assetid": str(assetid),
            "amount": str(amount),
            "price": price.as_integer(subtract_fees=True) * amount,
            "sessionid": await self.get_steam_session_id(),
        }

        headers = {
            "Referer": f"{self.community_url}/profiles/{steamid.id64}/inventory",
        }

        response = await self.request_json(
            f"{self.community_url}/market/sellitem", headers=headers, data=data,
        )

        if 'success' in response and not response['success']:
            raise MarketError(response['message'])

        return response

    async def buy_item(
            self,
            appid: int,
            hash_name: str,
            price: universe.SteamPrice,
            currency: int,
            amount: int = 1,
    ) -> Dict[str, Any]:
        """
        Buy item on market
        :param appid: AppID
        :param hash_name: Market hash name
        :param price: Buy price
        :param currency: Wallet currency
        :param amount: Quantity to buy
        :return: Json data
        """
        data = {
            'currency': str(currency),
            "appid": str(appid),
            "market_hash_name": hash_name,
            "price_total": price.as_integer() * amount,
            "quantity": str(amount),
            "billing_state": "",
            "save_my_address": "0",
            "sessionid": await self.get_steam_session_id(),
        }

        headers = {
            "Referer": f"{self.community_url}/market/listings/{appid}/{hash_name}",
        }

        response = await self.request_json(
            f"{self.community_url}/market/createbuyorder", headers=headers, data=data,
        )

        if 'success' in response and response['success'] != 1:
            raise MarketError(response['message'])

        return response

    async def send_trade_offer(
            self,
            steamid: universe.SteamId,
            token: str,
            contextid: int,
            me: List[Tuple[int, int, int]],
            them: List[Tuple[int, int, int]],
    ) -> Dict[str, Any]:
        """
        Send a trade offer
        :param steamid: `SteamId`
        :param token: Partner token
        :param contextid: Context ID
        :param me: List of my items to trade
        :param them: List of them items to trade
        :return: Json data
        """
        me_assets = [
            {
                'appid': item[0],
                'contextid': str(contextid),
                'amount': item[2],
                'assetid': str(item[1]),
            }
            for item in me
        ]
        them_assets = [
            {
                'appid': item[0],
                'contextid': str(contextid),
                'amount': item[2],
                'assetid': str(item[1]),
            }
            for item in them
        ]
        offer = {
            'newversion': True,
            'version': len(me_assets) + len(them_assets) + 1,
            'me': {
                'assets': me_assets,
                'currency': [],
                'ready': False,
            },
            'them': {
                'assets': them_assets,
                'currency': [],
                'ready': False,
            }
        }

        data = {
            'sessionid': await self.get_steam_session_id(),
            'serverid': 1,
            'partner': steamid.id64,
            'tradeoffermessage': '',
            'json_tradeoffer': json.dumps(offer),
            'captcha': None,  # TODO
            'trade_offer_create_params': json.dumps({'trade_offer_access_token': token}),
        }

        headers = {'referer': f'{self.community_url}/tradeoffer/new/?partner={steamid.id3}&token={token}'}
        return await self.request_json(
            f"{self.community_url}/tradeoffer/new/send", data=data, headers=headers
        )

    async def send_confirmation(
            self,
            identity_secret: str,
            steamid: universe.SteamId,
            deviceid: str,
            trade_id: int,
            trade_key: int,
            action: str,
    ) -> Dict[str, Any]:
        """
        Send confirmation aprovals/refuses
        :param identity_secret: Steam user identity secret
        :param steamid: `SteamId`
        :param deviceid: device ID
        :param trade_id: trade ID
        :param trade_key: trade key
        :param action: Action to taken from [allow, cancel]
        :return: Json data
        """
        extra_params = {'cid': trade_id, 'ck': trade_key, 'op': action}
        params = await self._new_mobileconf_query(deviceid, steamid, identity_secret, 'conf')
        return await self.request_json(
            f'{self.mobileconf_url}/ajaxop', params={**params, **extra_params}
        )

    async def revoke_api_key(self) -> None:
        """
        Revoke the developer API Key associated with the current logged account
        :return: None
        """
        data = {'sessionid': await self.get_steam_session_id()}
        await self.request(f'{self.community_url}/dev/revokekey', data=data)

    async def register_api_key(self, domain: str = 'stlib') -> None:
        """
        (DEPRECATED! Use `request_api_key` instead)
        Register a new developer API Key for the current logged account
        :param domain: app name
        :return: None
        """
        log.warning("Using deprecated method to get api key.")

        data = {
            'domain': domain,
            'agreeToTerms': 'agreed',
            'sessionid': await self.get_steam_session_id(),
            'Submit': 'Register',
        }

        await self.request(f'{self.community_url}/dev/registerkey', data=data)

    async def request_api_key(self, domain: str = 'stlib', request_id: int = 0) -> Tuple[int, str]:
        """
        Request a new developer API Key for the current logged account
        :param domain: app name
        :param request_id: request id
        :return: request id, api key
        """
        data = {
            'domain': domain,
            'agreeToTerms': 'true',
            'sessionid': await self.get_steam_session_id(),
            'request_id': str(request_id),
        }

        json_data = await self.request_json(f'{self.community_url}/dev/requestkey', data=data)

        return int(json_data['request_id'] or 0), str(json_data['api_key'] or "")

    async def get_api_key(self) -> Tuple[str, str]:
        """
        Get developer API Key for the current logged account
        :return: key, domain
        """
        html = await self.request_html(f'{self.community_url}/dev/apikey')
        main = html.find('div', id='mainContents')

        if 'Access Denied' in main.find('h2').text:
            raise PermissionError("Your Steam account is limited")

        contents = html.find('div', id="bodyContents_ex")

        if 'Register' in contents.find('h2').text:
            raise AttributeError('No api key registered')

        key = contents.find('p').text[5:]
        domain = contents.find_all('p')[1].text[13:]
        return key, domain
