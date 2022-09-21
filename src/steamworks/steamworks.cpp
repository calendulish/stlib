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

#include "steam/steam_api.h"

#include "steamworks.h"

static PyMethodDef steamworks_methods[] = {
    {NULL},
};

static struct PyModuleDef steamworks_module = {
    PyModuleDef_HEAD_INIT,
    "stlib.steamworks",
    PyDoc_STR("SteamWorks SDK python bindings"),
    -1,
    steamworks_methods,
};

PyMODINIT_FUNC PyInit_steamworks(void)
{
    PyObject *module;

    if (PyType_Ready(&SteamAPIType) < 0)
    {
        return NULL;
    }

    if (PyType_Ready(&SteamGameServerType) < 0)
    {
        return NULL;
    }

    module = PyModule_Create(&steamworks_module);
    if (module == NULL)
    {
        return NULL;
    }

    Py_INCREF(&SteamAPIType);
    Py_INCREF(&SteamGameServerType);

    if (PyModule_AddObject(module, "SteamAPI", (PyObject *)&SteamAPIType) < 0)
    {
        Py_DECREF(&SteamAPIType);
        Py_DECREF(module);
        return NULL;
    }

    if (PyModule_AddObject(module, "SteamGameServer", (PyObject *)&SteamGameServerType) < 0)
    {
        Py_DECREF(&SteamGameServerType);
        Py_DECREF(module);
        return NULL;
    }

    return module;
}
