/* -*- Mode: C; c-basic-offset: 4 -*- */


#include <Python.h>

/* include this first, before NO_IMPORT_PYGOBJECT is defined */
#include <pygobject.h>

void gnchtmlwebkit_register_classes (PyObject *d);

extern PyMethodDef gnchtmlwebkit_functions[];

DL_EXPORT(void)
initgnchtmlwebkit(void)
{
    PyObject *m, *d;
	
    init_pygobject();

    m = Py_InitModule("gnchtmlwebkit", gnchtmlwebkit_functions);
    d = PyModule_GetDict(m);
	
    gnchtmlwebkit_register_classes(d);

    if (PyErr_Occurred ()) {
	PyErr_Print();
	Py_FatalError("can't initialise module gnchtmlwebkit");
    }
}
