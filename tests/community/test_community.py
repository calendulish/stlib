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

from stlib import community
from tests import debug, requires_unlimited_account


async def test_get_last_played_game(community_session, steamid) -> None:
    last_played_game = await community_session.get_last_played_game(steamid)
    assert isinstance(last_played_game, int) or last_played_game is None
    debug(str(last_played_game), wait_for=0)


async def test_get_my_buy_orders(community_session) -> None:
    my_orders = await community_session.get_my_orders()
    assert isinstance(my_orders, tuple)
    assert isinstance(my_orders[0], list)
    assert isinstance(my_orders[1], list)

    for order in my_orders[0] + my_orders[1]:
        assert isinstance(order, community.Order)

    debug(str(my_orders), wait_for=3)


@requires_unlimited_account
async def test_get_item_histogram(community_session) -> None:
    histogram = await community_session.get_item_histogram(753, "1385730-:SecretPresent:")
    assert isinstance(histogram, dict)
    debug(str(histogram), wait_for=0)
