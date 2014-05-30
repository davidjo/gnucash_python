
// it appears we need to protect callbacks from gnucash by the python GIL
// havent figured a way for this to be done automatically
// this module is used to add actions to existing gnucash menus
// so that the menu callback can add GIL protection before going into python

#include <Python.h>

#include <stdio.h>


#include <glib.h>

#include <glib/gi18n.h>

#include <glib-object.h>

#include <gtk/gtk.h>

#include <pygobject.h>


// static GtkActionEntry gnc_plugin_actions [] = {
//     /* Menu Items */
//     { "pythongenericAction", NULL, N_("python generic description..."), NULL,
//       N_("python generic tooltip"),
//       G_CALLBACK(gnc_plugin_python_generic_cmd_callback) },
// };
//static guint gnc_plugin_n_actions = G_N_ELEMENTS(gnc_plugin_actions);

#define MAX_PYTHON_ACTIONS 100
static GtkActionEntry gnc_python_actions[MAX_PYTHON_ACTIONS];

static void gnc_python_callback (GtkAction *action, PyObject *data);


// we basically have to hijack add_actions

static PyObject *
wrap_add_actions(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *py_callback_obj=NULL;
    PyGObject *py_actiongroup=NULL;
    PyObject *py_entries=NULL, *py_user_data=NULL;
    int itm;

    // looks like we need keywords for every argument
    static char *kwlist[] = {"callback", "actiongroup", "entries", "user_data", NULL};

    // we need to pass the actiongroup

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOO|O:pythoncallback.add_actions", kwlist,
                                      &py_callback_obj, &py_actiongroup, &py_entries, &py_user_data))
        return NULL;

    // we need to instantiate a new wrapcallback object
    //PyObject *newwrap = PyWrapCallBack_new(PyWrapCallBack_Type);
    // for the moment pass a callback object
    if (!PyObject_HasAttrString(py_callback_obj,"callbacks")) {
        PyErr_SetString(PyExc_KeyError, "callback object has no callbacks dict");
        return NULL;
    }
    PyObject *py_callbackdict = PyObject_GetAttrString(py_callback_obj,"callbacks");
    if (!PyDict_Check(py_callbackdict)) {
        PyErr_SetString(PyExc_TypeError, "callbacks attribute is not a dict");
        return NULL;
    }

    if (py_user_data != NULL) {
        if (!PyObject_HasAttrString(py_callback_obj,"user_data")) {
            PyErr_SetString(PyExc_AttributeError, "callback object has no user_data attribute");
            return NULL;
        }
        PyObject_SetAttrString(py_callback_obj,"user_data",py_user_data);
    }
    if (PyErr_Occurred())
        {
        fprintf(stderr,"Python Error in callback add_actions setup 1\n");
        PyErr_Print();
        }

    // we have to re-write the actions to replace the callback

    int n_actions = PyList_Size(py_entries);
    for (itm = 0; itm < n_actions; itm++)
        {
        char *pstr1,*pstr2,*pstr3,*pstr4,*pstr5;
        PyObject *pobj6;
        GtkActionEntry *tmpgtkact = &gnc_python_actions[itm];

        // NOTE the test for Py_None if string object is None
        // actually maybe should make ""  the NULL string??

        PyObject *ptupl = PyList_GetItem(py_entries,itm);
        int tupl_size = PyTuple_Size(ptupl);
        if (tupl_size < 1 || tupl_size > 6) {
            return NULL;
        }
        PyObject *pitm1 = PyTuple_GetItem(ptupl,0);
        pstr1 = NULL;
        if (pitm1 != Py_None)
            pstr1 = PyString_AsString(pitm1);
        pstr2 = NULL;
        if (tupl_size > 1) {
            PyObject *pitm2 = PyTuple_GetItem(ptupl,1);
            if (pitm2 != Py_None)
                pstr2 = PyString_AsString(pitm2);
        }
        pstr3 = NULL;
        if (tupl_size > 2) {
            PyObject *pitm3 = PyTuple_GetItem(ptupl,2);
            if (pitm3 != Py_None)
                pstr3 = PyString_AsString(pitm3);
        }
        pstr4 = NULL;
        if (tupl_size > 3) {
            PyObject *pitm4 = PyTuple_GetItem(ptupl,3);
            if (pitm4 != Py_None)
                pstr4 = PyString_AsString(pitm4);
        }
        pstr5 = NULL;
        if (tupl_size > 4) {
            PyObject *pitm5 = PyTuple_GetItem(ptupl,4);
            if (pitm5 != Py_None)
                pstr5 = PyString_AsString(pitm5);
        }
        if (tupl_size > 5) {
            pobj6 = PyTuple_GetItem(ptupl,5);
        } else {
            Py_INCREF(Py_None);
            pobj6 = Py_None;
        }
        if (PyErr_Occurred())
            {
            fprintf(stderr,"Python Error in callback add_actions setup 2\n");
            PyErr_Print();
            }

        // add python callback to callbacks dict
        PyDict_SetItem(py_callbackdict, pitm1, pobj6);
        if (PyErr_Occurred())
            {
            fprintf(stderr,"Python Error in callback add_actions setup 3\n");
            PyErr_Print();
            }

        // and re-save action entry with generic C callback
        tmpgtkact->name = (gchar *)pstr1;
        tmpgtkact->stock_id = (gchar *)pstr2;
        tmpgtkact->label = N_(pstr3);
        tmpgtkact->accelerator = (gchar *)pstr4;
        tmpgtkact->tooltip = N_(pstr5);
        if (pobj6 != Py_None)
            tmpgtkact->callback = G_CALLBACK(gnc_python_callback);
        else
            tmpgtkact->callback = NULL;
        }

    // always do this check at end of any routine using Python calls
    // to clear any python error that may have occurred
    // - otherwise will be reported at some later time!!
    if (PyErr_Occurred())
        {
        fprintf(stderr,"Python Error in callback add_actions setup\n");
        PyErr_Print();
        }

    // need to type check this!!
    GtkActionGroup *actiongroup = (GtkActionGroup*)(py_actiongroup->obj);

    // whats not clear is whether I need to allocate a new structure each time
    // or is the data copied??
    // we need to set up a list as this is the only way I see to add user data
    // how to add user_data to individual actions?? - you cant according to Gtk Manual!!
    // for the moment passing dict directly
    fprintf(stderr, "callback is %llx\n",(unsigned long long)py_callback_obj);
    gtk_action_group_add_actions(actiongroup, gnc_python_actions, n_actions, py_callback_obj);

    Py_INCREF(Py_None);
    return Py_None;
}

