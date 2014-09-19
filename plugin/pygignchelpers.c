
#include <Python.h>

#include <pygobject.h>

//#include <gtk/gtk.h>

//#include <libintl.h>


// helper functions to use GObject Introspection

#include "webkit/webkit.h"

#include "gnc-html.h"
#include "gnc-html-extras.h"

#include "gnc-html-webkit.h"
#include "gnc-html-webkit-p.h"

// only defined in gnc-html-webkit.c
#define GNC_HTML_WEBKIT_GET_PRIVATE(o) (GNC_HTML_WEBKIT(o)->priv)


static PyObject *
_wrap_gnc_html_webkit_show_data(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "html", "data", "datalen", NULL };
    PyGObject *html;
    char *data;
    int datalen;
    GncHtmlWebkitPrivate *priv;

    //fprintf(stderr,"webkit show data called 1\n");

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"Osi:Gnc.HtmlWebkit.show_data", kwlist, &html, &data, &datalen))
        return NULL;

    //fprintf(stderr,"webkit show data called 2\n");

    // we now call the gnc-html class pointer
    //gnc_html_webkit_show_data(GNC_HTML_WEBKIT(html->obj), data, datalen);

    GncHtmlWebkit* gself = GNC_HTML_WEBKIT(html->obj);

    fprintf(stderr,"html self is %llx\n",(void *)GNC_HTML(gself));
    fprintf(stderr,"html self is %d\n",GNC_IS_HTML(gself));
    fprintf(stderr,"html self class is %llx\n",(void *)GNC_HTML_GET_CLASS(gself));
    fprintf(stderr,"html self show_data is %llx\n",(void *)(GNC_HTML_GET_CLASS(gself)->show_data));

    // this appears to be the way we call should call it rather than
    // direct pointer call
    // great - inspection of code show this only displays stuff if priv->html_string is set
    // note that the dispose function frees this

    priv = GNC_HTML_WEBKIT_GET_PRIVATE(gself);
    priv->html_string = g_strdup(data);

    gnc_html_show_data( GNC_HTML(gself), data, datalen );

    Py_INCREF(Py_None);
    return Py_None;
}


static PyMethodDef methods[] =
{
    { "show_data", _wrap_gnc_html_webkit_show_data, METH_VARARGS | METH_KEYWORDS, "call webkit show_data setting hidden private variable"},
    { NULL, NULL, 0, NULL }
};

PyMODINIT_FUNC
initpygignchelpers(void)
{
    PyObject *modul;

    // to use ANY pygobject_... functions MUST have this
    //init_pygobject();

    modul = Py_InitModule("pygignchelpers", methods);
    if (modul == NULL)
        return;

}

