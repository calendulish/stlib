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
import http.cookies
import json
import logging
from typing import Dict, Any, Optional, NamedTuple

import aiohttp
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)
_session_cache = {}


class Response(NamedTuple):
    status: int
    """Status code"""
    info: aiohttp.RequestInfo
    """Request Info"""
    cookies: http.cookies.SimpleCookie
    """Cookies"""
    content: str
    """Content as string"""
    content_type: str
    """Content type"""


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
    async def new_session(cls, session_index: int, **kwargs) -> 'Base':
        """
        Create an instance of module at given `session_index`.
        If a previous instance exists in cache at same index, it will returns IndexError.
        The instance will be associated with a http session at same index.
        If a http session is not present in cache, it'll create a new one.
        If there's a 'http_session' present in kwargs, it will be used instead.

        :param session_index: Session number
        :param kwargs: Instance parameters
        :return: Instance of module
        """
        if cls.__name__ not in _session_cache:
            log.debug("Creating a new cache object at %s for %s", session_index, cls.__name__)
            _session_cache[cls.__name__] = {}

        if 'http_session' not in _session_cache:
            log.debug("Creating a new http cache object at %s for %s", session_index, cls.__name__)
            _session_cache['http_session'] = {}

        if 'http_session' in kwargs:
            log.info("Using existent http session at kwargs for %s", cls.__name__)
            _session_cache['http_session'][session_index] = kwargs['http_session']
        else:
            if session_index in _session_cache['http_session']:
                log.info(f"Reusing http session at index %s for %s", session_index, cls.__name__)
                kwargs['http_session'] = _session_cache['http_session'][session_index]
            else:
                log.info("Creating a new http session at index %s for %s", session_index, cls.__name__)
                kwargs['http_session'] = aiohttp.ClientSession(raise_for_status=True)

        if session_index in _session_cache[cls.__name__]:
            raise IndexError(f"There's already a {cls.__name__} session at index {session_index}")
        else:
            log.info("Creating a new %s session at %s", cls.__name__, session_index)
            _session_cache[cls.__name__][session_index] = super().__new__(cls)
            log.debug("Initializing instance for %s", cls.__name__)
            _session_cache[cls.__name__][session_index].__init__(**kwargs)

        return _session_cache[cls.__name__][session_index]

    @classmethod
    async def destroy_session(cls, session_index: int, no_fail: bool = False) -> None:
        """
        Destroy an instance of module at `session_index` and remove from cache.
        :param session_index: Session number
        :param no_fail: suppress errors if there is no session at given index
        """
        if cls.__name__ in _session_cache and session_index in _session_cache[cls.__name__]:
            del _session_cache[cls.__name__][session_index]
            await _session_cache['http_session'][session_index].close()
            del _session_cache['http_session'][session_index]
        else:
            if not no_fail:
                raise IndexError(f"There's no session at {session_index}")

    @classmethod
    def get_session(cls, session_index: int) -> 'Base':
        """
        Get an instance of module from cache at `session_index`.
        If session isn't present in cache, it will returns IndexError
        :param session_index: session number
        :return: instance of module
        """
        if cls.__name__ not in _session_cache or session_index not in _session_cache[cls.__name__]:
            raise IndexError(f"There's no session for {cls.__name__} at {session_index}")

        return _session_cache[cls.__name__][session_index]

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
    async def get_html(response: Response) -> BeautifulSoup:
        """
        get html parsed from response
        It's a convenient helper for `request`
        """
        return BeautifulSoup(response.content, 'html.parser')

    async def request_json(self, *args, **kwargs) -> Dict[str, Any]:
        """
        make a new http request and returns json data
        It's a convenient helper for `request`
        """
        response = await self.request(*args, **kwargs)
        return json.loads(response.content)

    async def request_json_from_js(
            self,
            *args,
            script_index: int = 0,
            **kwargs,
    ) -> Dict[str, Any]:
        """
        make a new http request and returns json data from javascript at given index
        It's a convenient helper for `request`
        :param args: request args
        :param script_index: index of script at html page
        :param kwargs: request kwargs
        :return: json_data as Dict
        """
        html = await self.request_html(*args, **kwargs)
        javascript = html.find_all('script')[script_index]
        return self.get_json_from_js(javascript)

    async def request_html(self, *args, **kwargs) -> BeautifulSoup:
        """
        make a new http request and returns html
        It's a convenient helper for `request`
        """
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
    ) -> Response:
        """
        Make a new http request
        :param url: URL to request
        :param params: Http parameters
        :param data: Form data
        :param headers: Http headers
        :param auto_recovery: If defined and http request fail, it will try again
        :param kwargs: Extra kwargs passed directly to http request
        :return: `Request`
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
                    return Response(
                        response.status,
                        response.request_info,
                        response.cookies,
                        await response.text(),
                        response.content_type,
                    )
            except aiohttp.ClientResponseError as exception:
                log.debug("Response error %s", exception.status)

                if 400 <= exception.status <= 499:
                    raise exception from None

                if auto_recovery:
                    log.debug("Auto recovering in 5 seconds")
                    await asyncio.sleep(5)
                    continue
                else:
                    raise exception from None
