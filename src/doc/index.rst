.. Lara Maia <dev@lara.click> 2015 ~ 2018
.. .
.. The stlib is free software: you can redistribute it and/or
.. modify it under the terms of the GNU General Public License as
.. published by the Free Software Foundation, either version 3 of
.. the License, or (at your option) any later version.
.. .
.. The stlib is distributed in the hope that it will be useful,
.. but WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
.. See the GNU General Public License for more details.
.. .
.. You should have received a copy of the GNU General Public License
.. along with this program. If not, see http://www.gnu.org/licenses/.


stlib reference
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Universe Module
--------------------

.. automodule:: universe

.. autofunction:: generate_steam_code

.. autofunction:: generate_device_id

.. autofunction:: generate_time_hash

.. autofunction:: encrypt_password

Data Structures:
^^^^^^^^^^^^^^^^

.. autoclass:: SteamKey

Client Module:
--------------

.. automodule:: client

.. autoclass:: SteamApiExecutor
   :members:
   :undoc-members:

.. autoclass:: SteamGameServer
   :members:
   :undoc-members:

Exceptions:
^^^^^^^^^^^

.. autoexception:: SteamAPIError

.. autoexception:: SteamGameServerError

Webapi Module
-------------

.. automodule:: webapi

.. autoclass:: SteamWebAPI
   :members:
   :undoc-members:

.. autoclass:: Login
   :members:
   :undoc-members:

.. autofunction:: js_to_json

Data Structures:
^^^^^^^^^^^^^^^^

.. autoclass:: LoginData

.. autoclass:: Confirmation

.. autoclass:: Game

.. autoclass:: Badge

Exceptions:
^^^^^^^^^^^

.. autoexception:: LoginError

.. autoexception:: LoginBlockedError

.. autoexception:: CaptchaError

.. autoexception:: MailCodeError

.. autoexception:: TwoFactorCodeError

.. autoexception:: SMSCodeError

.. autoexception:: PhoneNotRegistered

.. autoexception:: AuthenticatorExists

.. autoexception:: RevocationError

Plugins
-------

.. automodule:: plugins

.. autoclass:: Manager
   :members:
   :undoc-members:

Exceptions:
^^^^^^^^^^^

.. autoexception:: PluginError

.. autoexception:: PluginNotFoundError

.. autoexception:: PluginLoaderError

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
