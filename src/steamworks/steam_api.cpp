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

#include "common.h"

typedef struct
{
    PyObject_HEAD
} SteamAPIObject;

static int SteamAPIObjectInit(SteamAPIObject *self, PyObject *args, PyObject *kwds)
{
    if (!SteamAPI_IsSteamRunning())
    {
        PyErr_SetString(PyExc_ProcessLookupError, "Steam is not running");
        return -1;
    }

    uint32 appID;

    if (!PyArg_ParseTuple(args, "I", &appID))
    {
        return -1;
    }

    char appid_string[32];
    std::to_chars(appid_string, appid_string + sizeof(appID), appID);

    if (setenv("SteamAppId", appid_string, true) != 0)
    {
        PyErr_SetString(PyExc_AttributeError, "Error when setting AppID");
        return -1;
    }

    if (!SteamAPI_Init())
    {
        PyErr_SetString(PyExc_AttributeError, "Failed to initialize SteamAPI");
        return -1;
    }

    if (setenv("SteamAppId", "", true) != 0)
    {
        PyErr_SetString(PyExc_AttributeError, "Error when unsetting AppID");
        return -1;
    }

    if (!SteamUser()->BLoggedOn())
    {
        PyErr_SetString(PyExc_AttributeError, "User isn't logged in");
        return -1;
    }

    if (!SteamInput()->Init(false))
    {
        PyErr_SetString(PyExc_AttributeError, "Failed to initialize SteamInput");
        return -1;
    }

    return 0;
}

