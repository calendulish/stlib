.. Lara Maia <dev@lara.monster> 2015 ~ 2020
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

.. autofunction:: generate_otp_code

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

.. autofunction:: get_session

.. autofunction:: js_to_json

Data Structures:
^^^^^^^^^^^^^^^^

.. autoclass:: Confirmation

.. autoclass:: Game

.. autoclass:: Badge

Exceptions:
^^^^^^^^^^^

.. autoexception:: BadgeError

.. autoexception:: SMSCodeError

.. autoexception:: PhoneNotRegistered

.. autoexception:: AuthenticatorExists

.. autoexception:: RevocationError

Login
-----

.. automodule:: login

.. autoclass:: Login
   :members:
   :undoc-members:

.. autofunction:: get_session

Data Structures:
^^^^^^^^^^^^^^^^

.. autoclass:: LoginData

Exceptions:
^^^^^^^^^^^

.. autoexception:: LoginError

.. autoexception:: LoginBlockedError

.. autoexception:: MailCodeError

.. autoexception:: TwoFactorCodeError

Plugins
-------

.. automodule:: plugins

.. autoclass:: Plugin
   :members:
   :undoc-members:

.. autoclass:: Manager
   :members:
   :undoc-members:

.. autofunction:: plugin_manager

.. autofunction:: has_plugin

.. autofunction:: get_plugin

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
