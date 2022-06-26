/*
 * Copyright 2016 - 2022
 * Andr\xe9 Malo or his licensors, as applicable
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "cext.h"

#include "util.h"


/*
 * Find a particular pyobject attribute
 *
 * Return -1 on error
 * Return 0 if no error occured. attribute will be NULL if it was simply not
 * found. If it was found, a new reference will be returned.
 */
EXT_LOCAL int
tdi_attr(PyObject *obj, const char *name, PyObject **attr)
{
    PyObject *result;

    if ((result = PyObject_GetAttrString(obj, name))) {
        *attr = result;
        return 0;
    }
    else if (!PyErr_Occurred()) {
        *attr = NULL;
        return 0;
    }
    else if (PyErr_ExceptionMatches(PyExc_AttributeError)) {
        PyErr_Clear();
        *attr = NULL;
        return 0;
    }

    return -1;
}
