/********************************************************************\
 * gnc-helpers-python.c -- gnucash glib helper functions for python *
 *                                                                  *
 * This program is free software; you can redistribute it and/or    *
 * modify it under the terms of the GNU General Public License as   *
 * published by the Free Software Foundation; either version 2 of   *
 * the License, or (at your option) any later version.              *
 *                                                                  *
 * This program is distributed in the hope that it will be useful,  *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of   *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the    *
 * GNU General Public License for more details.                     *
 *                                                                  *
 * You should have received a copy of the GNU General Public License*
 * along with this program; if not, contact:                        *
 *                                                                  *
 * Free Software Foundation           Voice:  +1-617-542-5942       *
 * 51 Franklin Street, Fifth Floor    Fax:    +1-617-542-2652       *
 * Boston, MA  02110-1301,  USA       gnu@gnu.org                   *
 *                                                                  *
\********************************************************************/

#include "config.h"

#include <assert.h>
#include <string.h>
#include <glib.h>
#include <Python.h>
#include "swig-runtime-python.h"
#include "glib-helpers-python.h"


static PyObject
*glist_to_python_list_helper(GList *glist, swig_type_info *wct)
{
    PyObject *list = NULL;
    GList *node;

    list = PyList_New(0);
    for (node = glist; node; node = node->next)
        {
        int retval = PyList_Append(list, SWIG_NewPointerObj(node->data, wct, 0));
        if (retval != 0)
            {
            return NULL;
            }
        }

    return list;
}

PyObject
*gnc_glist_to_python_list(GList *glist, gchar *wct)
{
    swig_type_info *stype = SWIG_TypeQuery(wct);
    g_return_val_if_fail(stype, NULL);
    return glist_to_python_list_helper(glist, stype);
}

GList *
gnc_python_list_to_glist(PyObject *rest)
{
    GList *result = NULL;
    PyObject *python_item;
    int indx;

    SWIG_GetModule(NULL); /* Work-around for SWIG bug. */
    assert(PyList_Check(rest)==0);
    //if (!PyList_Check(rest))
        //assert(, "gnc_python_list_to_glist");

    ssize_t lstlen = PyList_Size(rest);

    for(indx=0;indx<lstlen;indx++)
        {
        void *item = NULL;

        python_item = PyList_GetItem(rest,indx);

        // try and check for wrapped SWIG instance here and a basic CObject
        if (PyObject_HasAttrString(python_item, "instance"))
            {
            item = PyObject_GetAttrString(python_item, "instance");
            if (!SwigPyObject_Check(item))
                {
                PyErr_SetString(PyExc_TypeError,"gnc_python_list_to_glist: Item in list not a SWIG instance.");
                }
            }
        else if (PyCObject_Check(python_item))
            {
            item = PyCObject_AsVoidPtr(python_item);
            }
        else
            {
            PyErr_SetString(PyExc_TypeError,"gnc_python_list_to_glist: Item in list not a CObject or SWIG instance.");
            }

        result = g_list_prepend(result, item);
        }

    return g_list_reverse(result);
}

/********************************************************************
 * gnc_glist_string_to_python
 ********************************************************************/
PyObject
*gnc_glist_string_to_python(GList *glist)
{
    PyObject *list = NULL;
    GList *node;

    list = PyList_New(0);
    for (node = glist; node; node = node->next)
    {
        if (node->data)
            {
            // for guile there was a utf-8 conversion
            // do we need to worry about it?
            PyObject *pystr = PyString_FromString(node->data);
            int retval = PyList_Append(list, pystr);
            if (retval != 0)
                return NULL;
            }
        else
            {
            //retval = PyList_Append(list, PyString_FromString(""));
            int retval = PyList_Append(list, Py_None);
            }
    }

    return list;
}




/********************************************************************
 * gnc_python_to_glist_string
 ********************************************************************/

GList *
gnc_python_to_glist_string(PyObject *list)
{
    GList *glist = NULL;
    PyObject *python_item;
    int indx;

    assert(PyList_Check(list)==0);

    ssize_t lstlen = PyList_Size(list);

    for(indx=0;indx<lstlen;indx++)
        {
        void *item = NULL;

        python_item = PyList_GetItem(list,indx);

        if (PyString_Check(python_item))
        {
            char *str;
            str = PyString_AsString(python_item);
            if (str)
                glist = g_list_prepend (glist, g_strdup (str));
        }
    }

    return g_list_reverse (glist);
}

GSList *
gnc_python_to_gslist_string(PyObject *list)
{
    GSList *gslist = NULL;
    PyObject *python_item;
    int indx;

    assert(PyList_Check(list)==0);

    ssize_t lstlen = PyList_Size(list);

    for(indx=0;indx<lstlen;indx++)
        {
        void *item = NULL;

        python_item = PyList_GetItem(list,indx);

        if (PyString_Check(python_item))
        {
            char *str;
            str = PyString_AsString(python_item);
            if (str)
                gslist = g_slist_prepend (gslist, g_strdup (str));
        }
    }

    return g_slist_reverse (gslist);
}

/********************************************************************
 * gnc_glist_string_p
 ********************************************************************/

int
gnc_glist_string_p(PyObject *list)
{
    return PyList_Check(list);
}
