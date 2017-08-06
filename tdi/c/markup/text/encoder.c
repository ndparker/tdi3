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

#include "length.h"
#include "markup/attr.h"
#include "markup/text/encoder.h"

#define LENGTH_ADD(toadd) do {                      \
    if (-1 == (length = length_add(length, toadd))) \
        return NULL;                                \
} while(0)

/*
 * Object structure for TextEncoder
 */
typedef struct {
    PyObject_HEAD
    PyObject *weakreflist;

    PyObject *encoding;
} tdi_text_encoder_t;


static PyObject *
encode_starttag(tdi_bytestr_t *name, tdi_attrlist_t *attrs, int closed)
{
    PyObject *result;
    tdi_attrlist_iter_t attriter;
    tdi_attr_t *attr;
    char *c;
    Py_ssize_t length;

    length = name->length;
    LENGTH_ADD(closed ? 4 : 2);
    if (-1 == tdi_attrlist_iter_init(&attriter, attrs))
        LCOV_EXCL_LINE_RETURN(NULL);

    for(;;) {
        if (-1 == tdi_attrlist_iter_next(&attriter, &attr))
            LCOV_EXCL_LINE_RETURN(NULL);
        if (!attr)
            break;

        LENGTH_ADD(1);
        LENGTH_ADD(attr->key.length);
        if (attr->value.bytes) {
            LENGTH_ADD(1);
            LENGTH_ADD(attr->value.length);
        }
    }

    if (!(result = PyBytes_FromStringAndSize(NULL, length)))
        LCOV_EXCL_LINE_RETURN(NULL);

    c = PyBytes_AS_STRING(result);

    *c++ = '[';
    if (closed) *c++ = '[';
    (void)memcpy(c, name->bytes, (size_t)name->length);
    c += name->length;

    if (-1 == tdi_attrlist_iter_init(&attriter, attrs))
        LCOV_EXCL_LINE_GOTO(error_result);

    for(;;) {
        if (-1 == tdi_attrlist_iter_next(&attriter, &attr))
            LCOV_EXCL_LINE_GOTO(error_result);
        if (!attr)
            break;

        *c++ = ' ';
        (void)memcpy(c, attr->key.bytes, (size_t)attr->key.length);
        c += attr->key.length;
        if (attr->value.bytes) {
            *c++ = '=';
            (void)memcpy(c, attr->value.bytes, (size_t)attr->value.length);
            c += attr->value.length;
        }
    }

    if (closed) *c++ = ']';
    *c = ']';

    return result;

error_result:
    LCOV_EXCL_START

    Py_DECREF(result);

    return NULL;

    LCOV_EXCL_STOP
}


static PyObject *
encode_endtag(tdi_bytestr_t *name)
{
    PyObject *result;
    char *c;
    Py_ssize_t length;

    length = name->length;
    LENGTH_ADD(3);

    if (!(result = PyBytes_FromStringAndSize(NULL, length)))
        LCOV_EXCL_LINE_RETURN(NULL);
    c = PyBytes_AS_STRING(result);

    *c++ = '[';
    *c++ = '/';
    (void)memcpy(c, name->bytes, (size_t)name->length);
    c += name->length;
    *c = ']';

    return result;
}

/*
 * Encode an object
 */
static PyObject *
do_encode(PyObject *value, PyObject *encoding)
{
    const char *encoding_s, *errors_s = "strict";

#ifdef EXT2
    if (!PyUnicode_Check(value))
        return PyObject_Str(value);

    if (!(encoding_s = PyString_AsString(encoding)))
        LCOV_EXCL_LINE_RETURN(NULL);
    return PyUnicode_AsEncodedString(value, encoding_s, errors_s);

#else
    PyObject *tmp;

    if (PyBytes_Check(value)) {
        Py_INCREF(value);
        return value;
    }

    if (!(encoding_s = PyUnicode_AsUTF8(encoding)))
        LCOV_EXCL_LINE_RETURN(NULL);

    if (!(tmp = PyObject_Str(value)))
        return NULL;
    value = PyUnicode_AsEncodedString(tmp, encoding_s, errors_s);
    Py_DECREF(tmp);
    return value;
#endif
}


/*
 * Encode name
 */
static PyObject *
encode_name(PyObject *name, PyObject *encoding)
{
    return do_encode(name, encoding);
}


