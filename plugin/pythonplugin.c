
// for the moment I dont know if I can combine both the python module and plugin
// in a single object

#include <Python.h>

#include <stdio.h>


#include <glib.h>

#include <glib/gi18n.h>

#include <glib-object.h>

#include <pygobject.h>

#include "config.h"

#include "gnc-module.h"

#include "gnc-plugin.h"

#include "gnc-plugin-python-generic.h"


// what I need is a list of callback functions

static PyObject *pPluginObject = NULL;

void python_plugin_class_init(GObjectClass *, GncPluginClass *);
void python_plugin_init(GncPluginpythongeneric *);
void python_plugin_finalize(GObject *);

struct _plugin_functions {
    void (* python_callback_class_init)(GObjectClass *, GncPluginClass *);
    void (* python_callback_init)(GncPluginpythongeneric *);
    void (* python_callback_finalize)(GObject *);
};


struct _plugin_functions global_plugin_functions = {
    python_plugin_class_init,
    python_plugin_init,
    python_plugin_finalize,
};


/* Command callbacks */
static void gnc_plugin_python_generic_cmd_callback (GtkAction *action, GncMainWindowActionData *data);

#define PLUGIN_ACTIONS_NAME "gnc-plugin-python-generic-actions"
#define PLUGIN_UI_FILENAME  "/Users/djosg/.gnucash/ui/gnc-plugin-python-generic-ui.xml"

#define MAX_PLUGIN_ACTIONS 100
static GtkActionEntry gnc_plugin_actions[MAX_PLUGIN_ACTIONS];
static guint gnc_plugin_n_actions = 0;

// static GtkActionEntry gnc_plugin_actions [] = {
//     /* Menu Items */
//     { "pythongenericAction", NULL, N_("python generic description..."), NULL,
//       N_("python generic tooltip"),
//       G_CALLBACK(gnc_plugin_python_generic_cmd_callback) },
// };
//static guint gnc_plugin_n_actions = G_N_ELEMENTS(gnc_plugin_actions);


struct _plugin_functions *get_plugin_callbacks(void)
{
    return &(global_plugin_functions);
}

void
gnc_plugin_python_generic_add_to_window (GncPlugin *plugin,
                                         GncMainWindow *window,
                                         GQuark type)
{
    if (PyObject_HasAttrString(pPluginObject,"add_to_window"))
        {
        PyObject *py_window = pygobject_new((GObject *)window);
        PyObject *py_quark = PyInt_FromLong(type);
        PyObject_CallMethodObjArgs(pPluginObject,PyString_FromString("add_to_window"),py_window,py_quark,NULL);
        }
}

void
gnc_plugin_python_generic_remove_from_window (GncPlugin *plugin,
                                              GncMainWindow *window,
                                              GQuark type)
{
    if (PyObject_HasAttrString(pPluginObject,"remove_from_window"))
        {
        PyObject *py_window = pygobject_new((GObject*)window);
        PyObject *py_quark = PyInt_FromLong(type);
        PyObject_CallMethodObjArgs(pPluginObject,PyString_FromString("remove_from_window"),py_window,py_quark,NULL);
        }
}


