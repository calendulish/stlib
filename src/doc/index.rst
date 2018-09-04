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

Authenticator Module
--------------------

.. automodule:: authenticator

.. autoclass:: AndroidDebugBridge
   :members:
   :undoc-members:

.. autofunction:: get_code

.. autofunction:: generate_device_id

Data Structures:
^^^^^^^^^^^^^^^^

.. autofunction:: AuthenticatorCode

Exceptions:
^^^^^^^^^^^

.. autoexception:: DeviceError

.. autoexception:: RootError

.. autoexception:: LoginError

.. autoexception:: SteamGuardError

.. autoexception:: MobileAppError

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

.. autofunction:: encrypt_password

.. autofunction:: new_time_hash

.. autofunction:: js_to_json

Data Structures:
^^^^^^^^^^^^^^^^

.. autoclass:: SteamKey

.. autoclass:: Confirmation

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


Plugins
-------

.. automodule:: plugins

.. autofunction:: get_plugin

.. autofunction:: has_plugin

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