/*
 * Encode attribute from unicode
 */
static PyObject *
encode_attribute_unicode(PyObject *value, PyObject *encoding)
{
    PyObject *uresult, *result;
    unsigned char *source, *target;
    Py_ssize_t length, slength, js, jt;
    EXT_UNI_CP c;
    EXT_UNI_KIND_DECL(kind)
    EXT_UNI_KIND_DECL(tkind)
    EXT_UNI_MAX_DECL(m)

    EXT_UNI_KIND_SET(kind, PyUnicode_KIND(value))
    source = PyUnicode_DATA(value);

    length = slength = PyUnicode_GET_LENGTH(value);
    LENGTH_ADD(2);  /* quotes */

    EXT_UNI_MAX_SET(m, 0)
    EXT_UNI_MAX_LEVEL(m, U('"'));
    for (js=0; js < slength; ) {
        c = PyUnicode_READ(kind, source, js); ++js;
        if (c == U('\\') || c == U('"')) {
            EXT_UNI_MAX_LEVEL(m, U('\\'));
            LENGTH_ADD(1);  /* backslash */
        }
        EXT_UNI_MAX_LEVEL(m, c);
    }

    if (!(uresult = PyUnicode_New(length, m)))
        LCOV_EXCL_LINE_RETURN(NULL);
    target = PyUnicode_DATA(uresult);
    EXT_UNI_KIND_SET(tkind, PyUnicode_KIND(uresult))

    jt = 0;
    PyUnicode_WRITE(tkind, target, jt, U('"')); ++jt;

    for (js=0; js < slength; ) {
        c = PyUnicode_READ(kind, source, js); ++js;
        if (c == U('\\') || c == U('"')) {
            PyUnicode_WRITE(tkind, target, jt, U('\\')); ++jt;
        }
        PyUnicode_WRITE(tkind, target, jt, c); ++jt;
    }
    PyUnicode_WRITE(tkind, target, jt, U('"'));

    result = do_encode(uresult, encoding);
    Py_DECREF(uresult);
    return result;
}


/*
 * Encode attribute from bytes
 */
static PyObject *
encode_attribute_bytes(PyObject *value)
{
    PyObject *result;
    char *source, *target, *sentinel;
    Py_ssize_t length, slength;
    char c;

    source = PyBytes_AS_STRING(value);
    length = slength = PyBytes_GET_SIZE(value);
    LENGTH_ADD(2);  /* quotes */

    for (sentinel = source + slength; source < sentinel; ) {
        c = *source++;
        if (c == '\\' || c == '"')
            LENGTH_ADD(1);  /* backslash */
    }

    if (!(result = PyBytes_FromStringAndSize(NULL, length)))
        LCOV_EXCL_LINE_RETURN(NULL);

    source = PyBytes_AS_STRING(value);
    target = PyBytes_AS_STRING(result);
    *target++ = '"';
    for (sentinel = source + slength; source < sentinel; ) {
        c = *source++;
        if (c == '\\' || c == '"')
            *target++ = '\\';
        *target++ = c;
    }
    *target++ = '"';

    return result;
}


/*
 * Encode attribute (bytes or unicode)
 */
static PyObject *
encode_attribute(PyObject *value, PyObject *encoding)
{
    PyObject *tmp;

#ifdef EXT2
    if (PyUnicode_Check(value)) {
        return encode_attribute_unicode(value, encoding);
    }
    else {
        if (!(tmp = PyObject_Str(value)))
            return NULL;
        value = encode_attribute_bytes(tmp);
        Py_DECREF(tmp);
        return value;
    }
#else
    if (!PyBytes_Check(value)) {
        if (!(tmp = PyObject_Str(value)))
            return NULL;
        value = encode_attribute_unicode(tmp, encoding);
        Py_DECREF(tmp);
        return value;
    }
    else {
        return encode_attribute_bytes(value);
    }
#endif
}


/*
 * Encode content (bytes or unicode)
 */
static PyObject *
encode_content(PyObject *value, PyObject *encoding)
{
    return do_encode(value, encoding);
}


/*
 * Encode generic (bytes or unicode)
 */
static PyObject *
encode_encode(PyObject *value, PyObject *encoding)
{
    return do_encode(value, encoding);
}


