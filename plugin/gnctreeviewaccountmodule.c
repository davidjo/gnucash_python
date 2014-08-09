/* -*- Mode: C; c-basic-offset: 4 -*- */


#include <Python.h>

/* include this first, before NO_IMPORT_PYGOBJECT is defined */
#include <pygobject.h>

void gnctreeviewaccount_register_classes (PyObject *d);

extern PyMethodDef gnctreeviewaccount_functions[];

DL_EXPORT(void)
initgnctreeviewaccount(void)
{
    PyObject *m, *d;
	
    init_pygobject();

    m = Py_InitModule("gnctreeviewaccount",gnctreeviewaccount_functions);
    d = PyModule_GetDict(m);
	
    gnctreeviewaccount_register_classes(d);

    if (PyErr_Occurred ()) {
	PyErr_Print();
	Py_FatalError("can't initialise module gnctreeviewaccount");
    }
}
