/* -*- Mode: C; c-basic-offset: 4 -*-
 * pyglib - Python bindings for GLIB.
 * Copyright (C) 2007  Gian Mario Tagliaretti
 *
 *   pygkeyfile.c: GKeyFile wrapper.
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
 * USA
 */

#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include <Python.h>
#include <structmember.h>

#include <glib.h>

#include "pyglib.h"

//#include "pyglib-private.h"

#include "pygkeyfile.h"

static int
pyg_key_file_init(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    self->key_file = g_key_file_new ();
    return 0;
}

static void
pyg_key_file_dealloc(PyGKeyFile *self)
{
    if (self->key_file != NULL) {
	g_key_file_free(self->key_file);
	self->key_file = NULL;
    }

    PyObject_Del(self);
}

static int
pyg_key_file_compare(PyGKeyFile *self, PyGKeyFile *v)
{
    if (self->key_file == v->key_file) return 0;
    if (self->key_file > v->key_file) return -1;
    return 1;
}

static PyObject *
pyg_key_file_set_list_separator(PyGKeyFile *self,PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "separator", NULL };
    char        separator;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,
                                     "s:glib.KeyFile.set_list_separator",
                                     kwlist, &separator))
        return NULL;

    g_key_file_set_list_separator(self->key_file, separator);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_load_from_file(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "file", "flags", NULL };
    gchar           *file;
    GKeyFileFlags   flags;
    GError          *error = NULL;
    gboolean        ret;
    PyObject        *py_ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "si:glib.KeyFile.load_from_file",
                                     kwlist, &file, &flags))
        return NULL;

    ret = g_key_file_load_from_file(self->key_file, file, flags, &error);

    if (pyglib_error_check(&error))
        return NULL;

    py_ret = ret ? Py_True : Py_False;
    
    Py_INCREF(py_ret);
    return py_ret;
}

static PyObject *
pyg_key_file_load_from_data(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "data", "length", "flags", NULL };
    gchar           *data;
    gsize           length;
    GKeyFileFlags   flags;
    GError          *error = NULL;
    gboolean        ret;
    PyObject        *py_ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "sii:glib.KeyFile.load_from_data",
                                     kwlist, &data, &length, &flags))
        return NULL;

    ret = g_key_file_load_from_data(self->key_file, data, length, flags, &error);

    if (pyglib_error_check(&error))
        return NULL;

    py_ret = ret ? Py_True : Py_False;

    Py_INCREF(py_ret);
    return py_ret;
}

static PyObject *
pyg_key_file_load_from_data_dirs(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "file", "flags", NULL };
    gchar           *file;
    gchar           *full_path = NULL;
    GKeyFileFlags   flags;
    GError          *error = NULL;
    gboolean        ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "si:glib.KeyFile.load_from_data_dirs",
                                     kwlist, &file, &flags))
        return NULL;

    ret = g_key_file_load_from_data_dirs(self->key_file, file,
                                         &full_path, flags, &error);

    if (pyglib_error_check(&error))
        return NULL;
    
    if (ret)
        return PyString_FromString(full_path);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_to_data(PyGKeyFile *self)
{
    gsize           length;
    GError          *error = NULL;
    gchar           *ret;

    ret = g_key_file_to_data(self->key_file, &length, &error);

    if (pyglib_error_check(&error))
        return NULL;

    if (ret)
        return PyString_FromString(ret);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_get_start_group(PyGKeyFile *self)
{
    gchar           *ret;

    ret = g_key_file_get_start_group(self->key_file);

    if (ret)
        return PyString_FromString(ret);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_get_groups(PyGKeyFile *self)
{
    gchar       **ret, **tmp;
    gsize       *length = NULL;
    PyObject    *py_ret;
    int         i = 0, j;

    ret = g_key_file_get_groups(self->key_file, length);

    if (ret) {
        tmp = ret;
        while (*tmp)
            tmp++, i++;

        py_ret = PyTuple_New(i);
        for (j = 0; j < i; j++)
            PyTuple_SetItem(py_ret, j, PyString_FromString(ret[j]));
        return py_ret;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_get_keys(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "group", NULL };
    gchar       **ret, **tmp;
    gchar       *group;
    gsize       *length = NULL;
    PyObject    *py_ret;
    int         i = 0, j;
    GError      *error = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s:glib.KeyFile.get_keys",
                                     kwlist, &group))
        return NULL;

    ret = g_key_file_get_keys(self->key_file, group, length, &error);
    
    if (pyglib_error_check(&error))
        return NULL;

    if (ret) {
        tmp = ret;
        while (*tmp)
            tmp++, i++;

        py_ret = PyTuple_New(i);
        for (j = 0; j < i; j++)
            PyTuple_SetItem(py_ret, j, PyString_FromString(ret[j]));
        return py_ret;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_has_group(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "group", NULL };
    gchar       *group;
    gboolean    ret;
    PyObject    *py_ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s:glib.KeyFile.has_group",
                                     kwlist, &group))
        return NULL;

    ret = g_key_file_has_group(self->key_file, group);

    py_ret = ret ? Py_True : Py_False;

    Py_INCREF(py_ret);
    return py_ret;
}