/*
 * Escape unicode
 */
static PyObject *
encode_escape_unicode(PyObject *value, PyObject *encoding)
{
    PyObject *uresult;
    unsigned char *source, *target;
    Py_ssize_t length, slength, js, jt;
    EXT_UNI_CP c;
    EXT_UNI_KIND_DECL(kind)
    EXT_UNI_KIND_DECL(tkind)
    EXT_UNI_MAX_DECL(m)

    EXT_UNI_KIND_SET(kind, PyUnicode_KIND(value))
    source = PyUnicode_DATA(value);

    length = slength = PyUnicode_GET_LENGTH(value);

    EXT_UNI_MAX_SET(m, 0)
    for (js=0; js < slength; ) {
        c = PyUnicode_READ(kind, source, js); ++js;
        if (c == U('[')) {
            EXT_UNI_MAX_LEVEL(m, U(']'));
            LENGTH_ADD(1);  /* escape */
        }
        EXT_UNI_MAX_LEVEL(m, c);
    }

    if (!(uresult = PyUnicode_New(length, m)))
        LCOV_EXCL_LINE_RETURN(NULL);

    target = PyUnicode_DATA(uresult);
    EXT_UNI_KIND_SET(tkind, PyUnicode_KIND(uresult))

    jt = 0;
    for (js=0; js < slength; ) {
        c = PyUnicode_READ(kind, source, js); ++js;
        PyUnicode_WRITE(tkind, target, jt, c); ++jt;
        if (c == U('[')) {
            PyUnicode_WRITE(tkind, target, jt, U(']')); ++jt;
        }
    }

    return uresult;
}


/*
 * Escape bytes
 */
static PyObject *
encode_escape_bytes(PyObject *value)
{
    PyObject *result;
    char *source, *target, *sentinel;
    Py_ssize_t length, slength;
    char c;

    source = PyBytes_AS_STRING(value);
    length = slength = PyBytes_GET_SIZE(value);

    for (sentinel = source + slength; source < sentinel; ) {
        c = *source++;
        if (c == '[')
            LENGTH_ADD(1);  /* backslash */
    }

    if (!(result = PyBytes_FromStringAndSize(NULL, length)))
        LCOV_EXCL_LINE_RETURN(NULL);

    source = PyBytes_AS_STRING(value);
    target = PyBytes_AS_STRING(result);
    for (sentinel = source + slength; source < sentinel; ) {
        c = *source++;
        *target++ = c;
        if (c == '[')
            *target++ = ']';
    }

    return result;
}


/*
 * escape content (bytes or unicode)
 */
static PyObject *
encode_escape(PyObject *value, PyObject *encoding)
{
    PyObject *tmp;

#ifdef EXT2
    if (PyUnicode_Check(value)) {
        return encode_escape_unicode(value, encoding);
    }
    else {
        if (!(tmp = PyObject_Str(value)))
            return NULL;
        value = encode_escape_bytes(tmp);
        Py_DECREF(tmp);
        return value;
    }
#else
    if (!PyBytes_Check(value)) {
        if (!(tmp = PyObject_Str(value)))
            return NULL;
        value = encode_escape_unicode(tmp, encoding);
        Py_DECREF(tmp);
        return value;
    }
    else {
        return encode_escape_bytes(value);
    }
#endif
}



/* ------------------ BEGIN TDI_TextEncoder DEFINITION ----------------- */

PyDoc_STRVAR(TDI_TextEncoder_starttag__doc__,
"starttag(self, name, attr, closed)\n\
\n\
:See: `abstract.Encoder`");

static PyObject *
TDI_TextEncoder_starttag(tdi_text_encoder_t *self, PyObject *args,
                         PyObject *kwds)
{
    PyObject *name_, *attr_, *closed_, *result;
    static char *kwlist[] = {"name", "attr", "closed", NULL};
    tdi_bytestr_t name = {0};
    tdi_attrlist_t *attrs;
    int closed;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOO", kwlist,
                                     &name_, &attr_, &closed_))
        return NULL;

    if (-1 == (closed = PyObject_IsTrue(closed_)))
        return NULL;

    Py_INCREF(name_);
#ifdef EXT2
    if (!PyBytes_Check(name_)) {
        PyErr_SetString(PyExc_TypeError, "expected bytes");
        goto error_name;
    }
