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
import asyncio
import contextlib
import logging
from typing import Dict, Any, Optional

import aiohttp
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)
_session_cache = {}


class Base:
    """
    You should not instantiate this class directly!
    See `get_session`
    """
    def __new__(cls) -> None:
        raise SyntaxError(
            "Don't instantiate this class directly! "
            "Use get_session(<index>) to support multiple sessions."
        )

    def __init__(
            self,
            headers: Optional[Dict[str, str]] = None,
            http_session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        self._headers = headers
        self._http_session = http_session

    @property
    def headers(self) -> Dict[str, str]:
        """returns the default headers to send with all http requests"""
        if not self._headers:
            self._headers = {'User-Agent': 'Unknown/0.0.0'}

        return self._headers

    @property
    def http(self) -> aiohttp.ClientSession:
        """returns the default http session"""
        if not self._http_session:
            log.debug("Creating a new un-cached http session")
            self._http_session = aiohttp.ClientSession(raise_for_status=True)

        return self._http_session

    @classmethod
    def get_session(cls, session_index: int, **kwargs) -> 'Base':
        """
        Get an instance of module with `http_session` from cache at `session_index`.

        If session doesn't exist in cache, it will create a new session.
        If session exist in cache, it will reuse session from cache.

        :param session_index: session number
        :return: instance of module
        """
        if 'http_session' not in _session_cache:
            _session_cache['http_session'] = []

        session_count = len(_session_cache['http_session'])

        if 'http_session' not in kwargs:
            if session_count > session_index:
                log.info("Using existent http session at index %s for %s", session_index, cls.__name__)
                kwargs['http_session'] = _session_cache['http_session'][session_index]
            else:
                log.debug("Creating a new http session at index %s for %s", session_index, cls.__name__)
                kwargs['http_session'] = aiohttp.ClientSession(raise_for_status=True)

                if session_count < session_index:
                    log.error("Session index is invalid. Session will be created at index %s", session_count)

                _session_cache['http_session'].insert(session_index, kwargs['http_session'])

        if cls.__name__ not in _session_cache:
            log.debug("Creating a new %s session", cls.__name__)
            _session_cache[cls.__name__] = super().__new__(cls)

        log.debug("Initializing instance for %s", cls.__name__)
        _session_cache[cls.__name__].__init__(**kwargs)

        return _session_cache[cls.__name__]

    @staticmethod
    def get_json_from_js(javascript: BeautifulSoup) -> Dict[str, Any]:
        """
        converts javascript data to json data
        :param javascript: javascript parsed with data. Usually contents of a ''<script>''  tag
        :return: json data as Dict
        """
        json_data = {}
        for line in str(javascript).split('\t+'):
            if "BuildHover" in line:
                for item in line.split(','):
                    with contextlib.suppress(ValueError):
                        key_raw, value_raw = item.split(':"')
                        key = key_raw.replace('"', '')
                        value = bytes(value_raw.replace('"', ''), 'utf-8').decode('unicode_escape')
                        json_data[key] = value
            break

        return json_data

    @staticmethod
    async def get_html(response: aiohttp.ClientResponse) -> BeautifulSoup:
        """get html parsed from response"""
        return BeautifulSoup(await response.text(), 'html.parser')

    async def request_json(self, *args, **kwargs) -> Dict[str, Any]:
        """make a new http request and returns json data"""
        response = await self.request(*args, **kwargs)
        return await response.json()

    async def request_json_from_js(
            self,
            *args,
            script_index: int = 0,
            **kwargs,
    ) -> Dict[str, Any]:
        """
        make a new http request and returns json data from javascript at given index
        :param args: request args
        :param script_index: index of script at html page
        :param kwargs: request kwargs
        :return: json_data as Dict
        """
        html = await self.request_html(*args, **kwargs)
        javascript = html.find_all('script')[script_index]
        return self.get_json_from_js(javascript)

    async def request_html(self, *args, **kwargs) -> BeautifulSoup:
        """make a new http request and returns html"""
        response = await self.request(*args, **kwargs)
        return await self.get_html(response)

    async def request(
            self,
            url: str,
            params: Optional[Dict[str, str]] = None,
            data: Optional[Dict[str, str]] = None,
            headers: Optional[Dict[str, str]] = None,
            auto_recovery: bool = True,
            **kwargs,
    ) -> aiohttp.ClientResponse:
        """
        Make a new http request
        :param auto_recovery: if defined and http request fail, it will try again
        :param kwargs: extra kwargs passed directly to http request
        :return: http response
        """
        if not params:
            params = {}

        if not headers:
            headers = {}

        http_method = 'POST' if data else 'GET'

        request_params: Dict[str, Any] = {
            'method': http_method,
            'url': url,
            'params': params,
            'data': data,
            'headers': {**self.headers, **headers},
            **kwargs,
        }

        log.debug("Requesting %s via %s with %s:%s", url, http_method, params, data)

        for _ in range(3):
            try:
                async with self.http.request(**request_params) as response:
                    return response
            except aiohttp.ClientResponseError as exception:
                log.debug("Response error %s", exception.status)

                if auto_recovery:
                    log.debug("Auto recovering in 5 seconds")
                    await asyncio.sleep(5)
                    continue
                else:
                    raise exception from None
