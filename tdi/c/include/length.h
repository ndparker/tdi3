/*
 * Copyright 2017
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

#ifndef TDI_LENGTH_H
#define TDI_LENGTH_H

#include "cext.h"

#if defined USE_INLINE && defined __GNUC__ && !defined __GNUC_STDC_INLINE__
#define inline __inline__
#endif

/*
 * safe-sum length values. Return -1 in case of error (OverflowError is set)
 */
Py_LOCAL_INLINE(Py_ssize_t)
length_add(Py_ssize_t first, Py_ssize_t second)
{
    assert(first >= 0);
    assert(second >= 0);

    if (first > PY_SSIZE_T_MAX - second) {
        LCOV_EXCL_START

        PyErr_SetNone(PyExc_OverflowError);
        return -1;

        LCOV_EXCL_STOP
    }
    return first + second;
}


#endif
