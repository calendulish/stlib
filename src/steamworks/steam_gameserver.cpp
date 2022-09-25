/*
/ Lara Maia <dev@lara.monster> 2015 ~ 2022
/
/ The stlib is free software: you can redistribute it and/or
/ modify it under the terms of the GNU General Public License as
/ published by the Free Software Foundation, either version 3 of
/ the License, or (at your option) any later version.
/
/ The stlib is distributed in the hope that it will be useful,
/ but WITHOUT ANY WARRANTY; without even the implied warranty of
/ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
/ See the GNU General Public License for more details.
/
/ You should have received a copy of the GNU General Public License
/ along with this program. If not, see http://www.gnu.org/licenses/.
*/

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
#include <charconv>

#include "steam/steam_api.h"
#include "steam/steam_gameserver.h"

#include "common.h"

typedef struct
{
    PyObject_HEAD
    uint16 eServerModeNoAuthentication_;
    uint16 eServerModeAuthentication_;
    uint16 eServerModeAuthenticationAndSecure_;
    const char *STEAMGAMESERVER_INTERFACE_VERSION_;
    uint16 STEAMGAMESERVER_QUERY_PORT_SHARED_;
} SteamGameServerObject;

static PyObject *SteamGameServerObjectNew(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    SteamGameServerObject *self;

    self = (SteamGameServerObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        self->eServerModeNoAuthentication_ = 1;
        self->eServerModeAuthentication_ = 2;
        self->eServerModeAuthenticationAndSecure_ = 3;
        self->STEAMGAMESERVER_INTERFACE_VERSION_ = STEAMGAMESERVER_INTERFACE_VERSION;
        self->STEAMGAMESERVER_QUERY_PORT_SHARED_ = STEAMGAMESERVER_QUERY_PORT_SHARED;
    }

    return (PyObject *)self;
}

static int SteamGameServerObjectInit(SteamGameServerObject *self, PyObject *args, PyObject *kwds)
{
    if (!SteamAPI_IsSteamRunning())
    {
        PyErr_SetString(PyExc_ProcessLookupError, "Steam is not running");
        return -1;
    }

    uint32 appID;
    uint32 unIP;
    uint16 usGamePort;
    uint16 usQueryPort = STEAMGAMESERVER_QUERY_PORT_SHARED;
    uint16 eServerMode = eServerModeNoAuthentication;
    const char *pchVersionString = STEAMGAMESERVER_INTERFACE_VERSION;

    if (!PyArg_ParseTuple(args, "IIH|HHs", &appID, &unIP, &usGamePort, &usQueryPort, &eServerMode, &pchVersionString))
    {
        return -1;
    }

    char appid_string[32];
    std::to_chars(appid_string, appid_string + 32, appID);

    if (setenv("SteamAppId", appid_string, true) != 0)
    {
        PyErr_SetString(PyExc_AttributeError, "Error when setting AppID");
        return -1;
    }

    if (!SteamGameServer_Init(unIP, usGamePort, usQueryPort, (EServerMode)eServerMode, pchVersionString))
    {
        PyErr_SetString(PyExc_AttributeError, "Failed to initialize SteamGameServer");
        return -1;
    }

    SteamGameServer()->SetModDir("");
    SteamGameServer()->SetProduct("stlib");
    SteamGameServer()->SetGameDescription("stlib server");
    SteamGameServer()->LogOnAnonymous();

    return 0;
}

