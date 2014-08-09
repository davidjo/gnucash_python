/* -*- Mode: C; c-basic-offset: 4 -*- */


#include <Python.h>

/* include this first, before NO_IMPORT_PYGOBJECT is defined */
#include <pygobject.h>

void gnctreeview_register_classes (PyObject *d);

extern PyMethodDef gnctreeview_functions[];

DL_EXPORT(void)
initgnctreeview(void)
{
    PyObject *m, *d;
	
    init_pygobject();

    m = Py_InitModule("gnctreeview",gnctreeview_functions);
    d = PyModule_GetDict(m);
	
    gnctreeview_register_classes(d);

    if (PyErr_Occurred ()) {
	PyErr_Print();
	Py_FatalError("can't initialise module gnctreeview");
    }
}
