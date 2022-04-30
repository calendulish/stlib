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

#include <Python.h>

// Steam Public API
#include "steam/steam_api.h"
#include "steam/steam_gameserver.h"

// Python Extensions
#include "steam_user.h"
#include "steam_utils.h"
#include "steam_gameserver.h"

static PyObject *server_shutdown(PyObject *self, PyObject *args) {
    SteamGameServer_Shutdown();

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *server_init(PyObject *self, PyObject *args) {
    if (!SteamAPI_IsSteamRunning()) {
        PyErr_SetString(PyExc_ProcessLookupError, "Steam is not running");
        return NULL;
    }

    uint32 ip;
    uint16 game_port;
    uint16 query_port = MASTERSERVERUPDATERPORT_USEGAMESOCKETSHARE;
    EServerMode server_mode = eServerModeNoAuthentication;
    const char *version_string = STEAMGAMESERVER_INTERFACE_VERSION;

    if (!PyArg_ParseTuple(args, "li|iss", &ip, &game_port, &query_port, &server_mode, &version_string)
        ) {
        PyErr_SetString(PyExc_TypeError, "server_init missing required positional arguments");
        return NULL;
    }

    bool result = SteamGameServer_Init(ip, game_port, query_port, server_mode, version_string);

    return PyBool_FromLong(result);
}

static PyObject *shutdown(PyObject *self, PyObject *args) {
    SteamAPI_Shutdown();

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *is_steam_running(PyObject *self, PyObject *args) {
    bool result = SteamAPI_IsSteamRunning();

    return PyBool_FromLong(result);
}

static PyObject *init(PyObject *self, PyObject *args) {
    if (!SteamAPI_IsSteamRunning()) {
        PyErr_SetString(PyExc_ProcessLookupError, "Steam is not running");
        return NULL;
    }

    bool result = SteamAPI_Init();

    return PyBool_FromLong(result);
}

static PyMethodDef steam_api_methods[] = {
    {"init",              init,             METH_NOARGS,  NULL},
    {"server_init",       server_init,      METH_VARARGS, NULL},
    {"_is_steam_running", is_steam_running, METH_NOARGS,  NULL},
    {"shutdown",          shutdown,         METH_NOARGS,  NULL},
    {"server_shutdown",   server_shutdown,  METH_NOARGS,  NULL},
    {NULL,                NULL,             0,            NULL},
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "stlib.steam_api",
    "Steam API.",
    -1,
    steam_api_methods
};

PyMODINIT_FUNC PyInit_steam_api(void) {
    PyObject *module;

    if (PyType_Ready(&SteamUserType) < 0) {
        PyErr_SetString(PyExc_AttributeError, "Unable to initialize SteamUser");
        return NULL;
    }

    if (PyType_Ready(&SteamUtilsType) < 0) {
        PyErr_SetString(PyExc_AttributeError, "Unable to initialize SteamUtils");
        return NULL;
    }

    if (PyType_Ready(&SteamGameServerType) < 0) {
        PyErr_SetString(PyExc_AttributeError, "Unable to initialize SteamGameServer");
        return NULL;
    }

    module = PyModule_Create(&moduledef);

    if (module == NULL) {
        PyErr_SetString(PyExc_AttributeError, "Unable to initialize steam_api");
        return NULL;
    }

    Py_INCREF(&SteamUserType);
    Py_INCREF(&SteamUtilsType);
    Py_INCREF(&SteamGameServerType);

    PyModule_AddObject(module, "SteamUser", (PyObject * ) & SteamUserType);
    PyModule_AddObject(module, "SteamUtils", (PyObject * ) & SteamUtilsType);
    PyModule_AddObject(module, "SteamGameServer", (PyObject * ) & SteamGameServerType);

    return module;
}
