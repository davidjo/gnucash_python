
#include <Python.h>
#include <swig-runtime-python.h>


int dbgflg = 0;


// dummy define the ctype types so dont include the ctypes.h and figuring out
// where that is
// not working cause still need to link to ctypes module
//extern void *PointerType_Type;
//extern void *SimpleType_Type;


//#ifdef SWIGPY_USE_CAPSULE
//    pswig = (swig_type_info *) PyCapsule_GetPointer(obj, NULL);
//#else
//    pswig = (swig_type_info *) PyCObject_AsVoidPtr(obj);
//#endif

// maybe this is how we can name the capsule
// the name has to exist externally to the capsule
// for the moment dont distinguish by swig type - we just
// want to ensure the passed capsule IS a SwigTypeCapsule
static char *swigtypecapsule = "SwigTypeCapsule";


// get the swig type from the swig type name
// and return as PyCObject (python 2) or PyCapsule (python 3)
// - how to return a ctypes object directly

static PyObject *wrap_get_swig_type(PyObject *self, PyObject *args)
{
    PyObject *pswigtype;
    PyObject *pswig;
    void *cobject;
    char *swigtypstr;

    if (!PyArg_ParseTuple(args, "s:get_swig_type", &swigtypstr))
        return NULL;

    if (dbgflg) fprintf(stderr,"swig type string %s\n",swigtypstr);

    swig_type_info *stype = SWIG_TypeQuery(swigtypstr);

    if (stype == NULL)
        {
        // or raise exception??
        //Py_INCREF(Py_None);
        //return Py_None;
        PyErr_SetString(PyExc_TypeError,"get_swig_type: swig type not found");
        return NULL;
        }

#ifdef SWIGPY_USE_CAPSULE
    pswig = PyCapsule_New((void*) stype, swigtypecapsule, NULL);
#else
    pswig = PyCObject_FromVoidPtr((void *)stype, NULL);
#endif

    return pswig;
}

// this function takes a python int object assuming is address of object to be wrapped
// and converts to a wrapped SWIG object given the SWIG type string
// the assumption is the integer is a pointer to an object of the SWIG type
// these are highly dangerous functions as incomplete type compatibility
// tested for the moment

static PyObject *wrap_int_to_swig(PyObject *self, PyObject *args)
{
    PyObject *pint;
    PyObject *pswigtyp;
    char *swigtypstr;
    PyObject *pswig;
    void *cobject;
    swig_type_info *stype = NULL;

    if (!PyArg_ParseTuple(args, "OO:int_to_swig", &pint, &pswigtyp))
        return NULL;

    // pass a pointer as integer
    if (PyLong_Check(pint))
        cobject = (void *) PyLong_AsLongLong(pint);
#if PY_VERSION_HEX < 0x03000000
    else if (PyInt_Check(pint))
        cobject = (void *) PyInt_AsUnsignedLongLongMask(pint);
#endif
    else
        {
        PyErr_SetString(PyExc_TypeError,"int_to_swig: unable to wrap this type of python object as swig");
        return NULL;
        }

    if (dbgflg) fprintf(stderr,"cobject pointer %llx\n",(unsigned long long)cobject);

#ifdef SWIGPY_USE_CAPSULE
    // allow pass either Capsule version of swig type or swig type string
    // assuming only this routine is generating the type capsule via wrap_get_swig_type
    if (PyCapsule_IsValid(pswigtyp, swigtypecapsule))
        {
	stype = (swig_type_info *) PyCapsule_GetPointer(pswigtyp, swigtypecapsule);
        if (dbgflg) fprintf(stderr,"swig type capsule\n");
        }
#else
    // allow pass either CObject version of swig type or swig type string
    // using CObjects very dangerous as no check if really is a swig type object
    if (PyCObject_Check(pswigtyp))
        {
        stype = PyCObject_AsVoidPtr(pswigtyp);
        if (dbgflg) fprintf(stderr,"swig type cobject\n");
        }
#endif
    else if (PyUnicode_Check(pswigtyp))
        {
        swigtypstr = PyUnicode_AsUTF8(pswigtyp);
        if (dbgflg) fprintf(stderr,"swig type string %s\n",swigtypstr);

        stype = SWIG_TypeQuery(swigtypstr);

        if (stype == NULL)
            {
            PyErr_SetString(PyExc_TypeError,"int_to_swig: swig type not found");
            return NULL;
            }
        }
    else
        {
        PyErr_SetString(PyExc_TypeError,"int_to_swig: passed bad swig type");
        return NULL;
        }

    pswig = SWIG_NewPointerObj(cobject, stype, 0);

    return pswig;
}


// note the following 2 functions not tested!!

#ifdef SWIGPY_USE_CAPSULE


// this function takes a C object
// and converts to a wrapped SWIG object given the SWIG type string
// these are highly dangerous functions as incomplete type compatibility
// tested for the moment


