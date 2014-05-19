
// looks like the only real way to use subclassed GObject objects in python
// is to create a python type for it in an extension module
// we will do this for the gnc-plugin-page type


#include <glib.h>

#include <glib/gi18n.h>

#include <glib-object.h>


#include <Python.h>


#include <pygobject.h>


#include <stdio.h>

#include "config.h"


static PyObject *wrap_loadplugin(PyObject *self, PyObject *args)
{
    PyObject *pPlugObj;
    PyObject *pModPath;
    PyObject *pIFace;
    void *retval;

    if (!PyArg_ParseTuple(args, "OOO:loadplugin", &pPlugObj, &pModPath, &pIFace))
        return NULL;

    if (!PyObject_HasAttrString(pPlugObj,"plugin_class_init"))
        return NULL;

    if (!PyObject_HasAttrString(pPlugObj,"plugin_init"))
        return NULL;

    if (!PyObject_HasAttrString(pPlugObj,"plugin_finalize"))
        return NULL;

    if (!PyObject_HasAttrString(pPlugObj,"plugin_action_callback"))
        return NULL;

    pPluginObject = pPlugObj;
    // is this needed
    Py_INCREF(pPluginObject);

    char *modpath = PyString_AsString(pModPath);
    int iface = PyInt_AsLong(pIFace);

    retval = gnc_module_load(modpath,iface);

    if (PyErr_Occurred())
        {
        fprintf(stderr,"Python Error in loadplugin\n");
        PyErr_Print();
        }

    fprintf(stderr,"return from module load %llx\n",retval);

    Py_INCREF(Py_None);
    return Py_None;
}

// how to add this as a class method??
//    { "recreate_page", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},

static PyMethodDef methods[] =
{
    { "get_type", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "create_widget", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "destroy_widget", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "show_summarybar", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "save_page", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "merge_actions", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "unmerge_actions", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "get_plugin_name", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "add_book", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "has_book", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "has_books", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},

    { "get_window", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "get_ui_merge", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "get_action_group", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "create_action_group", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "get_action", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    {"finish_pending", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},

    // these do not appear as a property
    { "get_page_long_name", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "set_page_long_name", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},

    // these are properties - do I need them
    // it appears those that are properties can be get/set without calling
    // these functions - there is only one storage entity if called via these
    // functions or via get_property/set_property
    { "get_page_name", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "set_page_name", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "get_page_color", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "set_page_color", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "get_uri", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "set_uri", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "get_statusbar_text", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "set_statusbar_text", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "get_use_new_window", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "set_use_new_window", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "get_ui_description", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { "set_ui_description", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},

// signals - do I need these or not
// I think not - we have access to them
//void gnc_plugin_page_inserted (GncPluginPage *plugin_page);
//void gnc_plugin_page_removed (GncPluginPage *plugin_page);
//void gnc_plugin_page_selected (GncPluginPage *plugin_page);
//void gnc_plugin_page_unselected (GncPluginPage *plugin_page);

    { NULL, NULL, 0, NULL }

};



PyMODINIT_FUNC
initpluginpage(void)
{
    PyObject *modul;

    modul = Py_InitModule("initpluginpage", methods);
    if (modul == NULL)
        return;

}

// not sure I need this - this can use pygobject_new to construct
// new python object auto

PyTypeObject G_GNUC_INTERNAL PyGncPluginPageType = {
    PyObject_HEAD_INIT(NULL)
    0,                                 /* ob_size */
    "gnc.PluginPage",                   /* tp_name */
    sizeof(PyGObject),          /* tp_basicsize */
    0,                                 /* tp_itemsize */
    /* methods */
    (destructor)0,        /* tp_dealloc */
    (printfunc)0,                      /* tp_print */
    (getattrfunc)0,       /* tp_getattr */
    (setattrfunc)0,       /* tp_setattr */
    (cmpfunc)0,           /* tp_compare */
    (reprfunc)0,             /* tp_repr */
    (PyNumberMethods*)0,     /* tp_as_number */
    (PySequenceMethods*)0, /* tp_as_sequence */
    (PyMappingMethods*)0,   /* tp_as_mapping */
    (hashfunc)0,             /* tp_hash */
    (ternaryfunc)0,          /* tp_call */
    (reprfunc)0,              /* tp_str */
    (getattrofunc)0,     /* tp_getattro */
    (setattrofunc)0,     /* tp_setattro */
    (PyBufferProcs*)0,  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,                      /* tp_flags */
    NULL,                        /* Documentation string */
    (traverseproc)0,     /* tp_traverse */
    (inquiry)0,             /* tp_clear */
    (richcmpfunc)0,   /* tp_richcompare */
    //offsetof(PyGObject, weakreflist),             /* tp_weaklistoffset */
    (weakreflist)0,             /* tp_weaklistoffset */
    (getiterfunc)0,          /* tp_iter */
    (iternextfunc)0,     /* tp_iternext */
    //(struct PyMethodDef*)_PyGtkWidget_methods, /* tp_methods */
    (struct PyMethodDef*)0,
    (struct PyMemberDef*)0,              /* tp_members */
    //(struct PyGetSetDef*)gtk_widget_getsets,  /* tp_getset */
    (struct PyGetSetDef*)0,
    NULL,                              /* tp_base */
    NULL,                              /* tp_dict */
    (descrgetfunc)0,    /* tp_descr_get */
    (descrsetfunc)0,    /* tp_descr_set */
    //offsetof(PyGObject, inst_dict),                 /* tp_dictoffset */
    (inst_dict)0,
    (initproc)0,             /* tp_init */
    (allocfunc)0,           /* tp_alloc */
    (newfunc)0,               /* tp_new */
    (freefunc)0,             /* tp_free */
    (inquiry)0              /* tp_is_gc */
};