void python_plugin_class_init(GObjectClass *object_class, GncPluginClass *plugin_class)
{
    PyObject *pDictRet;

    object_class->finalize = python_plugin_finalize;

    // these callbacks will also allow updates to main window GUI
    if (PyObject_HasAttrString(pPluginObject,"add_to_window"))
        {
        plugin_class->add_to_window = gnc_plugin_python_generic_add_to_window;
        }

    if (PyObject_HasAttrString(pPluginObject,"remove_from_window"))
        {
        plugin_class->remove_from_window = gnc_plugin_python_generic_remove_from_window;
        }


    if (global_plugin_functions.python_callback_class_init != NULL)
        {
        // probably should pass the GncPluginpythongeneric  here
        pDictRet = PyObject_CallMethod(pPluginObject,"plugin_class_init",NULL);

        // return a null dict to do no updates
        if (PyDict_Check(pDictRet) && PyDict_Size(pDictRet) > 0)
            {
            int itm;
            char *pstr1,*pstr2,*pstr3,*pstr4,*pstr5;

            PyObject *pActionsName = PyDict_GetItemString(pDictRet,"actions_name");
            char *pactionsname = PyString_AsString(pActionsName);

            PyObject *pActionList = PyDict_GetItemString(pDictRet,"actions");

            gnc_plugin_n_actions = PyList_Size(pActionList);

            // until we do proper mallocing
            if (gnc_plugin_n_actions > MAX_PLUGIN_ACTIONS)
                {
                fprintf(stderr,"Error in python_plugin_class_init - too many actions!!\n");
                }
            else
                {
                // NOTE the test for Py_None if string object is None
                // actually maybe should make ""  the NULL string??

                for (itm = 0; itm < gnc_plugin_n_actions; itm++)
                    {
                    GtkActionEntry *tmpgtkact = &gnc_plugin_actions[itm];
                    PyObject *ptupl = PyList_GetItem(pActionList,itm);
                    PyObject *pitm1 = PyTuple_GetItem(ptupl,0);
                    if (pitm1 != Py_None)
                        pstr1 = PyString_AsString(pitm1);
                    else
                        pstr1 = NULL;
                    PyObject *pitm2 = PyTuple_GetItem(ptupl,1);
                    if (pitm2 != Py_None)
                        pstr2 = PyString_AsString(pitm2);
                    else
                        pstr2 = NULL;
                    PyObject *pitm3 = PyTuple_GetItem(ptupl,2);
                    if (pitm3 != Py_None)
                        pstr3 = PyString_AsString(pitm3);
                    else
                        pstr3 = NULL;
                    PyObject *pitm4 = PyTuple_GetItem(ptupl,3);
                    if (pitm4 != Py_None)
                        pstr4 = PyString_AsString(pitm4);
                    else
                        pstr4 = NULL;
                    PyObject *pitm5 = PyTuple_GetItem(ptupl,4);
                    if (pitm5 != Py_None)
                        pstr5 = PyString_AsString(pitm5);
                    else
                        pstr5 = NULL;
                    //PyObject *pitm6 = PyTuple_GetItem(ptupl,5);
                    //void *pstr6 = PyString_AsString(pitm6);
                    tmpgtkact->name = (gchar *)pstr1;
                    tmpgtkact->stock_id = (gchar *)pstr2;
                    tmpgtkact->label = N_(pstr3);
                    tmpgtkact->accelerator = (gchar *)pstr4;
                    tmpgtkact->tooltip = N_(pstr5);
                    tmpgtkact->callback = G_CALLBACK(gnc_plugin_python_generic_cmd_callback);
                    }

                PyObject *pUiFilename = PyDict_GetItemString(pDictRet,"ui_filename");
                char *puifilename = PyString_AsString(pUiFilename);

                /* widget addition/removal */
                plugin_class->actions_name       = pactionsname;
                plugin_class->actions            = gnc_plugin_actions;
                plugin_class->n_actions          = gnc_plugin_n_actions;
                plugin_class->ui_filename        = puifilename;

                }
            }
        }

        // always do this check at end of any routine using Python calls
        // to clear any python error that may have occurred
        // - otherwise will be reported at some later time!!
        if (PyErr_Occurred())
            {
            fprintf(stderr,"Python Error in python_plugin_class_init\n");
            PyErr_Print();
            }
}

void python_plugin_init(GncPluginpythongeneric *plugin)
{
    // not sure if really need GIL here - hasnt caused problems
    // maybe because before main usage of gtk threads
    PyGILState_STATE gstate;
    if (global_plugin_functions.python_callback_init != NULL)
        {
        PyGILState_Ensure();
        // probably should pass the GncPluginpythongeneric  here
        PyObject_CallMethod(pPluginObject,"plugin_init",NULL);
        if (PyErr_Occurred())
            {
            fprintf(stderr,"Python Error in python_plugin_init\n");
            PyErr_Print();
            }
        PyGILState_Release(gstate);
        }
}