#endif
    if (-1 == PyBytes_AsStringAndSize(name_, &name.bytes, &name.length))
        goto error_name;

    if (-1 == tdi_attrlist_from_iterable(attr_, &attrs))
        goto error_name;

    result = encode_starttag(&name, attrs, closed);

    tdi_attrlist_clear(&attrs);
    Py_DECREF(name_);
    return result;

error_name:
    Py_DECREF(name_);

    return NULL;
}


PyDoc_STRVAR(TDI_TextEncoder_endtag__doc__,
"endtag(self, name)\n\
\n\
:See: `abstract.Encoder`");

static PyObject *
TDI_TextEncoder_endtag(tdi_text_encoder_t *self, PyObject *args,
                         PyObject *kwds)
{
    PyObject *name_, *result;
    static char *kwlist[] = {"name", NULL};
    tdi_bytestr_t name = {0};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist,
                                     &name_))
        return NULL;

    Py_INCREF(name_);
#ifdef EXT2
    if (!PyBytes_Check(name_)) {
        PyErr_SetString(PyExc_TypeError, "expected bytes");
        goto error_name;
    }
#endif
    if (-1 == PyBytes_AsStringAndSize(name_, &name.bytes, &name.length))
        goto error_name;

    result = encode_endtag(&name);

    Py_DECREF(name_);
    return result;

error_name:
    Py_DECREF(name_);

    return NULL;
}


PyDoc_STRVAR(TDI_TextEncoder_name__doc__,
"name(self, name)\n\
\n\
:See: `abstract.Encoder`");

static PyObject *
TDI_TextEncoder_name(tdi_text_encoder_t *self, PyObject *args,
                     PyObject *kwds)
{
    PyObject *name_, *result;
    static char *kwlist[] = {"name", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist,
                                     &name_))
        return NULL;

    Py_INCREF(name_);
    result = encode_name(name_, self->encoding);
    Py_DECREF(name_);
    return result;
}


PyDoc_STRVAR(TDI_TextEncoder_attribute__doc__,
"attribute(self, value)\n\
\n\
:See: `abstract.Encoder`");

static PyObject *
TDI_TextEncoder_attribute(tdi_text_encoder_t *self, PyObject *args,
                          PyObject *kwds)
{
    PyObject *value_, *result;
    static char *kwlist[] = {"value", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist,
                                     &value_))
        return NULL;

    Py_INCREF(value_);
    result = encode_attribute(value_, self->encoding);
    Py_DECREF(value_);
    return result;
}


PyDoc_STRVAR(TDI_TextEncoder_content__doc__,
"content(self, value)\n\
\n\
:See: `abstract.Encoder`");

static PyObject *
TDI_TextEncoder_content(tdi_text_encoder_t *self, PyObject *args,
                        PyObject *kwds)
{
    PyObject *value_, *result;
    static char *kwlist[] = {"value", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist,
                                     &value_))
        return NULL;

    Py_INCREF(value_);
    result = encode_content(value_, self->encoding);
    Py_DECREF(value_);
    return result;
}


PyDoc_STRVAR(TDI_TextEncoder_encode__doc__,
"encode(self, value)\n\
\n\
:See: `abstract.Encoder`");

static PyObject *
TDI_TextEncoder_encode(tdi_text_encoder_t *self, PyObject *args,
                       PyObject *kwds)
{
    PyObject *value_, *result;
    static char *kwlist[] = {"value", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist,
                                     &value_))
        return NULL;

    Py_INCREF(value_);
    result = encode_encode(value_, self->encoding);
    Py_DECREF(value_);
    return result;
}


PyDoc_STRVAR(TDI_TextEncoder_escape__doc__,
"escape(self, value)\n\
\n\
:See: `abstract.Encoder`");

static PyObject *
TDI_TextEncoder_escape(tdi_text_encoder_t *self, PyObject *args,
                       PyObject *kwds)
{
    PyObject *value_, *result;
    static char *kwlist[] = {"value", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist,
                                     &value_))
        return NULL;

    Py_INCREF(value_);
    result = encode_escape(value_, self->encoding);
    Py_DECREF(value_);
    return result;
}


