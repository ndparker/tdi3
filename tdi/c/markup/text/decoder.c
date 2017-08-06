/*
 * Copyright 2013 - 2017
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

#include "markup/text/decoder.h"

/*
 * Object structure for TextDecoder
 */
typedef struct {
    PyObject_HEAD
    PyObject *weakreflist;

    PyObject *encoding;
} tdi_text_decoder_t;


static PyObject *
decode(PyObject *value, PyObject *encoding, PyObject *errors)
{
    const char *encoding_s, *errors_s = "strict";

#ifdef EXT2
    if (!(encoding_s = PyString_AsString(encoding)))
        LCOV_EXCL_LINE_RETURN(NULL);
    if (errors) {
        if (!(errors_s = PyString_AsString(errors)))
            return NULL;
    }
#else
    if (!(encoding_s = PyUnicode_AsUTF8(encoding)))
        LCOV_EXCL_LINE_RETURN(NULL);
    if (errors) {
        if (!(errors_s = PyUnicode_AsUTF8(errors)))
            return NULL;
    }
#endif

    return PyUnicode_FromEncodedObject(value, encoding_s, errors_s);
}


static PyObject *
attribute(PyObject *value, PyObject *encoding, PyObject *errors)
{
    PyObject *result;
    unsigned char *source, *target;
    Py_ssize_t js, jt, length, slength;
    enum PyUnicode_Kind kind;
    EXT_UNI_CP c;
    EXT_UNI_MAX_DECL(m)

    if (!(value = decode(value, encoding, errors)))
        return NULL;

    length = PyUnicode_GET_LENGTH(value);
    if (length == 0)
        return value;

    kind = PyUnicode_KIND(value);
    source = PyUnicode_DATA(value);

    /* 0: Strip quotes */
    c = PyUnicode_READ(kind, source, 0);
    if (c == U('"') || c == U('\'')) {
        if (length <= 2) {
            Py_DECREF(value);
            return PyUnicode_DecodeASCII("", 0, "strict");
        }
        source += kind;
        length -= 2;
    }

    /* 1: Inspect */
    EXT_UNI_MAX_SET(m, 0)
    for (js=0, slength=length; js < slength; ) {
        c = PyUnicode_READ(kind, source, js); ++js;
        if (c == U('\\') && js < slength) {
            c = PyUnicode_READ(kind, source, js); ++js;
            --length;
        }
        EXT_UNI_MAX_LEVEL(m, c);
    }

    /* 2: Allocate */
    if (!(result = PyUnicode_New(length, m))) {
        LCOV_EXCL_START

        Py_DECREF(value);
        return NULL;

        LCOV_EXCL_STOP
    }

    /* 3: Write */
    target = PyUnicode_DATA(result);
    for (js=0, jt=0; js < slength; ) {
        c = PyUnicode_READ(kind, source, js); ++js;
        if (c == U('\\') && js < slength) {
            c = PyUnicode_READ(kind, source, js); ++js;
        }
        PyUnicode_WRITE(kind, target, jt, c); ++jt;
    }
    Py_DECREF(value);

    return result;
}

/* ------------------ BEGIN TDI_TextDecoder DEFINITION ----------------- */

PyDoc_STRVAR(TDI_TextDecoder_normalize__doc__,
"normalize(self, name)\n\
\n\
:See: `abstract.Decoder`");

static PyObject *
TDI_TextDecoder_normalize(tdi_text_decoder_t *self, PyObject *args,
                          PyObject *kwds)
{
    PyObject *name;
    static char *kwlist[] = {"name", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist,
                                     &name))
        return NULL;

    return Py_INCREF(name), name;
}


PyDoc_STRVAR(TDI_TextDecoder_decode__doc__,
"decode(self, value, errors='strict')\n\
\n\
:See: `abstract.Decoder`");

static PyObject *
TDI_TextDecoder_decode(tdi_text_decoder_t *self, PyObject *args,
                       PyObject *kwds)
{
    PyObject *value, *errors = NULL;
    static char *kwlist[] = {"value", "errors", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O", kwlist,
                                     &value, &errors))
        return NULL;

    return decode(value, self->encoding, errors);
}


PyDoc_STRVAR(TDI_TextDecoder_attribute__doc__,
"attribute(self, value, errors='strict')\n\
\n\
:See: `abstract.Decoder`");

static PyObject *
TDI_TextDecoder_attribute(tdi_text_decoder_t *self, PyObject *args,
                          PyObject *kwds)
{
    PyObject *value, *errors = NULL;
    static char *kwlist[] = {"value", "errors", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O", kwlist,
                                     &value, &errors))
        return NULL;

    return attribute(value, self->encoding, errors);
}


