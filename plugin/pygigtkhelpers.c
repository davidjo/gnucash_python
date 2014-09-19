
#include <Python.h>

#include <glib-object.h>

#include <pygobject.h>

#include <gtk/gtk.h>

#include <libintl.h>


// helper functions to use GObject Introspection

//#include "gnc-plugin.h"

// duplicate definition instead of including gnc-plugin.h
// - very bad
typedef struct
{
    /*  The name of the action. */
    const char *action_name;
    /*  The alternate toolbar label to use */
    const char *label;
} action_toolbar_labels;


void
gnc_plugin_init_short_names (GtkActionGroup *action_group,
                             action_toolbar_labels *toolbar_labels);


static PyObject *
_wrap_gnc_plugin_init_short_names(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "action_group", "toolbar_labels", NULL };
    PyObject *action_group_obj;
    GtkActionGroup *action_group;
    PyObject *toolbar_labels_obj;
    action_toolbar_labels *toolbar_labels;
    int indx_toolbar_labels;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OO:GncPluginPage.init_short_names",
                                     kwlist, &action_group_obj, &toolbar_labels_obj)) {
        return NULL;
    }

    // dont yet know how to do this with gobject introspection
    //if (pygobject_check(action_group_obj, &PyGtkActionGroup_Type)) {
    //    action_group = GTK_ACTION_GROUP(pygobject_get(action_group_obj));
    //} else {
    //    PyErr_SetString(PyExc_TypeError,
    //                    "action_group must be a GtkActionGroup");
    //    return NULL;
    //}
    // something like this might work
    GType gtypbase = g_type_from_name("GtkActionGroup");
    // is this only way to get class??
    PyObject *cls = PyObject_GetAttrString(action_group_obj,"__class__");
    if (!PyObject_HasAttrString(cls,"__info__"))
        {
        PyErr_SetString(PyExc_TypeError,
                        "action_group must be a GtkActionGroup");
        return NULL;
        }
    PyObject *infoobj = PyObject_GetAttrString(cls,"__info__");
    PyObject *gtypobj = PyObject_CallMethod(infoobj,"get_g_type",NULL);
    if (gtypobj == NULL)
        {
        PyErr_SetString(PyExc_TypeError,
                        "action_group must be a GtkActionGroup");
        return NULL;
        }
    PyObject *gtypnam = PyObject_GetAttrString(gtypobj,"name");
    GType gtyp = g_type_from_name(PyString_AsString(gtypnam));
    if (gtyp != gtypbase)
        {
        PyErr_SetString(PyExc_TypeError,
                        "action_group must be a GtkActionGroup");
        return NULL;
        }
    action_group = GTK_ACTION_GROUP(pygobject_get(action_group_obj));

    if (!PyList_Check(toolbar_labels_obj)) {
        PyErr_SetString(PyExc_TypeError, "toolbar_labels argument is not a list");
        return NULL;
    }
    int nitms = PyList_Size(toolbar_labels_obj);
    toolbar_labels = (action_toolbar_labels *) g_malloc(sizeof(action_toolbar_labels)*(nitms+1));
    for (indx_toolbar_labels=0; indx_toolbar_labels<nitms; indx_toolbar_labels++)
        {
        PyObject *ptupl = PyList_GetItem(toolbar_labels_obj,indx_toolbar_labels);
        if (!PyTuple_Check(ptupl)) {
            PyErr_SetString(PyExc_TypeError, "toolbar_labels list item is not a tuple");
            return NULL;
        }
        PyObject *pitm1 = PyTuple_GetItem(ptupl,0);
        if (!PyString_Check(pitm1)) {
            PyErr_SetString(PyExc_TypeError, "toolbar_labels list item action_name is not a string");
            return NULL;
        }
        PyObject *pitm2 = PyTuple_GetItem(ptupl,1);
        if (!PyString_Check(pitm2)) {
            PyErr_SetString(PyExc_TypeError, "toolbar_labels list item label is not a string");
            return NULL;
        }
        toolbar_labels[indx_toolbar_labels].action_name = PyString_AsString(pitm1);
        toolbar_labels[indx_toolbar_labels].label = PyString_AsString(pitm2);
        }
    toolbar_labels[nitms].action_name = NULL;
    toolbar_labels[nitms].label = NULL;

    // hmm - this does not check if the action names in toolbar_labels
    // actually exists in the action_group
    gnc_plugin_init_short_names (action_group, toolbar_labels);

    // Im assuming gnc_plugin_init_short_names takes a copy of the names
    g_free(toolbar_labels);
    
    Py_INCREF(Py_None);
    return Py_None;
}

// this is the actual function - might just replace it completely

#ifdef USE_THIS

void
gnc_plugin_init_short_names (GtkActionGroup *action_group,
                             action_toolbar_labels *toolbar_labels)
{
    GtkAction *action;
    GValue value = { 0, };
    gint i;

    g_value_init (&value, G_TYPE_STRING);

    for (i = 0; toolbar_labels[i].action_name; i++)
    {
        /* Add a couple of short labels for the toolbar */
        action = gtk_action_group_get_action (action_group,
                                              toolbar_labels[i].action_name);
        g_value_set_static_string (&value, gettext(toolbar_labels[i].label));
        g_object_set_property (G_OBJECT(action), "short_label", &value);
    }
}

#endif


static PyMethodDef methods[] =
{
    { "init_short_names", _wrap_gnc_plugin_init_short_names, METH_VARARGS | METH_KEYWORDS, "call plugin init_short names with python list"},
    { NULL, NULL, 0, NULL }
};

PyMODINIT_FUNC
initpygigtkhelpers(void)
{
    PyObject *modul;

    // to use ANY pygobject_... functions MUST have this
    //init_pygobject();

    modul = Py_InitModule("pygigtkhelpers", methods);
    if (modul == NULL)
        return;

}