static PyObject *
pyg_key_file_has_key(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "group", "key", NULL };
    gchar       *group;
    gchar       *key;
    GError      *error = NULL;
    gboolean    ret;
    PyObject    *py_ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ss:glib.KeyFile.has_key",
                                     kwlist, &group, &key))
        return NULL;

    ret = g_key_file_has_key(self->key_file, group, key, &error);

    if (pyglib_error_check(&error))
        return NULL;

    py_ret = ret ? Py_True : Py_False;

    Py_INCREF(py_ret);
    return py_ret;
}

static PyObject *
pyg_key_file_get_value(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "group", "key", NULL };
    gchar           *group;
    gchar           *key;
    GError          *error = NULL;
    gchar           *ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ss:glib.KeyFile.get_value",
                                     kwlist, &group, &key))
        return NULL;

    ret = g_key_file_get_value(self->key_file, group, key, &error);

    if (pyglib_error_check(&error))
        return NULL;

    if (ret)
        return PyString_FromString(ret);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_get_string(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "group", "key", NULL };
    gchar           *group;
    gchar           *key;
    GError          *error = NULL;
    gchar           *ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ss:glib.KeyFile.get_string",
                                     kwlist, &group, &key))
        return NULL;

    ret = g_key_file_get_string(self->key_file, group, key, &error);

    if (pyglib_error_check(&error))
        return NULL;

    if (ret)
        return PyString_FromString(ret);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_get_locale_string(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "group", "key", "locale", NULL };
    gchar           *group;
    gchar           *key;
    gchar           *locale;
    GError          *error = NULL;
    gchar           *ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "sss:glib.KeyFile.get_locale_string",
                                     kwlist, &group, &key, &locale))
        return NULL;

    ret = g_key_file_get_locale_string(self->key_file, group, key, locale, &error);

    if (pyglib_error_check(&error))
        return NULL;
    
    if (ret)
        return PyString_FromString(ret);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_get_boolean(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "group", "key", NULL };
    gchar           *group;
    gchar           *key;
    GError          *error = NULL;
    gboolean        ret;
    PyObject        *py_ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ss:glib.KeyFile.get_boolean",
                                     kwlist, &group, &key))
        return NULL;

    ret = g_key_file_get_boolean(self->key_file, group, key, &error);

    if (pyglib_error_check(&error))
        return NULL;

    py_ret = ret ? Py_True : Py_False;

    Py_INCREF(py_ret);
    return py_ret;
}

static PyObject *
pyg_key_file_get_integer(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "group", "key", NULL };
    gchar           *group = NULL, *key;
    PyObject        *py_group = Py_None;
    GError          *error = NULL;
    gint            ret;
    PyObject        *py_ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Os:glib.KeyFile.get_integer",
                                     kwlist, &py_group, &key))
        return NULL;
    
    if (py_group != Py_None)
        group = PyString_AsString(py_group);
    
    ret = g_key_file_get_integer(self->key_file, group, key, &error);

    if (pyglib_error_check(&error))
        return NULL;

    py_ret = PyLong_FromLong(ret);

    return py_ret;
}

