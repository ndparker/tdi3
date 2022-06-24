/*
 * Copyright 2013 - 2022
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

#include "markup/attr.h"

#define ATTR_CHUNK_SIZE (5)

typedef struct tdi_attrlist_chunk_t {
    struct tdi_attrlist_chunk_t *next;
    tdi_attr_t attr[ATTR_CHUNK_SIZE];
    int index;
} tdi_attrlist_chunk_t;

struct tdi_attrlist_t {
    tdi_attrlist_chunk_t first;
    tdi_attrlist_chunk_t *last;
};


/*
 * Clear attrlist
 *
 * attrs will be set to NULL
 */
void
tdi_attrlist_clear(tdi_attrlist_t **attrs_)
{
    tdi_attrlist_t *attrs = *attrs_;
    tdi_attrlist_chunk_t *current, *next;
    tdi_attr_t *attr;
    int j;

    if (!attrs)
        return;

    *attrs_ = NULL;
    current = attrs->last = &attrs->first;
    while (current) {
        next = current->next;
        current->next = NULL;
        for (j=current->index; j >= 0; --j) {
            attr = &current->attr[j];
            Py_CLEAR(attr->key.obj);
            Py_CLEAR(attr->value.obj);
        }
        if (current != &attrs->first)
            PyMem_Free(current);
        current = next;
    }
}


/*
 * Add attr to attrlist, create if needed
 *
 * key and value are stolen, regardless of success.
 *
 * Return -1 on error, 0 on success
 */
int
tdi_attrlist_add(tdi_attrlist_t **root_, PyObject *key, PyObject *value)
{
    tdi_attrlist_t *root = *root_;
    tdi_attrlist_chunk_t *current, *next;
    tdi_attr_t *attr;
    int index;

    if (!root) {
        if (!(root = PyMem_Malloc(sizeof *root))) {
            LCOV_EXCL_START

            PyErr_SetNone(PyExc_MemoryError);
            goto error_kv;

            LCOV_EXCL_STOP
        }
        root->last = current = &root->first;
        current->next = NULL;
        current->index = -1;

        *root_ = root;
    }
    else {
        current = root->last;
    }

    index = current->index + 1;
    if (index >= ATTR_CHUNK_SIZE) {
        if (!(next = PyMem_Malloc(sizeof *next))) {
            LCOV_EXCL_START

            PyErr_SetNone(PyExc_MemoryError);
            goto error_kv;

            LCOV_EXCL_STOP
        }
        next->next = NULL;
        next->index = index = 0;

        current->next = next;
        current = root->last = next;
    }
    else {
        current->index = index;
    }

    attr = &current->attr[index];
    attr->key.obj = NULL;
    attr->value.obj = NULL;

#ifdef EXT2
    if (!PyBytes_Check(key)) {
        PyErr_SetString(PyExc_TypeError, "expected bytes");
        goto error_kv;
    }
#endif
    if (-1 == PyBytes_AsStringAndSize(key, &attr->key.bytes,
                                      &attr->key.length))
        goto error_kv;

    if (value == Py_None) {
        Py_DECREF(value);
        attr->value.bytes = NULL;
    }
#ifdef EXT2
    else if (!PyBytes_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "expected bytes");
        goto error_kv;
    }
#endif
    else if (-1 == PyBytes_AsStringAndSize(value, &attr->value.bytes,
                                           &attr->value.length))
        goto error_kv;

    attr->key.obj = key;
    attr->value.obj = value;
    return 0;

error_kv:
    Py_DECREF(value);
    Py_DECREF(key);

    return -1;
}


/*
 * Create attrlist from iter([(key, value), ...])
 *
 * Return -1 on error, 0 on sucess
 * result_ contains the result. may be NULL.
 */
int
tdi_attrlist_from_iterable(PyObject *attr_, tdi_attrlist_t **result_)
{
    PyObject *iter, *item, *itemiter, *first, *second, *tmp;
    tdi_attrlist_t *result = NULL;

    if (!(iter = PyObject_GetIter(attr_)))
        return -1;

    while ((item = PyIter_Next(iter))) {
        if (!(itemiter = PyObject_GetIter(item)))
            goto error_item;
        if (!(first = PyIter_Next(itemiter))) {
            if (!PyErr_Occurred())
                PyErr_SetString(PyExc_ValueError,
                                "Expected iterator of length 2");
            goto error_itemiter;
        }
        if (!(second = PyIter_Next(itemiter))) {
            if (!PyErr_Occurred())
                PyErr_SetString(PyExc_ValueError,
                                "Expected iterator of length 2");
            goto error_first;
        }
        if (!(tmp = PyIter_Next(itemiter))) {
            if (PyErr_Occurred())
                goto error_second;
        }
        else {
            Py_DECREF(tmp);
            PyErr_SetString(PyExc_ValueError,
                            "Expected iterator of length 2");
            goto error_second;
        }
        Py_DECREF(itemiter);
        Py_DECREF(item);
        if (-1 == tdi_attrlist_add(&result, first, second))
            goto error_iter;
    }
    if (PyErr_Occurred())
        goto error_iter;
    Py_DECREF(iter);

    *result_ = result;
    return 0;

error_second:
    Py_DECREF(second);
error_first:
    Py_DECREF(first);
error_itemiter:
    Py_DECREF(itemiter);
error_item:
    Py_DECREF(item);
error_iter:
    Py_DECREF(iter);

    tdi_attrlist_clear(&result);

    return -1;
}


/*
 * Init attribute iterator from attrlist
 *
 * Return -1 on error, 0 on success
 */
int
tdi_attrlist_iter_init(tdi_attrlist_iter_t *iter, tdi_attrlist_t *attrs)
{
    iter->current = &attrs->first;
    iter->index = -1;

    return 0;
}


/*
 * Get next attr from attrlist iterator
 *
 * Return -1 on error, 0 on success, attr is set NULL if exhausted.
 */
int
tdi_attrlist_iter_next(tdi_attrlist_iter_t *iter, tdi_attr_t **attr_)
{
    tdi_attr_t *attr = NULL;
    tdi_attrlist_chunk_t *current;
    int index;

    while ((current = iter->current)) {
        index = iter->index + 1;
        if (index > current->index) {
            iter->current = current->next;
            iter->index = -1;
        }
        else {
            attr = &current->attr[index];
            iter->index = index;
            break;
        }
    }

    *attr_ = attr;
    return 0;
}



