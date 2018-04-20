/*
/ Lara Maia <dev@lara.click> 2015 ~ 2018
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

typedef struct {
    PyObject_HEAD
} SteamUser_Object;

static PyObject *SteamUser_get_steam_id(SteamUser_Object *self) {
    CSteamID result = SteamUser()->GetSteamID();

    return PyLong_FromUnsignedLongLong(result.ConvertToUint64());
}

static int SteamUser_init(SteamUser_Object *self, PyObject *args, PyObject *kwds) {
    if (!SteamAPI_IsSteamRunning()) {
        PyErr_SetString(PyExc_ProcessLookupError, "Steam is not running");
        return -1;
    }

    if (!SteamUser()) {
        PyErr_SetString(PyExc_AttributeError, "Interface pointers for SteamUser is not populated");
        return -1;
    }

    return 0;
}

static PyMethodDef SteamUser_methods[] = {
    {"get_steam_id", (PyCFunction) SteamUser_get_steam_id, METH_NOARGS, NULL},
    {NULL},
};

static PyTypeObject SteamUserType = {
    PyObject_HEAD_INIT(NULL)
    "stlib.steam_api.SteamUser",
    sizeof(SteamUser_Object),
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    0, 0, 0, 0, 0, 0, 0,
    SteamUser_methods,
    0, 0, 0, 0, 0, 0, 0,
    (initproc)SteamUser_init,
    0,
    PyType_GenericNew,
};