static PyObject *server_shutdown(PyObject *self, PyObject *args)
{
    SteamGameServer_Shutdown();

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *server_get_steamid(PyObject *self, PyObject *args)
{
    CSteamID SteamID = SteamGameServer_GetSteamID();

    return PyLong_FromUnsignedLongLong(SteamID.ConvertToUint64());
}

static PyObject *server_get_seconds_since_app_active(PyObject *self, PyObject *args)
{
    uint32 seconds = SteamGameServerUtils()->GetSecondsSinceAppActive();

    return PyLong_FromUnsignedLong(seconds);
}

static PyObject *server_get_seconds_since_computer_active(PyObject *self, PyObject *args)
{
    uint32 seconds = SteamGameServerUtils()->GetSecondsSinceComputerActive();

    return PyLong_FromUnsignedLong(seconds);
}

static PyObject *server_get_connected_universe(PyObject *self, PyObject *args)
{
    EUniverse universe = SteamGameServerUtils()->GetConnectedUniverse();

    return PyLong_FromLong(universe);
}

static PyObject *server_get_server_real_time(PyObject *self, PyObject *args)
{
    uint32 time = SteamGameServerUtils()->GetServerRealTime();

    return PyLong_FromUnsignedLong(time);
}

static PyObject *server_get_ip_country(PyObject *self, PyObject *args)
{
    const char *country = SteamGameServerUtils()->GetIPCountry();

    return PyUnicode_FromString(country);
}

static PyObject *server_get_current_battery_power(PyObject *self, PyObject *args)
{
    uint8 current = SteamGameServerUtils()->GetCurrentBatteryPower();

    return PyLong_FromUnsignedLong(current);
}

static PyObject *server_get_appid(PyObject *self, PyObject *args)
{
    uint32 appid = SteamGameServerUtils()->GetAppID();

    return PyLong_FromUnsignedLong(appid);
}

static PyObject *server_get_ipc_call_count(PyObject *self, PyObject *args)
{
    uint32 call_count = SteamGameServerUtils()->GetIPCCallCount();

    return PyLong_FromUnsignedLong(call_count);
}

static PyObject *server_is_steam_running_in_vr(PyObject *self, PyObject *args)
{
    bool result = SteamGameServerUtils()->IsSteamRunningInVR();

    return PyBool_FromLong(result);
}

static PyObject *server_is_steam_in_big_picture_mode(PyObject *self, PyObject *args)
{
    bool result = SteamGameServerUtils()->IsSteamInBigPictureMode();

    return PyBool_FromLong(result);
}

static PyObject *server_is_steam_china_launcher(PyObject *self, PyObject *args)
{
    bool result = SteamGameServerUtils()->IsSteamChinaLauncher();

    return PyBool_FromLong(result);
}

static PyObject *server_is_steam_running_on_steam_deck(PyObject *self, PyObject *args)
{
    bool result = SteamGameServerUtils()->IsSteamRunningOnSteamDeck();

    return PyBool_FromLong(result);
}

static PyMethodDef SteamGameServerMethods[] = {
    {
        "shutdown",
        server_shutdown,
        METH_NOARGS,
        PyDoc_STR("shutdown()\n--\n\n"
                  "Shuts down the Steamworks GameServer API, releases pointers and frees memory.\n"
                  ":return: `None`"),
    },
    {
        "get_steamid",
        server_get_steamid,
        METH_NOARGS,
        PyDoc_STR("get_steamid()\n--\n\n"
                  "Gets the Steam ID of the game server.\n"
                  ":return: `int`"),
    },
    {
        "get_seconds_since_app_active",
        server_get_seconds_since_app_active,
        METH_NOARGS,
        PyDoc_STR("get_seconds_since_app_active()\n--\n\n"
                  "Returns the number of seconds since the application was active.\n"
                  ":return: `int`"),
    },
    {
        "get_seconds_since_computer_active",
        server_get_seconds_since_computer_active,
        METH_NOARGS,
        PyDoc_STR("get_seconds_since_computer_active()\n--\n\n"
                  "Returns the number of seconds since the user last moved the mouse.\n"
                  ":return: `int`"),
    },
    {
        "get_connected_universe",
        server_get_connected_universe,
        METH_NOARGS,
        PyDoc_STR("get_connected_universe()\n--\n\n"
                  "Gets the universe that the current client is connecting to\n"
                  ":return: `int`"),
    },
    {
        "get_server_real_time",
        server_get_server_real_time,
        METH_NOARGS,
        PyDoc_STR("get_server_real_time()\n--\n\n"
                  "Returns the Steam server time in Unix epoch format.\n"
                  ":return: `int` (Number of seconds since Jan 1, 1970 UTC)"),
    },
    {
        "get_ip_country",
        server_get_ip_country,
        METH_NOARGS,
        PyDoc_STR("get_ip_country()\n--\n\n"
                  "Returns the 2 digit ISO 3166-1-alpha-2 format country code which client is running in.\n"
                  ":return: `str`"),
    },
    {
        "get_current_battery_power",
        server_get_current_battery_power,
        METH_NOARGS,
        PyDoc_STR("get_current_battery_power()\n--\n\n"
                  "Gets the current amount of battery power on the computer.\n"
                  ":return: `int`"),
    },
    {
        "get_appid",
        server_get_appid,
        METH_NOARGS,
        PyDoc_STR("get_appid()\n--\n\n"
                  "Gets the App ID of the current process.\n"
                  ":return: `int`"),
    },
    {
        "get_ipc_call_count",
        server_get_ipc_call_count,
        METH_NOARGS,
        PyDoc_STR("get_ipc_call_count()\n--\n\n"
                  "Returns the number of IPC calls made since the last time this function was called.\n"
                  ":return: `int`"),
    },
    {
        "is_steam_running_in_vr",
        server_is_steam_running_in_vr,
        METH_NOARGS,
        PyDoc_STR("is_steam_running_in_vr()\n--\n\n"
                  "Checks if Steam is running in VR mode.\n"
                  ":return: `bool`"),
    },
    {
        "is_steam_in_big_picture_mode",
        server_is_steam_in_big_picture_mode,
        METH_NOARGS,
        PyDoc_STR("is_steam_in_big_picture_mode()\n--\n\n"
                  "Checks if Steam & the Steam Overlay are running in Big Picture mode.\n"
                  ":return: `bool`"),
    },
    {
        "is_steam_china_launcher",
        server_is_steam_china_launcher,
        METH_NOARGS,
        PyDoc_STR("is_steam_china_launcher()\n--\n\n"
                  "Returns whether the current launcher is a Steam China launcher.\n"
                  ":return: `bool`"),
    },
    {
        "is_steam_running_on_steam_deck",
        server_is_steam_running_on_steam_deck,
        METH_NOARGS,
        PyDoc_STR("is_steam_running_on_steam_deck()\n--\n\n"
                  "Checks if Steam is running on a Steam Deck device.\n"
                  ":return: `bool`"),
    },
    {NULL},
};

static PyMemberDef SteamGameServerMembers[] = {
    {
        "eServerModeNoAuthentication",
        T_USHORT,
        offsetof(SteamGameServerObject, eServerModeNoAuthentication_),
        READONLY,
        PyDoc_STR("Don't authenticate user logins and don't list on the server list."),
    },
    {
        "eServerModeAuthentication",
        T_USHORT,
        offsetof(SteamGameServerObject, eServerModeAuthentication_),
        READONLY,
        PyDoc_STR("Authenticate users, list on the server list, don't run VAC on clients that connect."),
    },
    {
        "eServerModeAuthenticationAndSecure",
        T_USHORT,
        offsetof(SteamGameServerObject, eServerModeAuthenticationAndSecure_),
        READONLY,
        PyDoc_STR("Authenticate users, list on the server list and VAC protect clients."),
    },
    {
        "STEAMGAMESERVER_INTERFACE_VERSION",
        T_STRING,
        offsetof(SteamGameServerObject, STEAMGAMESERVER_INTERFACE_VERSION_),
        READONLY,
        PyDoc_STR("Internal SteamGameServer interface version"),
    },
    {
        "STEAMGAMESERVER_QUERY_PORT_SHARED",
        T_USHORT,
        offsetof(SteamGameServerObject, STEAMGAMESERVER_QUERY_PORT_SHARED_),
        READONLY,
        PyDoc_STR("Enable GameSocketShare mode"),
    },
    {NULL},
};

PyTypeObject SteamGameServerType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "stlib.steamworks.SteamGameServer",
    sizeof(SteamGameServerObject),
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    PyDoc_STR("`SteamGameServer` client.\n"
              "This interface should be accessed preferably using `stlib.client.SteamGameServer`"),
    0,
    0,
    0,
    0,
    0,
    0,
    SteamGameServerMethods,
    SteamGameServerMembers,
    0,
    0,
    0,
    0,
    0,
    0,
    (initproc)SteamGameServerObjectInit,
    0,
    SteamGameServerObjectNew,
};
