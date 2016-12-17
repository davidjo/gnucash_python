
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

// only defined in gnc-html.c
#define GNC_HTML_GET_PRIVATE(o) (GNC_HTML(o)->priv)

// only defined in gnc-html-webkit.c
#define GNC_HTML_WEBKIT_GET_PRIVATE(o) (GNC_HTML_WEBKIT(o)->priv)


static PyObject *
_wrap_gnc_html_webkit_show_data(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "html", "data", "datalen", NULL };
    PyGObject *html;
    char *data;
    int datalen;
    GncHtmlPrivate *priv_html;
    GncHtmlWebkitPrivate *priv;

    //fprintf(stderr,"webkit show data called 1\n");

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"Osi:Gnc.HtmlWebkit.show_data", kwlist, &html, &data, &datalen))
        return NULL;

    //fprintf(stderr,"webkit show data called 2\n");

    // we now call the gnc-html class pointer
    //gnc_html_webkit_show_data(GNC_HTML_WEBKIT(html->obj), data, datalen);

    GncHtml* gself_html = GNC_HTML(html->obj);
    GncHtmlWebkit* gself = GNC_HTML_WEBKIT(html->obj);

    fprintf(stderr,"html self is %p\n",(void *)gself_html);
    fprintf(stderr,"html self is %d\n",GNC_IS_HTML(gself_html));
    fprintf(stderr,"html self class is %p\n",(void *)GNC_HTML_GET_CLASS(gself_html));
    fprintf(stderr,"html self show_data is %p\n",(void *)(GNC_HTML_GET_CLASS(gself_html)->show_data));

    fprintf(stderr,"webkit self is %p\n",(void *)gself);
    fprintf(stderr,"webkit self is %d\n",GNC_IS_HTML(gself));
    fprintf(stderr,"webkit self class is %p\n",(void *)GNC_HTML_WEBKIT_GET_CLASS(gself));
    // so this does not exist - only the parent class GncHtml defines the show_data!!
    //fprintf(stderr,"webkit self show_data is %p\n",(void *)(GNC_HTML_WEBKIT_GET_CLASS(gself)->show_data));

    // this appears to be the way we call should call it rather than
    // direct pointer call
    // great - inspection of code show this only displays stuff if priv->html_string is set
    // note that the dispose function frees this

    priv_html = GNC_HTML_GET_PRIVATE(gself_html);
    fprintf(stderr,"html self priv %p\n",(char *)&(gself_html->priv));
    fprintf(stderr,"html self priv is %p\n",(void *)priv_html);

    priv = GNC_HTML_WEBKIT_GET_PRIVATE(gself);
    priv->html_string = g_strdup(data);

    fprintf(stderr,"html self html struct len %lx\n", sizeof(GncHtml));
    fprintf(stderr,"html self htmlwebkitstruct len %lx\n", sizeof(GncHtmlWebkit));
    fprintf(stderr,"webkit self priv %p\n",(char *)&(gself->priv));
    fprintf(stderr,"webkit self priv offset %llx\n",((char *)((char *)&(gself->priv)-(char *)gself)));
    fprintf(stderr,"webkit self priv is %p\n",(void *)priv);
    fprintf(stderr,"webkit self priv html_string is %p\n",(void *)&(priv->html_string));
    fprintf(stderr,"webkit self priv html_string offset %llx\n",((char *)&(priv->html_string)-(char *)priv));

    gnc_html_show_data( GNC_HTML(gself), data, datalen );

    Py_INCREF(Py_None);
    return Py_None;
}


static PyMethodDef methods[] =
{
    { "show_data", (PyCFunction)_wrap_gnc_html_webkit_show_data, METH_VARARGS | METH_KEYWORDS, "call webkit show_data setting hidden private variable"},
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

