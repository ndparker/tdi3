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

#ifndef TDI_MARKUP_ATTR_H
#define TDI_MARKUP_ATTR_H

#include "cext.h"

#include "bytestr.h"


typedef struct tdi_attr_t {
    tdi_bytestr_t key;
    tdi_bytestr_t value;
} tdi_attr_t;

typedef struct tdi_attrlist_t tdi_attrlist_t;
typedef struct tdi_attrlist_iter_t tdi_attrlist_iter_t;

struct tdi_attrlist_iter_t {
    void *current;
    int index;
};


/*
 * Clear attrlist
 *
 * attrs will be set to NULL
 */
EXT_LOCAL void
tdi_attrlist_clear(tdi_attrlist_t **);


/*
 * Add attr to attrlist, create if needed
 *
 * key and value are stolen, regardless of success.
 *
 * Return -1 on error, 0 on success
 */
EXT_LOCAL int
tdi_attrlist_add(tdi_attrlist_t **, PyObject *, PyObject *);


/*
 * Create attrlist from iter([(key, value), ...])
 *
 * Return -1 on error, 0 on sucess
 * result_ contains the result. may be NULL.
 */
EXT_LOCAL int
tdi_attrlist_from_iterable(PyObject *, tdi_attrlist_t **);


/*
 * Init attribute iterator from attrlist
 *
 * Allocate tdi_attrlist_iter_t yourself and pass it in.
 *
 * Return -1 on error, 0 on success
 */
EXT_LOCAL int
tdi_attrlist_iter_init(tdi_attrlist_iter_t *, tdi_attrlist_t *);


/*
 * Get next attr from attrlist iterator
 *
 * Return -1 on error, 0 on success, attr is set NULL if exhausted (returning 0)
 */
EXT_LOCAL int
tdi_attrlist_iter_next(tdi_attrlist_iter_t *, tdi_attr_t **);


#endif
