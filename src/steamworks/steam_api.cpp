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

#include "steam/steam_api.h"

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
    sprintf(appid_string, "SteamAppId=%u", appID);

    if (putenv(appid_string) != 0)
    {
        PyErr_SetString(PyExc_AttributeError, "Error when setting AppID");
        return -1;
    }

    if (!SteamAPI_Init())
    {
        PyErr_SetString(PyExc_AttributeError, "Failed to initialize SteamAPI");
        return -1;
    }

    if (putenv("SteamAppId=") != 0)
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
    {"shutdown", steam_api_shutdown, METH_NOARGS, NULL},
    {"restart_app_if_necessary", restart_app_if_necessary, METH_VARARGS, NULL},
    {"is_steam_running", is_steam_running, METH_NOARGS, NULL},
    {"get_seconds_since_app_active", get_seconds_since_app_active, METH_NOARGS, NULL},
    {"get_seconds_since_computer_active", get_seconds_since_computer_active, METH_NOARGS, NULL},
    {"get_connected_universe", get_connected_universe, METH_NOARGS, NULL},
    {"get_server_real_time", get_server_real_time, METH_NOARGS, NULL},
    {"get_ip_country", get_ip_country, METH_NOARGS, NULL},
    {"get_current_battery_power", get_current_battery_power, METH_NOARGS, NULL},
    {"get_appid", get_appid, METH_NOARGS, NULL},
    {"get_ipc_call_count", get_ipc_call_count, METH_NOARGS, NULL},
    {"is_steam_running_in_vr", is_steam_running_in_vr, METH_NOARGS, NULL},
    {"is_steam_in_big_picture_mode", is_steam_in_big_picture_mode, METH_NOARGS, NULL},
    {"is_steam_china_launcher", is_steam_china_launcher, METH_NOARGS, NULL},
    {"is_steam_running_on_steam_deck", is_steam_running_on_steam_deck, METH_NOARGS, NULL},
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
    0,
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