static PyObject *steam_api_shutdown(PyObject *self, PyObject *args)
{
    SteamAPI_Shutdown();

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *restart_app_if_necessary(PyObject *self, PyObject *args)
{
    uint32 unOwnAppID;
    bool result = 0;

    if (!PyArg_ParseTuple(args, "I", &unOwnAppID))
    {
        return NULL;
    }

    if (SteamAPI_RestartAppIfNecessary(unOwnAppID))
    {
        result = 1;
    }

    return PyBool_FromLong(result);
}

static PyObject *is_steam_running(PyObject *self, PyObject *args)
{
    bool result = SteamAPI_IsSteamRunning();

    return PyBool_FromLong(result);
}

static PyObject *get_seconds_since_app_active(PyObject *self, PyObject *args)
{
    uint32 seconds = SteamUtils()->GetSecondsSinceAppActive();

    return PyLong_FromUnsignedLong(seconds);
}

static PyObject *get_seconds_since_computer_active(PyObject *self, PyObject *args)
{
    uint32 seconds = SteamUtils()->GetSecondsSinceComputerActive();

    return PyLong_FromUnsignedLong(seconds);
}

static PyObject *get_connected_universe(PyObject *self, PyObject *args)
{
    EUniverse universe = SteamUtils()->GetConnectedUniverse();

    return PyLong_FromLong(universe);
}

static PyObject *get_server_real_time(PyObject *self, PyObject *args)
{
    uint32 time = SteamUtils()->GetServerRealTime();

    return PyLong_FromUnsignedLong(time);
}

static PyObject *get_ip_country(PyObject *self, PyObject *args)
{
    const char *country = SteamUtils()->GetIPCountry();

    return PyUnicode_FromString(country);
}

static PyObject *get_current_battery_power(PyObject *self, PyObject *args)
{
    uint8 current = SteamUtils()->GetCurrentBatteryPower();

    return PyLong_FromUnsignedLong(current);
}

static PyObject *get_appid(PyObject *self, PyObject *args)
{
    uint32 appid = SteamUtils()->GetAppID();

    return PyLong_FromUnsignedLong(appid);
}

static PyObject *get_ipc_call_count(PyObject *self, PyObject *args)
{
    uint32 call_count = SteamUtils()->GetIPCCallCount();

    return PyLong_FromUnsignedLong(call_count);
}

static PyObject *is_steam_running_in_vr(PyObject *self, PyObject *args)
{
    bool result = SteamUtils()->IsSteamRunningInVR();

    return PyBool_FromLong(result);
}

static PyObject *is_steam_in_big_picture_mode(PyObject *self, PyObject *args)
{
    bool result = SteamUtils()->IsSteamInBigPictureMode();

    return PyBool_FromLong(result);
}

static PyObject *is_steam_china_launcher(PyObject *self, PyObject *args)
{
    bool result = SteamUtils()->IsSteamChinaLauncher();

    return PyBool_FromLong(result);
}

static PyObject *is_steam_running_on_steam_deck(PyObject *self, PyObject *args)
{
    bool result = SteamUtils()->IsSteamRunningOnSteamDeck();

    return PyBool_FromLong(result);
}

static PyMethodDef SteamApiMethods[] = {
    {
        "shutdown",
        steam_api_shutdown,
        METH_NOARGS,
        PyDoc_STR("shutdown()\n--\n\n"
                  "Shuts down the Steamworks API, releases pointers and frees memory.\n"
                  ":return: `None`"),
    },
    {
        "restart_app_if_necessary",
        restart_app_if_necessary,
        METH_VARARGS,
        PyDoc_STR("restart_app_if_necessary(appid)\n--\n\n"
                  "Checks if your executable was launched through Steam and relaunches it through Steam if it wasn't.\n"
                  ":param appid: `int`\n"
                  ":return: `bool`"),
    },
    {
        "is_steam_running",
        is_steam_running,
        METH_NOARGS,
        PyDoc_STR("is_steam_running()\n--\n\n"
                  "Checks if Steam is running.\n"
                  ":return: `bool`"),
    },
    {
        "get_seconds_since_app_active",
        get_seconds_since_app_active,
        METH_NOARGS,
        PyDoc_STR("get_seconds_since_app_active()\n--\n\n"
                  "Returns the number of seconds since the application was active.\n"
                  ":return: `int`"),
    },
    {
        "get_seconds_since_computer_active",
        get_seconds_since_computer_active,
        METH_NOARGS,
        PyDoc_STR("get_seconds_since_computer_active()\n--\n\n"
                  "Returns the number of seconds since the user last moved the mouse.\n"
                  ":return: `int`"),
    },
    {
        "get_connected_universe",
        get_connected_universe,
        METH_NOARGS,
        PyDoc_STR("get_connected_universe()\n--\n\n"
                  "Gets the universe that the current client is connecting to\n"
                  ":return: `int`"),
    },
    {
        "get_server_real_time",
        get_server_real_time,
        METH_NOARGS,
        PyDoc_STR("get_server_real_time()\n--\n\n"
                  "Returns the Steam server time in Unix epoch format.\n"
                  ":return: `int` (Number of seconds since Jan 1, 1970 UTC)"),
    },
    {
        "get_ip_country",
        get_ip_country,
        METH_NOARGS,
        PyDoc_STR("get_ip_country()\n--\n\n"
                  "Returns the 2 digit ISO 3166-1-alpha-2 format country code which client is running in.\n"
                  ":return: `str`"),
    },
    {
        "get_current_battery_power",
        get_current_battery_power,
        METH_NOARGS,
        PyDoc_STR("get_current_battery_power()\n--\n\n"
                  "Gets the current amount of battery power on the computer.\n"
                  ":return: `int`"),
    },
    {
        "get_appid",
        get_appid,
        METH_NOARGS,
        PyDoc_STR("get_appid()\n--\n\n"
                  "Gets the App ID of the current process.\n"
                  ":return: `int`"),
    },
    {
        "get_ipc_call_count",
        get_ipc_call_count,
        METH_NOARGS,
        PyDoc_STR("get_ipc_call_count()\n--\n\n"
                  "Returns the number of IPC calls made since the last time this function was called.\n"
                  ":return: `int`"),
    },
    {
        "is_steam_running_in_vr",
        is_steam_running_in_vr,
        METH_NOARGS,
        PyDoc_STR("is_steam_running_in_vr()\n--\n\n"
                  "Checks if Steam is running in VR mode.\n"
                  ":return: `bool`"),
    },
    {
        "is_steam_in_big_picture_mode",
        is_steam_in_big_picture_mode,
        METH_NOARGS,
        PyDoc_STR("is_steam_in_big_picture_mode()\n--\n\n"
                  "Checks if Steam & the Steam Overlay are running in Big Picture mode.\n"
                  ":return: `bool`"),
    },
    {
        "is_steam_china_launcher",
        is_steam_china_launcher,
        METH_NOARGS,
        PyDoc_STR("is_steam_china_launcher()\n--\n\n"
                  "Returns whether the current launcher is a Steam China launcher.\n"
                  ":return: `bool`"),
    },
    {
        "is_steam_running_on_steam_deck",
        is_steam_running_on_steam_deck,
        METH_NOARGS,
        PyDoc_STR("is_steam_running_on_steam_deck()\n--\n\n"
                  "Checks if Steam is running on a Steam Deck device.\n"
                  ":return: `bool`"),
    },
    {NULL},
};

PyTypeObject SteamAPIType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "stlib.steamworks.SteamAPI",
    sizeof(SteamAPIObject),
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
    PyDoc_STR("`SteamAPI` Client.\n"
              "This interface should be accessed preferably using `stlib.client.SteamAPIExecutor`"),
    0,
    0,
    0,
    0,
    0,
    0,
    SteamApiMethods,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    (initproc)SteamAPIObjectInit,
    0,
    PyType_GenericNew,
};