static PyObject *
pyg_key_file_get_double(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "group", "key", NULL };
    gchar           *group = NULL, *key;
    PyObject        *py_group = Py_None;
    GError          *error = NULL;
    gdouble         ret;
    PyObject        *py_ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Os:glib.KeyFile.get_double",
                                     kwlist, &py_group, &key))
        return NULL;

    if (py_group != Py_None)
        group = PyString_AsString(py_group);

    ret = g_key_file_get_double(self->key_file, group, key, &error);

    if (pyglib_error_check(&error))
        return NULL;

    py_ret = PyFloat_FromDouble(ret);

    return py_ret;
}

static PyObject *
pyg_key_file_get_string_list(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "group", "key", NULL };
    gchar           *group;
    gchar           *key;
    GError          *error = NULL;
    gchar           **ret, **tmp;
    PyObject        *py_ret;
    int             i = 0, j;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ss:glib.KeyFile.get_string_list",
                                     kwlist, &group, &key))
        return NULL;

    ret = g_key_file_get_string_list(self->key_file, group, key, NULL, &error);

    if (pyglib_error_check(&error))
        return NULL;

    if (ret) {
        tmp = ret;
        while (*tmp)
            tmp++, i++;

        py_ret = PyTuple_New(i);
        for (j = 0; j < i; j++)
            PyTuple_SetItem(py_ret, j, PyString_FromString(ret[j]));
        
        return py_ret;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_get_locale_string_list(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "group", "key", "locale", NULL };
    gchar           *group;
    gchar           *key;
    gchar           *locale;
    PyObject        *py_locale;
    GError          *error = NULL;
    gchar           **ret, **tmp;
    PyObject        *py_ret;
    int             i = 0, j;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ssO:glib.KeyFile.get_locale_string_list",
                                     kwlist, &group, &key, &py_locale))
        return NULL;

    if (py_locale == Py_None)
        locale = NULL;
        
    if PyString_Check(py_locale)
        locale = PyString_AsString(py_locale);
    
    ret = g_key_file_get_locale_string_list(self->key_file, group, key, locale, NULL, &error);

    if (pyglib_error_check(&error))
        return NULL;
    
    if (ret) {
        tmp = ret;
        while (*tmp)
            tmp++, i++;

        py_ret = PyTuple_New(i);
        for (j = 0; j < i; j++)
            PyTuple_SetItem(py_ret, j, PyString_FromString(ret[j]));
        
        return py_ret;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_get_boolean_list(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "group", "key", NULL };
    gchar           *group;
    gchar           *key;
    gsize           length;
    GError          *error = NULL;
    gboolean        *ret;
    PyObject        *py_ret;
    int             j;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ss:glib.KeyFile.get_boolean_list",
                                     kwlist, &group, &key))
        return NULL;

    ret = g_key_file_get_boolean_list(self->key_file, group, key, &length, &error);

    if (pyglib_error_check(&error))
        return NULL;
    
    if (ret) {
        py_ret = PyTuple_New(length);
        for (j = 0; j < length; j++)
            PyTuple_SetItem(py_ret, j, ret[j] ? Py_True : Py_False);
    return py_ret;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_get_integer_list(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "group", "key", NULL };
    gchar           *group;
    gchar           *key;
    gsize           length;
    GError          *error = NULL;
    gint            *ret;
    PyObject        *py_ret = Py_None;
    int             j;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ss:glib.KeyFile.get_integer_list",
                                     kwlist, &group, &key))
        return NULL;

    ret = g_key_file_get_integer_list(self->key_file, group, key, &length, &error);

    if (pyglib_error_check(&error))
        return NULL;

    if (ret) {
        py_ret = PyTuple_New(length);
        for (j = 0; j < length; j++)
            PyTuple_SetItem(py_ret, j, PyLong_FromLong(ret[j]));
    return py_ret;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_get_double_list(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "group", "key", NULL };
    gchar           *group = NULL, *key;
    PyObject        *py_group = Py_None;
    gsize           length;
    GError          *error = NULL;
    gdouble         *ret;
    PyObject        *py_ret;
    int             j;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Os:glib.KeyFile.get_double_list",
                                     kwlist, &py_group, &key))
        return NULL;

    if (py_group != Py_None)
        group = PyString_AsString(py_group);

    ret = g_key_file_get_double_list(self->key_file, group, key, &length, &error);

    if (pyglib_error_check(&error))
        return NULL;

    if (ret) {
        py_ret = PyTuple_New(length);
        for (j = 0; j < length; j++)
            PyTuple_SetItem(py_ret, j, PyLong_FromDouble(ret[j]));
    return py_ret;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_get_comment(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "group", "key", NULL };
    PyObject        *py_group = Py_None, *py_key = Py_None;
    gchar           *group = NULL, *key = NULL;
    GError          *error = NULL;
    gchar           *ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OO:glib.KeyFile.get_comment",
                                     kwlist, &py_group, &py_key))
        return NULL;

    if (py_group != Py_None)
        group = PyString_AsString(py_group);

    if (py_key != Py_None)
        key = PyString_AsString(py_key);

    ret = g_key_file_get_comment(self->key_file, group, key, &error);

    if (pyglib_error_check(&error))
        return NULL;

    if (ret)
        return PyString_FromString(ret);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_set_value(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "group", "key", "value", NULL };
    gchar       *group;
    gchar       *key;
    gchar       *value;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "sss:glib.KeyFile.set_value",
                                     kwlist, &group, &key, &value))
        return NULL;

    g_key_file_set_value(self->key_file, group, key, value);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_set_string(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "group", "key", "string", NULL };
    gchar       *group;
    gchar       *key;
    gchar       *string;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "sss:glib.KeyFile.set_string",
                                     kwlist, &group, &key, &string))
        return NULL;

    g_key_file_set_string(self->key_file, group, key, string);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_set_locale_string(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "group", "key", "locale", "string", NULL };
    gchar       *group;
    gchar       *key;
    gchar       *locale;
    gchar       *string;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ssss:glib.KeyFile.set_locale_string",
                                     kwlist, &group, &key, &locale, &string))
        return NULL;

    g_key_file_set_locale_string(self->key_file, group, key, locale, string);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_set_boolean(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "group", "key", "value", NULL };
    gchar       *group;
    gchar       *key;
    PyObject    *py_val;
    gboolean    value;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ssO:glib.KeyFile.set_boolean",
                                     kwlist, &group, &key, &py_val))
        return NULL;

    if (!PyBool_Check(py_val))
        return NULL;

    value = PyObject_IsTrue(py_val) ? TRUE : FALSE;

    g_key_file_set_boolean(self->key_file, group, key, value);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_set_integer(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "group", "key", "value", NULL };
    gchar       *group;
    gchar       *key;
    gint        value;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ssi:glib.KeyFile.set_integer",
                                     kwlist, &group, &key, &value))
        return NULL;

    g_key_file_set_integer(self->key_file, group, key, value);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_set_double(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "group", "key", "value", NULL };
    gchar       *group = NULL;
    PyObject    *py_group = Py_None;
    gchar       *key;
    gdouble     value;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Osd:glib.KeyFile.set_double",
                                     kwlist, &py_group, &key, &value))
        return NULL;

    if (py_group != Py_None)
        group = PyString_AsString(py_group);
    
    g_key_file_set_double(self->key_file, group, key, value);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_set_string_list(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "group", "key", "string_list", "length", NULL };
    gchar       *group;
    gchar       *key;
    gchar       **list = NULL;
    PyObject    *strings;
    gsize       length;
    int         i, n;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ssOi:glib.KeyFile.set_string_list",
                                     kwlist, &group, &key, &strings, &length))
        return NULL;

    n = PySequence_Size(strings);
    list = g_new(gchar *, n+1);
    for (i = 0; i < n; i++) {
        PyObject *item = PySequence_GetItem(strings, i);
        list[i] = PyString_AsString(item);
    }

    g_key_file_set_string_list(self->key_file, group, key, (const gchar **) list, length);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_set_locale_string_list(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "group", "key", "locale", "strings", "length", NULL };
    gchar       *group;
    gchar       *key;
    gchar       *locale;
    gchar       **list = NULL;
    PyObject    *strings;
    gsize       length;
    int         i, n;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "sssOi:glib.KeyFile.set_locale_string_list",
                                     kwlist, &group, &key, &locale, &strings, &length))
        return NULL;

    n = PySequence_Size(strings);
    list = g_new(gchar *, n+1);
    for (i = 0; i < n; i ++) {
        PyObject *item = PySequence_GetItem(strings, i);
        list[i] = PyString_AsString(item);
    }

    g_key_file_set_locale_string_list(self->key_file, group, key, locale, (const gchar **) list, length);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_set_boolean_list(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "group", "key", "string_list", "length", NULL };
    gchar       *group = NULL;
    gchar       *key = NULL;
    PyObject    *py_key = Py_None, *py_group = Py_None;
    gboolean    *list = NULL;
    PyObject    *bool_list;
    gsize       length;
    int         i, n;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OOOi:glib.KeyFile.set_boolean_list",
                                     kwlist, &py_group, &py_key, &bool_list, &length))
        return NULL;

    if (py_key != Py_None)
        key = PyString_AsString(py_key);

    if (py_group != Py_None)
        group = PyString_AsString(py_group);

    n = PySequence_Size(bool_list);
    list = g_new(gboolean, length);
    for (i = 0; i < n; i ++) {
        PyObject *item = PySequence_GetItem(bool_list, i);
        if (!PyBool_Check(item))
            return NULL;
        list[i] = PyObject_IsTrue(item) ? TRUE : FALSE;
    }

    g_key_file_set_boolean_list(self->key_file, group, key, list, length);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_set_integer_list(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "group", "key", "integers", "length", NULL };
    gchar       *group;
    gchar       *key;
    int         *list = NULL;
    PyObject    *int_list;
    gsize       length;
    int         i, n;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ssOi:glib.KeyFile.set_integer_list",
                                     kwlist, &group, &key, &int_list, &length))
        return NULL;

    n = PySequence_Size(int_list);
    list = g_new(int, length);
    for (i = 0; i < n; i ++) {
        PyObject *item = PySequence_GetItem(int_list, i);
        if (!PyInt_Check(item))
            return NULL;
        list[i] = PyInt_AsLong(item);
    }

    g_key_file_set_integer_list(self->key_file, group, key, list, length);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_set_double_list(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "group", "key", "doubles", "length", NULL };
    gchar       *group = NULL, *key = NULL;
    PyObject    *py_group = Py_None, *py_key = Py_None;
    double      *list = NULL;
    PyObject    *doub_list;
    gsize       length;
    int         i, n;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OOOi:glib.KeyFile.set_double_list",
                                     kwlist, &py_group, &py_key, &doub_list, &length))
        return NULL;
    
    if (py_key != Py_None)
        key = PyString_AsString(py_key);

    if (py_group != Py_None)
        group = PyString_AsString(py_group);
    
    n = PySequence_Size(doub_list);
    list = g_new(double, length);
    for (i = 0; i < n; i ++) {
        PyObject *item = PySequence_GetItem(doub_list, i);
        if (!PyFloat_Check(item))
            return NULL;
        list[i] = PyFloat_AsDouble(item);
    }

    g_key_file_set_double_list(self->key_file, group, key, list, length);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_set_comment(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "group", "key", "comment", NULL };
    gchar           *group = NULL, *key = NULL;
    PyObject        *py_group = Py_None, *py_key = Py_None;
    gchar           *comment;
    GError          *error = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OOs:glib.KeyFile.set_comment",
                                     kwlist, &py_group, &py_key, &comment))
        return NULL;
    
    if (py_key != Py_None)
        key = PyString_AsString(py_key);

    if (py_group != Py_None)
        group = PyString_AsString(py_group);
    
    g_key_file_set_comment(self->key_file, group, key, comment, &error);

    if (pyglib_error_check(&error))
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_remove_group(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "group", NULL };
    gchar           *group;
    GError          *error = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s:glib.KeyFile.remove_group",
                                     kwlist, &group))
        return NULL;

    g_key_file_remove_group(self->key_file, group, &error);

    if (pyglib_error_check(&error))
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_remove_key(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "group", "key", NULL };
    gchar           *group;
    gchar           *key;
    GError          *error = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ss:glib.KeyFile.remove_key",
                                     kwlist, &group, &key))
        return NULL;

    g_key_file_remove_key(self->key_file, group, key, &error);

    if (pyglib_error_check(&error))
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pyg_key_file_remove_comment(PyGKeyFile *self, PyObject *args, PyObject *kwargs)
{
    static char     *kwlist[] = { "group", "key", NULL };
    gchar           *group = NULL, *key = NULL;
    GError          *error = NULL;
    PyObject        *py_group = Py_None, *py_key = Py_None;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OO:glib.KeyFile.remove_comment",
                                     kwlist, &py_group, &py_key))
        return NULL;

    if (py_group != Py_None) {
        if (!PyString_Check(py_group))
            return NULL;
        group = PyString_AsString(py_group);
    }

    if (py_key != Py_None) {
        if (!PyString_Check(py_key))
            return NULL;
        key = PyString_AsString(py_key);
    }

    g_key_file_remove_comment(self->key_file, group, key, &error);

    if (pyglib_error_check(&error))
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef pyg_key_file_methods[] = {
    { "set_list_separator", (PyCFunction)pyg_key_file_set_list_separator, METH_VARARGS | METH_KEYWORDS },
    { "load_from_file", (PyCFunction)pyg_key_file_load_from_file, METH_VARARGS | METH_KEYWORDS },
    { "load_from_data", (PyCFunction)pyg_key_file_load_from_data, METH_VARARGS | METH_KEYWORDS },
    { "load_from_data_dirs", (PyCFunction)pyg_key_file_load_from_data_dirs, METH_VARARGS | METH_KEYWORDS },
    { "to_data", (PyCFunction)pyg_key_file_to_data, METH_NOARGS },
    { "get_start_group", (PyCFunction)pyg_key_file_get_start_group, METH_NOARGS },
    { "get_groups", (PyCFunction)pyg_key_file_get_groups, METH_VARARGS | METH_KEYWORDS },
    { "get_keys", (PyCFunction)pyg_key_file_get_keys, METH_VARARGS | METH_KEYWORDS },
    { "has_group", (PyCFunction)pyg_key_file_has_group, METH_VARARGS | METH_KEYWORDS },
    { "has_key", (PyCFunction)pyg_key_file_has_key, METH_VARARGS | METH_KEYWORDS },
    { "get_value", (PyCFunction)pyg_key_file_get_value, METH_VARARGS | METH_KEYWORDS },
    { "get_string", (PyCFunction)pyg_key_file_get_string, METH_VARARGS | METH_KEYWORDS },
    { "get_locale_string", (PyCFunction)pyg_key_file_get_locale_string, METH_VARARGS | METH_KEYWORDS },
    { "get_boolean", (PyCFunction)pyg_key_file_get_boolean, METH_VARARGS | METH_KEYWORDS },
    { "get_integer", (PyCFunction)pyg_key_file_get_integer, METH_VARARGS | METH_KEYWORDS },
    { "get_double", (PyCFunction)pyg_key_file_get_double, METH_VARARGS | METH_KEYWORDS },
    { "get_string_list", (PyCFunction)pyg_key_file_get_string_list, METH_VARARGS | METH_KEYWORDS },
    { "get_locale_string_list", (PyCFunction)pyg_key_file_get_locale_string_list, METH_VARARGS | METH_KEYWORDS },
    { "get_boolean_list", (PyCFunction)pyg_key_file_get_boolean_list, METH_VARARGS | METH_KEYWORDS },
    { "get_integer_list", (PyCFunction)pyg_key_file_get_integer_list, METH_VARARGS | METH_KEYWORDS },
    { "get_double_list", (PyCFunction)pyg_key_file_get_double_list, METH_VARARGS | METH_KEYWORDS },
    { "get_comment", (PyCFunction)pyg_key_file_get_comment, METH_VARARGS | METH_KEYWORDS },
    { "set_value", (PyCFunction)pyg_key_file_set_value, METH_VARARGS | METH_KEYWORDS },
    { "set_string", (PyCFunction)pyg_key_file_set_string, METH_VARARGS | METH_KEYWORDS },
    { "set_locale_string", (PyCFunction)pyg_key_file_set_locale_string, METH_VARARGS | METH_KEYWORDS },
    { "set_boolean", (PyCFunction)pyg_key_file_set_boolean, METH_VARARGS | METH_KEYWORDS },
    { "set_integer", (PyCFunction)pyg_key_file_set_integer, METH_VARARGS | METH_KEYWORDS },
    { "set_double", (PyCFunction)pyg_key_file_set_double, METH_VARARGS | METH_KEYWORDS },
    { "set_string_list", (PyCFunction)pyg_key_file_set_string_list, METH_VARARGS | METH_KEYWORDS },
    { "set_locale_string_list", (PyCFunction)pyg_key_file_set_locale_string_list, METH_VARARGS | METH_KEYWORDS },
    { "set_boolean_list", (PyCFunction)pyg_key_file_set_boolean_list, METH_VARARGS | METH_KEYWORDS },
    { "set_integer_list", (PyCFunction)pyg_key_file_set_integer_list, METH_VARARGS | METH_KEYWORDS },
    { "set_double_list", (PyCFunction)pyg_key_file_set_double_list, METH_VARARGS | METH_KEYWORDS },
    { "set_comment", (PyCFunction)pyg_key_file_set_comment, METH_VARARGS | METH_KEYWORDS },
    { "remove_group", (PyCFunction)pyg_key_file_remove_group, METH_VARARGS | METH_KEYWORDS },
    { "remove_key", (PyCFunction)pyg_key_file_remove_key, METH_VARARGS | METH_KEYWORDS },
    { "remove_comment", (PyCFunction)pyg_key_file_remove_comment, METH_VARARGS | METH_KEYWORDS },
    { NULL, NULL, 0 },
};