static PyObject *wrap_capsule_to_swig(PyObject *self, PyObject *args)
{
    PyObject *pcobj;
    char *swigtypstr;
    PyObject *pswig;
    void *cobject;

    if (!PyArg_ParseTuple(args, "Os:capsule_to_swig", &pcobj, &swigtypstr))
        return NULL;

    // pass a PyCapsule
    // we cant check for validity - except for capsule - as would need something
    // to define the wrapped C pointer capsule name
    // NOTA BENE - NULL has to match the capsule name - so only capsule with NULL name
    // will match here
    // NOTA BENE - we still are assuming the object the capsule is pointing to is the same type
    // as the passed swig type string
    cobject = PyCapsule_GetPointer(pcobj, NULL);
    if (cobject == NULL && PyErr_Occurred())
        {
        PyErr_SetString(PyExc_TypeError,"unable to wrap this type of python object as swig");
        return NULL;
        }

    if (dbgflg) fprintf(stderr,"capsule pointer %llx\n",(unsigned long long)cobject);

    if (dbgflg) fprintf(stderr,"swig type string %s\n",swigtypstr);

    swig_type_info *stype = SWIG_TypeQuery(swigtypstr);

    if (stype == NULL)
        {
        PyErr_SetString(PyExc_TypeError,"capsule_to_swig: swig type not found");
        return NULL;
        }

    pswig = SWIG_NewPointerObj(cobject, stype, 0);

    return pswig;
}

#else

// this function takes a C object
// and converts to a wrapped SWIG object given the SWIG type string
// these are highly dangerous functions as incomplete type compatibility
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

    if (dbgflg) fprintf(stderr,"cobject pointer %llx\n",(void *)cobject);

    if (dbgflg) fprintf(stderr,"swig type string %s\n",swigtypstr);

    swig_type_info *stype = SWIG_TypeQuery(swigtypstr);

    if (stype == NULL)
        {
        PyErr_SetString(PyExc_TypeError,"cobject_to_swig: swig type not found");
        return NULL;
        }

    pswig = SWIG_NewPointerObj(cobject, stype, 0);

    return pswig;
}

#endif

// this function takes a ctype object
// and converts to a wrapped SWIG object given the SWIG type string
// these are highly dangerous functions as incomplete type compatibility
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
#if PY_VERSION_HEX >= 0x03000000
        cobject = (void *)PyLong_AsLongLong(adrs);
#else
        cobject = (void *)PyInt_AsUnsignedLongLongMask(adrs);
#endif
        }
    //else if (PyObject_TypeCheck(pctypes, SimpleType_Type))
    else if (PyObject_HasAttrString(pctypes,"value"))
        {
        PyObject *adrs = PyObject_CallFunction(pctypes,"addressof");
#if PY_VERSION_HEX >= 0x03000000
        cobject = (void *)PyLong_AsLongLong(adrs);
#else
        cobject = (void *)PyInt_AsUnsignedLongLongMask(adrs);
#endif
        }
    else
        {
        PyErr_SetString(PyExc_TypeError,"unable to wrap this type of python object as swig");
        return NULL;
        }

    if (dbgflg) fprintf(stderr,"cobject pointer %llx\n",(unsigned long long)cobject);

    if (dbgflg) fprintf(stderr,"swig type string %s\n",swigtypstr);

    swig_type_info *stype = SWIG_TypeQuery(swigtypstr);

    if (stype == NULL)
        {
        PyErr_SetString(PyExc_TypeError,"ctypes_to_swig: swig type not found");
        return NULL;
        }

    pswig = SWIG_NewPointerObj(cobject, stype, 0);

    return pswig;
}


static PyMethodDef swighelpers_methods[] =
{
    { "pointer_to_swig", wrap_int_to_swig, METH_VARARGS, "convert from int pointer to SWIG object"},
    { "int_to_swig", wrap_int_to_swig, METH_VARARGS, "convert from int pointer to SWIG object"},
#ifdef SWIGPY_USE_CAPSULE
    { "capsule_to_swig", wrap_capsule_to_swig, METH_VARARGS, "convert from capsule pointer to SWIG object"},
#else
    { "cobject_to_swig", wrap_cobject_to_swig, METH_VARARGS, "convert from cobject pointer to SWIG object"},
#endif
    { "ctypes_to_swig", wrap_ctypes_to_swig, METH_VARARGS, "convert from ctypes pointer to SWIG object"},
    { "get_swig_type", wrap_get_swig_type, METH_VARARGS, "find swig type if exists"},
    { NULL, NULL, 0, NULL }
};

#if PY_VERSION_HEX >= 0x03000000

static struct PyModuleDef swighelpers_module = {
    PyModuleDef_HEAD_INIT,
    "swighelpers",   /* name of module */
    NULL,     /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    swighelpers_methods
};

PyMODINIT_FUNC
PyInit_swighelpers(void)
{
    // to use ANY pygobject_... functions MUST have this
    //init_pygobject();

    return PyModule_Create(&swighelpers_module);
}
#else
PyMODINIT_FUNC
initswighelpers(void)
{
    PyObject *modul;

    // to use ANY pygobject_... functions MUST have this
    //init_pygobject();

    modul = Py_InitModule("swighelpers", methods);
    if (modul == NULL)
        return;

}
#endif