// this is callback we actually use in C

static void
gnc_python_callback (GtkAction *action, PyObject *data)
{
    PyGILState_STATE gstate;
    // can we use this to map back to a specific callback
    const gchar *action_name = gtk_action_get_name(action);
    fprintf(stderr,"action callback %s\n",action_name);

    fprintf(stderr, "data is %llx\n",(unsigned long long)data);

    // we apparently need to wrap python calls from arbitrary points with this
    PyGILState_Ensure();

    if (!PyObject_HasAttrString(data,"callbacks")) {
        fprintf(stderr,"gnc_python_callback: data has no callbacks attribute");
        PyGILState_Release(gstate);
        return;
    }
    PyObject *py_dict = PyObject_GetAttrString(data,"callbacks");

    if (!PyDict_Check(py_dict)) {
        fprintf(stderr,"gnc_python_callback: data callbacks is not a dict");
        PyGILState_Release(gstate);
        return;
    }

    // we need to lookup object associated with action name
    PyObject *callback = PyDict_GetItemString(py_dict,action_name);
    if (callback == NULL) {
        fprintf(stderr,"no callback for action");
        PyGILState_Release(gstate);
        return;
    }

    /* pygobject_new handles NULL checking */
    PyObject *action_obj = pygobject_new((GObject *)action);

    // access user_data if it exists
    PyObject *user_data = NULL;
    if (PyObject_HasAttrString(data, "user_data")) {
        user_data = PyObject_GetAttrString(data,"user_data");
    }

    PyObject *myargs = Py_BuildValue("(O)", action_obj);
    PyObject *kyargs = NULL;
    if (user_data != NULL) {
        kyargs = Py_BuildValue("{s:O}", "user_data", user_data);
    }

    PyObject_Call(callback,myargs,kyargs);
    Py_DECREF(myargs);
    Py_DECREF(kyargs);
    if (PyErr_Occurred())
        {
        fprintf(stderr,"Python Error in plugin_action_callback\n");
        PyErr_Print();
        }

    PyGILState_Release(gstate);
}



typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
} PyWrapCallBack;

static void
PyWrapCallBack_dealloc(PyWrapCallBack* self)
{
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
PyWrapCallBack_new(PyTypeObject* type, PyObject *args, PyObject *kwargs)
{
    PyWrapCallBack *self;

    self = (PyWrapCallBack *)type->tp_alloc(type, 0);

    //if (self != NULL) {
    //}

    return (PyObject *)self;
}

static int
PyWrapCallBack_init(PyWrapCallBack *self, PyObject *args, PyObject *kwds)
{
    //PyObject *first=NULL, *last=NULL, *number=NULL;

    //static char *kwlist[] = {"first", "last", "number", NULL};

    //if (! PyArg_ParseTupleAndKeywords(args, kwds, "|OOi", kwlist, 
    //                                  &first, &last, 
    //                                  &number))
    //    return -1; 

    return 0;
}


static PyMethodDef PyWrapCallBack_methods[] =
{
    { NULL, NULL, 0, NULL }
};


PyTypeObject PyWrapCallBack_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                 /* ob_size */
    "pygnc.WrapCallBack",                   /* tp_name */
    sizeof(PyWrapCallBack),          /* tp_basicsize */
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
    0,             /* tp_weaklistoffset */
    (getiterfunc)0,          /* tp_iter */
    (iternextfunc)0,     /* tp_iternext */
    (struct PyMethodDef*)NULL, /* tp_methods */
    (struct PyMemberDef*)0,              /* tp_members */
    (struct PyGetSetDef*)0,  /* tp_getset */
    NULL,                              /* tp_base */
    NULL,                              /* tp_dict */
    (descrgetfunc)0,    /* tp_descr_get */
    (descrsetfunc)0,    /* tp_descr_set */
    0,                 /* tp_dictoffset */
    (initproc)NULL,             /* tp_init */
    (allocfunc)0,           /* tp_alloc */
    (newfunc)0,               /* tp_new */
    (freefunc)0,             /* tp_free */
    (inquiry)0              /* tp_is_gc */
};



static PyMethodDef module_methods[] =
{
    { "add_actions", (PyCFunction)wrap_add_actions, METH_VARARGS | METH_KEYWORDS , "load actions into Gtk ActionGroup" },
    { NULL, NULL, 0, NULL }
};



PyMODINIT_FUNC
initpythoncallback(void)
{
    PyObject *modul;

    // to use ANY pygobject_... functions MUST have this
    init_pygobject();

    modul = Py_InitModule("pythoncallback", module_methods);
    if (modul == NULL)
        return;

}