void python_plugin_finalize(GObject *object)
{
    PyGILState_STATE gstate;
    if (global_plugin_functions.python_callback_finalize != NULL)
        {
        PyGILState_Ensure();
        // probably should pass the GObject here
        PyObject_CallMethod(pPluginObject,"plugin_finalize",NULL);
        if (PyErr_Occurred())
            {
            fprintf(stderr,"Python Error in python_plugin_finalize\n");
            PyErr_Print();
            }
        PyGILState_Release(gstate);
        }
}

/************************************************************
 *                    Command Callbacks                     *
 ************************************************************/

static void
gnc_plugin_python_generic_cmd_callback (GtkAction *action, GncMainWindowActionData *data)
{
    PyGILState_STATE gstate;
    //ENTER ("action %p, main window data %p", action, data);
    // can we use this to map back to a specific callback
    const gchar *action_name = gtk_action_get_name(action);
    fprintf(stderr,"action callback %s\n",action_name);
    fprintf(stderr,"data pointer %llx\n",(void *)data);
    fprintf(stderr,"window pointer %llx\n",(void *)(data->window));
    fprintf(stderr,"subdata pointer %llx\n",(void *)(data->data));

    // we apparently need to wrap python calls from arbitrary points with this
    PyGILState_Ensure();

    /* pygobject_new handles NULL checking */
    PyObject *action_obj = pygobject_new((GObject *)action);

    // return a PyCObject - still need ctypes to extract
    //PyObject *data_obj = PyCObject_FromVoidPtr((void *)data, NULL);
    // another option - return a LongLong with address
    // and again use ctypes to extract
    //PyObject *data_obj = PyLong_FromUnsignedLongLong((unsigned PY_LONG_LONG)data);
    //PyObject_CallMethod(pPluginObject,"plugin_action_callback","OO",action_obj,data_obj);

    // final option - convert the two components of GncMainWindowActionData and pass back
    // note that GncMainWindow is a GType object so could return that as a GObject object
    //GncMainWindow *window;
    //gpointer data;
    // this is a GncMainWindow
    //GtkWindow gtk_window;       /**< The parent object for a main window. */
    //GtkUIManager *ui_merge; /**< A pointer to the UI Manager data
    //                               structure for the whole window. */

    GncMainWindow *window = data->window;
    void *gdata = data->data;

    //PyObject *window_obj = pygobject_new((GObject *)(&(window->gtk_window)));
    // this may be all we need to return the GncMainWindow object
    // which appears to be a simple GObject subclass of GtkWindow
    // only question is if we will have access to the window object
    PyObject *window_obj = pygobject_new((GObject *)window);
    PyObject *data_obj = PyLong_FromUnsignedLongLong((unsigned PY_LONG_LONG)gdata);

    PyObject *dict_obj = PyDict_New();
    PyDict_SetItemString(dict_obj,"window",window_obj);
    PyDict_SetItemString(dict_obj,"data",data_obj);

    PyObject_CallMethod(pPluginObject,"plugin_action_callback","OO",action_obj,dict_obj);
    if (PyErr_Occurred())
        {
        fprintf(stderr,"Python Error in plugin_action_callback\n");
        PyErr_Print();
        }

    fprintf(stderr,"Python OK in plugin_action_callback\n");

    PyGILState_Release(gstate);

    fprintf(stderr,"Python OK 1 in plugin_action_callback\n");

    g_message ("python-generic");
    //LEAVE (" ");
}


// lets use this method to load a plugin
// this way can pass arguments from python

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


static PyMethodDef methods[] =
{
    { "loadPlugin", wrap_loadplugin, METH_VARARGS, "load a gnc-plugin"},
    { NULL, NULL, 0, NULL }
};

PyMODINIT_FUNC
initpythonplugin(void)
{
    PyObject *modul;

    // to use ANY pygobject_... functions MUST have this
    init_pygobject();

    modul = Py_InitModule("pythonplugin", methods);
    if (modul == NULL)
        return;

}

