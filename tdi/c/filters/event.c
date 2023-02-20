/*
 * Copyright 2013 - 2023
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

#include "util.h"
#include "filters/event.h"

/*
 * Object structure for BaseEventFilter
 */
typedef struct {
    PyObject_HEAD
    PyObject *weakreflist;

    PyObject *builder;
} tdi_base_event_filter_t;

/* ----------------- BEGIN TDI_BaseEventFilter DEFINITION ---------------- */

static PyObject *
TDI_BaseEventFilter_getattro(tdi_base_event_filter_t *self, PyObject *name)
{
    PyObject *tmp, *attr;
    int res;

    if (!(tmp = PyObject_GenericGetAttr((PyObject *)self, name))) {
        if (!PyErr_ExceptionMatches(PyExc_AttributeError))
            return NULL;
        PyErr_Clear();
    }
    else
        return tmp;

    if (!(attr = tdi_intern("builder")))
        LCOV_EXCL_LINE_RETURN(NULL);
    res = tdi_eq(attr, name);
    Py_DECREF(attr);
    if (res == -1)
        return NULL;
    else if (res) {
        if (!self->builder)
            Py_RETURN_NONE;
        return (Py_INCREF(self->builder), self->builder);
    }

    if (!(attr = tdi_intern("__getattr__")))
        LCOV_EXCL_LINE_RETURN(NULL);
    tmp = PyObject_GenericGetAttr((PyObject *)self, attr);
    Py_DECREF(attr);
    if (tmp) {
        attr = PyObject_CallFunction(tmp, "O", name);
        Py_DECREF(tmp);
        return attr;
    }
    if (!PyErr_ExceptionMatches(PyExc_AttributeError))
        return NULL;
    PyErr_Clear();

    if (self->builder)
        return PyObject_GetAttr(self->builder, name);
    return PyObject_GetAttr(Py_None, name);
}

static int
TDI_BaseEventFilter_setattro(tdi_base_event_filter_t *self, PyObject *name,
                             PyObject *value)
{
    PyObject *attr;
    int res;

    if (!(attr = tdi_intern("builder")))
        LCOV_EXCL_LINE_RETURN(-1);
    res = tdi_eq(attr, name);
    Py_DECREF(attr);
    if (res == -1)
        return -1;
    else if (res) {
        Py_CLEAR(self->builder);
        if (value)
            self->builder = (Py_INCREF(value), value);
        return 0;
    }

    return PyObject_GenericSetAttr((PyObject *)self, name, value);
}

static int
TDI_BaseEventFilter_init(tdi_base_event_filter_t *self, PyObject *args,
                         PyObject *kwds)
{
    static char *kwlist[] = {"builder", NULL};
    PyObject *builder;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &builder))
        return -1;

    self->builder = (Py_INCREF(builder), builder);

    return 0;
}

static PyObject *
TDI_BaseEventFilter_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    return (PyObject *)GENERIC_ALLOC(type);
}

LCOV_EXCL_START
static int
TDI_BaseEventFilter_traverse(tdi_base_event_filter_t *self, visitproc visit,
                             void *arg)
{
    Py_VISIT(self->builder);

    return 0;
}
LCOV_EXCL_STOP

static int
TDI_BaseEventFilter_clear(tdi_base_event_filter_t *self)
{
    if (self->weakreflist)
        PyObject_ClearWeakRefs((PyObject *)self);

    Py_CLEAR(self->builder);

    return 0;
}

DEFINE_GENERIC_DEALLOC(TDI_BaseEventFilter)

PyDoc_STRVAR(TDI_BaseEventFilter__doc__,
"BaseEventFilter(builder)\n\
\n\
Base event filter class, which actually passes everything unfiltered\n\
\n\
Override the event handlers you need.\n\
\n\
:See: `abstract.BuildingListener`\n\
\n\
Attributes:\n\
  builder (abstract.BuildingListener):\n\
    The next level builder");

PyTypeObject TDI_BaseEventFilter = {
    PyVarObject_HEAD_INIT(NULL, 0)
    EXT_MODULE_PATH ".BaseEventFilter",                 /* tp_name */
    sizeof(tdi_base_event_filter_t),                    /* tp_basicsize */
    0,                                                  /* tp_itemsize */
    (destructor)TDI_BaseEventFilter_dealloc,            /* tp_dealloc */
    0,                                                  /* tp_print */
    0,                                                  /* tp_getattr */
    0,                                                  /* tp_setattr */
    0,                                                  /* tp_compare */
    0,                                                  /* tp_repr */
    0,                                                  /* tp_as_number */
    0,                                                  /* tp_as_sequence */
    0,                                                  /* tp_as_mapping */
    0,                                                  /* tp_hash */
    0,                                                  /* tp_call */
    0,                                                  /* tp_str */
    (getattrofunc)TDI_BaseEventFilter_getattro,         /* tp_getattro */
    (setattrofunc)TDI_BaseEventFilter_setattro,         /* tp_setattro */
    0,                                                  /* tp_as_buffer */
    Py_TPFLAGS_HAVE_WEAKREFS                            /* tp_flags */
    | Py_TPFLAGS_HAVE_CLASS
    | Py_TPFLAGS_BASETYPE
    | Py_TPFLAGS_HAVE_GC,
    TDI_BaseEventFilter__doc__,                         /* tp_doc */
    (traverseproc)TDI_BaseEventFilter_traverse,         /* tp_traverse */
    (inquiry)TDI_BaseEventFilter_clear,                 /* tp_clear */
    0,                                                  /* tp_richcompare */
    offsetof(tdi_base_event_filter_t, weakreflist),     /* tp_weaklistoffset */
    0,                                                  /* tp_iter */
    0,                                                  /* tp_iternext */
    0,                                                  /* tp_methods */
    0,                                                  /* tp_members */
    0,                                                  /* tp_getset */
    0,                                                  /* tp_base */
    0,                                                  /* tp_dict */
    0,                                                  /* tp_descr_get */
    0,                                                  /* tp_descr_set */
    0,                                                  /* tp_dictoffset */
    (initproc)TDI_BaseEventFilter_init,                 /* tp_init */
    0,                                                  /* tp_alloc */
    TDI_BaseEventFilter_new,                            /* tp_new */
};

/* ------------------ END TDI_BaseEventFilter DEFINITION ----------------- */
