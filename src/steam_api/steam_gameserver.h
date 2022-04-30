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
#include "steam/steam_api.h"
#include "steam/steam_gameserver.h"

typedef struct {
    PyObject_HEAD
} SteamGameServer_Object;

static PyObject *SteamGameServer_get_steam_id(SteamGameServer_Object *self) {
    CSteamID result = SteamGameServer_GetSteamID();

    return PyLong_FromUnsignedLongLong(result.ConvertToUint64());
}

static PyObject *SteamGameServer_get_server_real_time(SteamGameServer_Object *self) {
    unsigned int result = SteamGameServerUtils()->GetServerRealTime();

    return PyLong_FromUnsignedLong(result);
}

static PyObject *SteamGameServer_log_on_anonymous(SteamGameServer_Object *self) {
    SteamGameServer()->LogOnAnonymous();

    Py_INCREF(Py_None);
    return Py_None;
}

static int SteamGameServer_init(SteamGameServer_Object *self, PyObject *args, PyObject *kwds) {
    if (!SteamAPI_IsSteamRunning()) {
        PyErr_SetString(PyExc_ProcessLookupError, "Steam is not running");
        return -1;
    }

    if (!SteamGameServer()) {
        PyErr_SetString(PyExc_AttributeError, "Interface pointers for SteamGameServer is not populated");
        return -1;
    }

    return 0;
}

static PyMethodDef SteamGameServer_methods[] = {
    {"log_on_anonymous", (PyCFunction) SteamGameServer_log_on_anonymous,     METH_NOARGS, NULL},
    {"get_server_time",  (PyCFunction) SteamGameServer_get_server_real_time, METH_NOARGS, NULL},
    {"get_steam_id",     (PyCFunction) SteamGameServer_get_steam_id,         METH_NOARGS, NULL},
    {NULL},
};

static PyTypeObject SteamGameServerType = {
    PyObject_HEAD_INIT(NULL)
    "stlib.steam_api.SteamGameServer",
    sizeof(SteamGameServer_Object),
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    0, 0, 0, 0, 0, 0, 0,
    SteamGameServer_methods,
    0, 0, 0, 0, 0, 0, 0,
    (initproc)SteamGameServer_init,
    0,
    PyType_GenericNew,
};
