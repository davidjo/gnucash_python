
#include <pygobject.h>

#include <Python.h>
#include <swig-runtime-python.h>

// dummy define the ctype types so dont include the ctypes.h and figuring out
// where that is
// not working cause still need to link to ctypes module
//extern void *PointerType_Type;
//extern void *SimpleType_Type;


// get the swig type from the swig type name
// and return as PyCObject
// - how to return a ctypes object directly

static PyObject *wrap_get_swig_type(PyObject *self, PyObject *args)
{
    PyObject *pswigtype;
    PyObject *pswig;
    void *cobject;
    char *swigtypstr;

    if (!PyArg_ParseTuple(args, "s:get_swig_type", &swigtypstr))
        return NULL;

    fprintf(stderr,"swig type string %s\n",swigtypstr);

    swig_type_info *stype = SWIG_TypeQuery(swigtypstr);

    if (stype == NULL)
        {
        // or raise exception??
        //Py_INCREF(Py_None);
        //return Py_None;
        PyErr_SetString(PyExc_TypeError,"get_swig_type: swig type not found");
        return NULL;
        }

    pswig = PyCObject_FromVoidPtr((void *)stype, NULL);

    return pswig;
}

// this function takes a python int object assuming is address of object to be wrapped
// and converts to a wrapped SWIG object given the SWIG type string
// the assumption is the integer is a pointer to an object of the SWIG type
// these are highly dangerous functions as incomplete type compartibility
// tested for the moment

static PyObject *wrap_int_to_swig(PyObject *self, PyObject *args)
{
    PyObject *pint;
    char *swigtypstr;
    PyObject *pswig;
    void *cobject;

    if (!PyArg_ParseTuple(args, "Os:int_to_swig", &pint, &swigtypstr))
        return NULL;

    // pass a pointer as integer
    if (PyLong_Check(pint))
        cobject = (void *) PyLong_AsLongLong(pint);
    else if (PyInt_Check(pint))
        cobject = (void *) PyInt_AsUnsignedLongLongMask(pint);
    else
        {
        PyErr_SetString(PyExc_TypeError,"int_to_swig: unable to wrap this type of python object as swig");
        return NULL;
        }

    fprintf(stderr,"cobject pointer %llx\n",(void *)cobject);

    fprintf(stderr,"swig type string %s\n",swigtypstr);

    swig_type_info *stype = SWIG_TypeQuery(swigtypstr);

    if (stype == NULL)
        {
        PyErr_SetString(PyExc_TypeError,"int_to_swig: swig type not found");
        return NULL;
        }

    pswig = SWIG_NewPointerObj(cobject, stype, 0);

    return pswig;
}


// this function takes a C object
// and converts to a wrapped SWIG object given the SWIG type string
// these are highly dangerous functions as incomplete type compartibility
// tested for the moment


static PyObject *wrap_cobject_to_swig(PyObject *self, PyObject *args)
{
    PyObject *pcobj;
    char *swigtypstr;
    PyObject *pswig;
    void *cobject;

    if (!PyArg_ParseTuple(args, "Os:cobject_to_swig", &pcobj, &swigtypstr))
        return NULL;

    // pass a PyCObject
    // this is very dangerous - we have no check that the PyCObject
    // actually points to the swig type
    if (PyCObject_Check(pcobj))
        cobject = PyCObject_AsVoidPtr(pcobj);
    else
        {
        PyErr_SetString(PyExc_TypeError,"unable to wrap this type of python object as swig");
        return NULL;
        }

    fprintf(stderr,"cobject pointer %llx\n",(void *)cobject);

    fprintf(stderr,"swig type string %s\n",swigtypstr);

    swig_type_info *stype = SWIG_TypeQuery(swigtypstr);

    if (stype == NULL)
        {
        PyErr_SetString(PyExc_TypeError,"cobject_to_swig: swig type not found");
        return NULL;
        }

    pswig = SWIG_NewPointerObj(cobject, stype, 0);

    return pswig;
}

// this function takes a ctype object
// and converts to a wrapped SWIG object given the SWIG type string
// these are highly dangerous functions as incomplete type compartibility
// tested for the moment


static PyObject *wrap_ctypes_to_swig(PyObject *self, PyObject *args)
{
    PyObject *pctypes;
    char *swigtypstr;
    PyObject *pswig;
    void *cobject;

    if (!PyArg_ParseTuple(args, "Os:ctypes_to_swig", &pctypes, &swigtypstr))
        return NULL;

    // not clear what a good way to check for a general ctypes object is
    // actually doesnt matter - only certain ctypes types are going to be
    // compatible with the swig type
    // but cannot see a way of type checking this - eg how to know the swig
    // type is a pointer
    //if (PyObject_TypeCheck(pctypes, PointerType_Type))
    if (PyObject_HasAttrString(pctypes,"contents"))
        {
        PyObject *adrs = PyObject_CallFunction(pctypes,"addressof");
        cobject = (void *)PyInt_AsUnsignedLongLongMask(adrs);
        }
    //else if (PyObject_TypeCheck(pctypes, SimpleType_Type))
    else if (PyObject_HasAttrString(pctypes,"value"))
        {
        PyObject *adrs = PyObject_CallFunction(pctypes,"addressof");
        cobject = (void *)PyInt_AsUnsignedLongLongMask(adrs);
        }
    else
        {
        PyErr_SetString(PyExc_TypeError,"unable to wrap this type of python object as swig");
        return NULL;
        }

    fprintf(stderr,"cobject pointer %llx\n",(void *)cobject);

    fprintf(stderr,"swig type string %s\n",swigtypstr);

    swig_type_info *stype = SWIG_TypeQuery(swigtypstr);

    if (stype == NULL)
        {
        PyErr_SetString(PyExc_TypeError,"ctypes_to_swig: swig type not found");
        return NULL;
        }

    pswig = SWIG_NewPointerObj(cobject, stype, 0);

    return pswig;
}


static PyMethodDef methods[] =
{
    { "pointer_to_swig", wrap_int_to_swig, METH_VARARGS, "convert from int pointer to SWIG object"},
    { "int_to_swig", wrap_int_to_swig, METH_VARARGS, "convert from int pointer to SWIG object"},
    { "cobject_to_swig", wrap_cobject_to_swig, METH_VARARGS, "convert from cobject pointer to SWIG object"},
    { "ctypes_to_swig", wrap_ctypes_to_swig, METH_VARARGS, "convert from ctypes pointer to SWIG object"},
    { "get_swig_type", wrap_get_swig_type, METH_VARARGS, "find swig type if exists"},
    { NULL, NULL, 0, NULL }
};

PyMODINIT_FUNC
initswighelpers(void)
{
    PyObject *modul;

    // to use ANY pygobject_... functions MUST have this
    init_pygobject();

    modul = Py_InitModule("swighelpers", methods);
    if (modul == NULL)
        return;

}

