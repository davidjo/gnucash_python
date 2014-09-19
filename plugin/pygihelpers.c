
#include <Python.h>

#include <gtk/gtk.h>

// helper functions to use GObject Introspection

// dummy define the ctype types so dont include the ctypes.h and figuring out
// where that is
// not working cause still need to link to ctypes module
//extern void *PointerType_Type;
//extern void *SimpleType_Type;

static PyTypeObject *_PyGIStruct_Type;

PyObject *
_mypygi_struct_new (PyTypeObject *type,
                  gpointer      pointer,
                  gboolean      free_on_dealloc);


// this function takes a python int object assuming is address of object to be wrapped
// and converts to a wrapped PyGI object given the PyGI type string
// the assumption is the integer is a pointer to an object of the PyGI type
// these are highly dangerous functions as incomplete type compatibility
// tested for the moment

static PyObject *wrap_int_to_pygistruct(PyObject *self, PyObject *args)
{
    PyObject *pint;
    PyTypeObject *pygicls;
    char *pygitypstr;
    PyObject *ppygi;
    void *cobject;

    if (!PyArg_ParseTuple(args, "OO:int_to_pygistruct", &pint, &pygicls))
        return NULL;

    // annoying - I cant see if there is a StructMeta type defined 
    // this test is done in _pygi_struct_new also
    if (!PyType_IsSubtype (pygicls, _PyGIStruct_Type)) {
        PyErr_SetString(PyExc_TypeError,"int_to_pygistruct: Must pass a Struct type class");
        return NULL;
    }

    // pass a pointer as integer
    if (PyLong_Check(pint))
        cobject = (void *) PyLong_AsLongLong(pint);
    else if (PyInt_Check(pint))
        cobject = (void *) PyInt_AsUnsignedLongLongMask(pint);
    else
        {
        PyErr_SetString(PyExc_TypeError,"int_to_pygistruct: unable to wrap this type of python object as pygi");
        return NULL;
        }

    fprintf(stderr,"cobject pointer %llx\n",(void *)cobject);

    // TRUE will deallocate when the wrapper is freed
    // FALSE means need to deallocate struct memory somewhere else
    // BIG problem - what if struct memory is freed externally (as python will do)
    // problem - cannot link to this as its a module
    ppygi = _mypygi_struct_new (pygicls, cobject, FALSE);

    return ppygi;
}

// needed for PyGPointer
#include <pygobject.h>

// DANGEROUS - redefine from pygi.h

typedef struct {
    PyGPointer base;
    gboolean free_on_dealloc;
} PyGIStruct;

// DANGEROUS - copied from pygi-struct.c

PyObject *
_mypygi_struct_new (PyTypeObject *type,
                  gpointer      pointer,
                  gboolean      free_on_dealloc)
{
    PyGIStruct *self;
    GType g_type;

    if (!PyType_IsSubtype (type, _PyGIStruct_Type)) {
        PyErr_SetString (PyExc_TypeError, "must be a subtype of gi.Struct");
        return NULL;
    }

    fprintf(stderr,"type is 0x%llx\n",type);

    self = (PyGIStruct *) type->tp_alloc (type, 0);
    if (self == NULL) {
        return NULL;
    }

    fprintf(stderr,"self is 0x%llx\n",self);

    g_type = pyg_type_from_object ( (PyObject *) type);

    fprintf(stderr,"g_type is 0x%x\n",g_type);

    ( (PyGPointer *) self)->gtype = g_type;
    ( (PyGPointer *) self)->pointer = pointer;
    self->free_on_dealloc = free_on_dealloc;

    return (PyObject *) self;
}



static PyMethodDef methods[] =
{
    { "pointer_to_pygistruct", wrap_int_to_pygistruct, METH_VARARGS, "convert from int pointer to PyGI object"},
    { "int_to_pygistruct", wrap_int_to_pygistruct, METH_VARARGS, "convert from int pointer to PyGI object"},
    { NULL, NULL, 0, NULL }
};

PyMODINIT_FUNC
initpygihelpers(void)
{
    PyObject *m;
    PyObject *module;

    // to use ANY pygobject_... functions MUST have this
    // - this is new version of init_pygobject
    pygobject_init(-1,-1,-1);

    m = Py_InitModule("pygihelpers", methods);
    if (m == NULL)
        return;

    if ((module = PyImport_ImportModule("gi._gi")) != NULL) {
        _PyGIStruct_Type = (PyTypeObject *)PyObject_GetAttrString(module, "Struct");
        if (_PyGIStruct_Type == NULL) {
            PyErr_SetString(PyExc_ImportError,
                "cannot import name PyGIStruct_Type from gi");
            return ;
        }
    } else {
        PyErr_SetString(PyExc_ImportError,
            "could not import pygihelpers");
        return ;
    }

}