static struct PyMethodDef TDI_TextEncoder_methods[] = {
    {"starttag",
     (PyCFunction)TDI_TextEncoder_starttag,           METH_VARARGS
                                                    | METH_KEYWORDS,
     TDI_TextEncoder_starttag__doc__},

    {"endtag",
     (PyCFunction)TDI_TextEncoder_endtag,             METH_VARARGS
                                                    | METH_KEYWORDS,
     TDI_TextEncoder_endtag__doc__},

    {"name",
     (PyCFunction)TDI_TextEncoder_name,               METH_VARARGS
                                                    | METH_KEYWORDS,
     TDI_TextEncoder_name__doc__},

    {"attribute",
     (PyCFunction)TDI_TextEncoder_attribute,          METH_VARARGS
                                                    | METH_KEYWORDS,
     TDI_TextEncoder_attribute__doc__},

    {"content",
     (PyCFunction)TDI_TextEncoder_content,            METH_VARARGS
                                                    | METH_KEYWORDS,
     TDI_TextEncoder_content__doc__},

    {"encode",
     (PyCFunction)TDI_TextEncoder_encode,             METH_VARARGS
                                                    | METH_KEYWORDS,
     TDI_TextEncoder_encode__doc__},

    {"escape",
     (PyCFunction)TDI_TextEncoder_escape,             METH_VARARGS
                                                    | METH_KEYWORDS,
     TDI_TextEncoder_escape__doc__},

    {NULL, NULL}  /* Sentinel */
};


static int
TDI_TextEncoder_setencoding(tdi_text_encoder_t *self, PyObject *value,
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
TDI_TextEncoder_getencoding(tdi_text_encoder_t *self, void *closure)
{
    return Py_INCREF(self->encoding), self->encoding;
}

static PyGetSetDef TDI_TextEncoder_getset[] = {
    {"encoding",
     (getter)TDI_TextEncoder_getencoding,
     (setter)TDI_TextEncoder_setencoding,
     NULL, NULL},

    {NULL}  /* Sentinel */
};

static PyObject *
TDI_TextEncoder_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"encoding", NULL};
    PyObject *encoding;
    tdi_text_encoder_t *self;

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
TDI_TextEncoder_traverse(tdi_text_encoder_t *self, visitproc visit,
                         void *arg)
{
    Py_VISIT(self->encoding);

    return 0;
}
LCOV_EXCL_STOP

static int
TDI_TextEncoder_clear(tdi_text_encoder_t *self)
{
    if (self->weakreflist)
        PyObject_ClearWeakRefs((PyObject *)self);

    Py_CLEAR(self->encoding);

    return 0;
}

DEFINE_GENERIC_DEALLOC(TDI_TextEncoder)

PyDoc_STRVAR(TDI_TextEncoder__doc__,
"``TextEncoder(encoding)``\n\
\n\
Encoder for text input");

PyTypeObject TDI_TextEncoder = {
    PyVarObject_HEAD_INIT(NULL, 0)
    EXT_MODULE_PATH ".TextEncoder",                     /* tp_name */
    sizeof(tdi_text_encoder_t),                         /* tp_basicsize */
    0,                                                  /* tp_itemsize */
    (destructor)TDI_TextEncoder_dealloc,                /* tp_dealloc */
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
    TDI_TextEncoder__doc__,                             /* tp_doc */
    (traverseproc)TDI_TextEncoder_traverse,             /* tp_traverse */
    (inquiry)TDI_TextEncoder_clear,                     /* tp_clear */
    0,                                                  /* tp_richcompare */
    offsetof(tdi_text_encoder_t, weakreflist),          /* tp_weaklistoffset */
    0,                                                  /* tp_iter */
    0,                                                  /* tp_iternext */
    TDI_TextEncoder_methods,                            /* tp_methods */
    0,                                                  /* tp_members */
    TDI_TextEncoder_getset,                             /* tp_getset */
    0,                                                  /* tp_base */
    0,                                                  /* tp_dict */
    0,                                                  /* tp_descr_get */
    0,                                                  /* tp_descr_set */
    0,                                                  /* tp_dictoffset */
    0,                                                  /* tp_init */
    0,                                                  /* tp_alloc */
    TDI_TextEncoder_new,                                /* tp_new */
};

/* ------------------- END TDI_TextEncoder DEFINITION ------------------ */