/* define an attribute to access the internal key_file value */
static PyMemberDef pyg_key_file_members[] = {
    { "key_file", T_ULONGLONG, offsetof(PyGKeyFile,key_file), READONLY, "glib GKeyFile pointer"},
    { NULL},
};

PyTypeObject PyGKeyFile_Type = {
    PyObject_HEAD_INIT(NULL)
    0,
    "glib.GKeyFile",
    sizeof(PyGKeyFile),
    0,
    /* methods */
    (destructor)pyg_key_file_dealloc,
    (printfunc)0,
    (getattrfunc)0,
    (setattrfunc)0,
    (cmpfunc)pyg_key_file_compare,
    (reprfunc)0,
    0,
    0,
    0,
    (hashfunc)0,
    (ternaryfunc)0,
    (reprfunc)0,
    (getattrofunc)0,
    (setattrofunc)0,
    0,
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    NULL,
    (traverseproc)0,
    (inquiry)0,
    (richcmpfunc)0,
    0,
    (getiterfunc)0,
    (iternextfunc)0,
    pyg_key_file_methods,
    pyg_key_file_members,
    0,
    NULL,
    NULL,
    (descrgetfunc)0,
    (descrsetfunc)0,
    0,
    (initproc)pyg_key_file_init,
};


PyMethodDef pygkeyfile_functions[];

DL_EXPORT(void)
initpygkeyfile(void)
{
    PyObject *m, *d;
	
    m = Py_InitModule("pygkeyfile", pygkeyfile_functions);
    d = PyModule_GetDict(m);

    // might not need this - not clear whats going on
    // the claim is PyType_Ready will set it to base class ob_type
    //PyGKeyFile_Type.ob_type = &PyType_Type;
    //PyGKeyFile_Type.tp_alloc = &PyType_GenericAlloc;
    PyGKeyFile_Type.tp_new = &PyType_GenericNew;
    if (PyType_Ready(&PyGKeyFile_Type))
        return;

    // curious - should do this or use PyModule_AddObject
    //Py_INCREF(&PyGKeyFile_Type);
    //PyModule_AddObject(m, "GKeyFile", (PyObject *)&PyGKeyFile_Type);
    PyDict_SetItemString(d, "GKeyFile", (PyObject *)&PyGKeyFile_Type);
	
    if (PyErr_Occurred ()) {
	Py_FatalError("can't initialise module pygkeyfile");
    }
}