static struct PyMethodDef TDI_TextDecoder_methods[] = {
    {"normalize",
     (PyCFunction)TDI_TextDecoder_normalize,          METH_VARARGS
                                                    | METH_KEYWORDS,
     TDI_TextDecoder_normalize__doc__},

    {"decode",
     (PyCFunction)TDI_TextDecoder_decode,             METH_VARARGS
                                                    | METH_KEYWORDS,
     TDI_TextDecoder_decode__doc__},

    {"attribute",
     (PyCFunction)TDI_TextDecoder_attribute,          METH_VARARGS
                                                    | METH_KEYWORDS,
     TDI_TextDecoder_attribute__doc__},

    {NULL, NULL}  /* Sentinel */
};

static int
TDI_TextDecoder_setencoding(tdi_text_decoder_t *self, PyObject *value,
                            void *closure)
{
    PyObject *encoding = PyObject_Str(value);
    if (!encoding)
        return -1;

    Py_CLEAR(self->encoding);
    self->encoding = encoding;

    return 0;
}

static PyObject *
TDI_TextDecoder_getencoding(tdi_text_decoder_t *self, void *closure)
{
    return Py_INCREF(self->encoding), self->encoding;
}

static PyGetSetDef TDI_TextDecoder_getset[] = {
    {"encoding",
     (getter)TDI_TextDecoder_getencoding,
     (setter)TDI_TextDecoder_setencoding,
     NULL, NULL},

    {NULL}  /* Sentinel */
};

static PyObject *
TDI_TextDecoder_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"encoding", NULL};
    PyObject *encoding;
    tdi_text_decoder_t *self;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &encoding))
        return NULL;

    if (!(encoding = PyObject_Str(encoding)))
        return NULL;

    if (!(self = GENERIC_ALLOC(type))) {
        LCOV_EXCL_START

        Py_DECREF(encoding);
        return NULL;

        LCOV_EXCL_STOP
    }

    self->encoding = encoding;

    return (PyObject *)self;
}

LCOV_EXCL_START
static int
TDI_TextDecoder_traverse(tdi_text_decoder_t *self, visitproc visit,
                         void *arg)
{
    Py_VISIT(self->encoding);

    return 0;
}
LCOV_EXCL_STOP

static int
TDI_TextDecoder_clear(tdi_text_decoder_t *self)
{
    if (self->weakreflist)
        PyObject_ClearWeakRefs((PyObject *)self);

    Py_CLEAR(self->encoding);

    return 0;
}

DEFINE_GENERIC_DEALLOC(TDI_TextDecoder)

PyDoc_STRVAR(TDI_TextDecoder__doc__,
"``TextDecoder(encoding)``\n\
\n\
Decoder for text input");

PyTypeObject TDI_TextDecoder = {
    PyVarObject_HEAD_INIT(NULL, 0)
    EXT_MODULE_PATH ".TextDecoder",                     /* tp_name */
    sizeof(tdi_text_decoder_t),                         /* tp_basicsize */
    0,                                                  /* tp_itemsize */
    (destructor)TDI_TextDecoder_dealloc,                /* tp_dealloc */
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
    0,                                                  /* tp_getattro */
    0,                                                  /* tp_setattro */
    0,                                                  /* tp_as_buffer */
    Py_TPFLAGS_HAVE_WEAKREFS                            /* tp_flags */
    | Py_TPFLAGS_HAVE_CLASS
    | Py_TPFLAGS_BASETYPE
    | Py_TPFLAGS_HAVE_GC,
    TDI_TextDecoder__doc__,                             /* tp_doc */
    (traverseproc)TDI_TextDecoder_traverse,             /* tp_traverse */
    (inquiry)TDI_TextDecoder_clear,                     /* tp_clear */
    0,                                                  /* tp_richcompare */
    offsetof(tdi_text_decoder_t, weakreflist),          /* tp_weaklistoffset */
    0,                                                  /* tp_iter */
    0,                                                  /* tp_iternext */
    TDI_TextDecoder_methods,                            /* tp_methods */
    0,                                                  /* tp_members */
    TDI_TextDecoder_getset,                             /* tp_getset */
    0,                                                  /* tp_base */
    0,                                                  /* tp_dict */
    0,                                                  /* tp_descr_get */
    0,                                                  /* tp_descr_set */
    0,                                                  /* tp_dictoffset */
    0,                                                  /* tp_init */
    0,                                                  /* tp_alloc */
    TDI_TextDecoder_new,                                /* tp_new */
};

/* ------------------- END TDI_TextDecoder DEFINITION ------------------ */
