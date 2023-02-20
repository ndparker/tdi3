/*
 * Copyright 2016 - 2023
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

#ifndef TDI_UTIL_H
#define TDI_UTIL_H

#include "cext.h"


#ifdef EXT2
#   define tdi_intern PyString_InternFromString
#else
#   define tdi_intern PyUnicode_InternFromString
#endif

#define tdi_eq(o1, o2) (PyObject_RichCompareBool(o1, o2, Py_EQ))


/*
 * Find a particular pyobject attribute
 *
 * Return -1 on error
 * Return 0 if no error occured. attribute will be NULL if it was simply not
 * found. If it was found, a new reference will be returned.
 */
EXT_LOCAL int
tdi_attr(PyObject *, const char *, PyObject **);


#endif
