/********************************************************************
 * gnc-html.h -- display html with gnc special tags                 *
 * Copyright (C) 2000 Bill Gribble <grib@billgribble.com>           *
 *                                                                  *
 * This program is free software; you can redistribute it and/or    *
 * modify it under the terms of the GNU General Public License as   *
 * published by the Free Software Foundation; either version 2 of   *
 * the License, or (at your option) any later version.              *
 *                                                                  *
 * This program is distributed in the hope that it will be useful,  *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of   *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the    *
 * GNU General Public License for more details.                     *
 *                                                                  *
 * You should have received a copy of the GNU General Public License*
 * along with this program; if not, contact:                        *
 *                                                                  *
 * Free Software Foundation           Voice:  +1-617-542-5942       *
 * 51 Franklin Street, Fifth Floor    Fax:    +1-617-542-2652       *
 * Boston, MA  02110-1301,  USA       gnu@gnu.org                   *
\********************************************************************/

#ifndef GNC_HTML_H
#define GNC_HTML_H

/**
 * GncHtml:
 *  A GncHtml object is an abstract base for an html engine used to display reports and
 *  charts in gnucash.  It must be overridden to create specific objects using specific
 *  html engines (e.g. webkit).
 */

#include <glib-object.h>

#include <gtk/gtk.h>

G_BEGIN_DECLS

#define GNC_TYPE_HTML         (gnc_html_get_type())
#define GNC_HTML(o)           (G_TYPE_CHECK_INSTANCE_CAST ((o), GNC_TYPE_HTML, GncHtml))
#define GNC_HTML_CLASS(k)     (G_TYPE_CHECK_CLASS_CAST((k), GNC_TYPE_HTML, GncHtmlClass))
#define GNC_IS_HTML(o)        (G_TYPE_CHECK_INSTANCE_TYPE((o), GNC_TYPE_HTML))
#define GNC_IS_HTML_CLASS(k)  (G_TYPE_CHECK_CLASS_TYPE((o), GNC_TYPE_HTML))
#define GNC_HTML_GET_CLASS(o) (G_TYPE_INSTANCE_GET_CLASS((o), GNC_TYPE_HTML, GncHtmlClass))

GType gnc_html_get_type(void);

typedef struct _GncHtml GncHtml;
typedef struct _GncHtmlClass GncHtmlClass;
typedef struct _GncHtmlPrivate GncHtmlPrivate;

#include "gnc-html-extras.h"

/* The result structure of url handlers. Strings should be g_malloc'd
 * by the handler and will be freed by gnc_html. */
typedef struct
{
    /* The following members are used if the handler succeeds (returns TRUE). */

    gboolean load_to_stream; /* If TRUE, the url should be loaded from
                            * a stream using the rest of the data in
                            * the struct into the original gnc_html
                            * object. If FALSE, the handler will
                            * perform all needed actions itself. */

    URLType url_type;        /* Defaults to original */
    gchar* location;         /* If NULL, use original (NULL is default) */
    gchar* label;            /* If NULL, use original (NULL is default) */

    URLType base_type;
    gchar* base_location;

    /* The following members are used if the handler fails (returns FALSE). */
    gchar* error_message;
} GNCURLResult;

typedef gboolean (* GncHTMLObjectCB)(GncHtml* html, gpointer eb,
                                     gpointer data);
typedef gboolean (* GncHTMLStreamCB)(const gchar* location, gchar** data, int* datalen);
typedef gboolean (* GncHTMLUrlCB)(const gchar* location, const gchar* label,
                                  gboolean new_window, GNCURLResult* result);

/**
 * gnc_html_register_urltype:
 * @type : New URL type
 * @protocol : Protocol - should be an empty string if there is no corresponding protocol.
 *  Registers a new URLType.
 *  returns TRUE if succesful, FALSE if type already exists.
 * return : TRUE if successful, FALSE if type already exists or protocol is NULL.
 */
gboolean gnc_html_register_urltype( URLType type, const gchar* protocol );

/**
 * gnc_html_initialize:
 *  Initializes the html subsystem
 */
void gnc_html_initialize( void );

gchar* gnc_html_encode_string( const gchar* in );
gchar* gnc_html_decode_string( const gchar* in );
gchar* gnc_html_escape_newlines( const gchar* in );
gchar* gnc_html_unescape_newlines( const gchar* in );

/* object handlers deal with <object classid="foo"> objects in HTML.
 * the handlers are looked up at object load time. */
/**
 * gnc_html_register_object_handler:
 * @classid : class id string
 * @hand : (scope notified) : callback
 */
/**
 * gnc_html_unregister_object_handler:
 * @classid : class id string
 */
void gnc_html_register_object_handler( const gchar* classid, GncHTMLObjectCB hand );
void gnc_html_unregister_object_handler( const gchar* classid );

/* stream handlers load data for particular URLTypes. */
/**
 * gnc_html_register_stream_handler:
 * @url_type: URL type string
 * @hand: (scope notified) : callback
 */
void gnc_html_register_stream_handler( URLType url_type, GncHTMLStreamCB hand );
void gnc_html_unregister_stream_handler( URLType url_type );

/* handlers for particular URLTypes. */
/**
 * gnc_html_register_url_handler:
 * @url_type: URL type string
 * @hand: (scope notified) : callback
 */
void gnc_html_register_url_handler( URLType url_type, GncHTMLUrlCB hand );
void gnc_html_unregister_url_handler( URLType url_type );

#include "gnc-html-history.h"

typedef int  (* GncHTMLUrltypeCB)(URLType ut);
typedef void (* GncHTMLFlyoverCB)(GncHtml* html, const gchar* url,
                                  gpointer data);
typedef void (* GncHTMLLoadCB)(GncHtml* html, URLType type,
                               const gchar* location, const gchar* label,
                               gpointer data);
typedef int  (* GncHTMLButtonCB)(GncHtml* html, GdkEventButton* event,
                                 gpointer data);

struct _GncHtmlClass
{
    GtkBinClass parent_class;

    /* Methods */
    void (*show_url)( GncHtml* html,
                      URLType type,
                      const gchar* location,
                      const gchar* label,
                      gboolean new_window_hint );
    void (*show_data)( GncHtml* html, const gchar* data, int datalen );
    void (*reload)( GncHtml* html );
    void (*copy_to_clipboard)( GncHtml* html );
    gboolean (*export_to_file)( GncHtml* html, const gchar* file );
    void (*print)( GncHtml* html, const gchar* jobname, gboolean export_pdf );
    void (*cancel)( GncHtml* html );
    /**
     * parse_url:
     * @html: html object pointer
     * @url: url string
     * @url_location: (out): url locations
     * @url_label: (out): url labels
     * return: parsed URLType
     */
    URLType (*parse_url)( GncHtml* html, const gchar* url,
                          gchar** url_location, gchar** url_label );
    void (*set_parent)( GncHtml* html, GtkWindow* parent );
};

struct _GncHtml
{
    GtkBin parent_instance;

    /*< private >*/
    GncHtmlPrivate* priv;
};

/**
 * gnc_html_destroy:
 * @html : GncHtml object to destroy
 *  Destroys a GncHtml object.
 *
 */
void gnc_html_destroy( GncHtml* html );

/**
 * gnc_html_show_url:
 * @html : GncHtml object
 * @type : URLType object
 * @location : a url
 * @label : a label
 * @new_window_hint : make a new window maybe
 *  Displays a URL in a GncHtml object.
 *
 */
void gnc_html_show_url( GncHtml* html, URLType type, const gchar* location,
                        const gchar* label, gboolean new_window_hint );

/**
 * gnc_html_show_data:
 * @html : GncHtml object
 * @data : User data
 * @datalen : Length of user data
 *  Displays an HTML string in a GncHtml object.
 *
 */
void gnc_html_show_data( GncHtml* html, const gchar* data, int datalen );

/**
 * gnc_html_reload:
 * @html : GncHtml object
 *  Reloads the current GncHtml object.
 *
 */
void gnc_html_reload( GncHtml* html );

/**
 * gnc_html_copy_to_clipboard:
 * @html : GncHtml object
 *  Copies the html to the clipboard
 *
 */
void gnc_html_copy_to_clipboard( GncHtml* html );

/**
 * gnc_html_export_to_file:
 * @html : GncHtml object
 * @file : External file name
 *  Exports the html to an external file.
 * return : TRUE if successful, FALSE if unsuccessful
 */
gboolean gnc_html_export_to_file( GncHtml* html, const gchar* file );

/**
 * gnc_html_print:
 * @html : GncHtml object
 * @jobname : A jobname for identifying this job, or to be used as an output file
 * @export_pdf : If TRUE, only run a "print to PDF" operation in order to
          export this to pdf. If FALSE, run a normal printing dialog.
 *  Prints the report.
 *
 */
void gnc_html_print( GncHtml* html, const gchar* jobname, gboolean export_pdf );

/**
 * gnc_html_cancel:
 * @html : GncHtml object
 * Cancels the current operation
 *
 */
void gnc_html_cancel( GncHtml* html );

/**
 * gnc_html_parse_url:
 * @html : GncHtml object
 * @url : URL
 * @url_location : (out) : Pointer where to store address of string containing main URI
 * @url_label : (out) : Pointer where to store address of string containing label
 * return: (transfer none) : type of parsed URL
 *
 *  Parses a URL into URI and label
 *
 */
URLType gnc_html_parse_url( GncHtml* html, const gchar* url,
                            gchar** url_location, gchar** url_label );

/**
 * gnc_html_get_history:
 * @html : GncHtml object
 *
 * return : (transfer none) : History
 *
 *  Returns the history for this html engine
 */
gnc_html_history* gnc_html_get_history( GncHtml* html );

/**
 * gnc_html_get_widget:
 * @html : GncHtml object
 * return: (transfer none) : main widget
 *
 *  Returns the main widget for this html engine
 */
GtkWidget* gnc_html_get_widget( GncHtml* html );

/**
 * gnc_html_set_parent:
 * @html : GncHtml object
 * @parent : Parent window
 *  Sets the parent window for this html engine.  The engine will be embedded in this parent.
 *
 */
void gnc_html_set_parent( GncHtml* html, GtkWindow* parent );

/* setting callbacks */
/**
 * gnc_html_set_urltype_cb:
 * @html: A #GncHtml
 * @urltype_cb: (scope notified) : a callback
 */
/**
 * gnc_html_set_load_cb:
 * @html: A #GncHtml
 * @load_cb: (scope notified) : a callback
 * @data: A #gpointer
 */
/**
 * gnc_html_set_flyover_cb:
 * @html: A #GncHtml
 * @newwin_cb: (scope notified) : a callback
 * @data: A #gpointer
 */
/**
 * gnc_html_set_button_cb:
 * @html: A #GncHtml
 * @button_cb: (scope notified) : a callback
 * @data: A #gpointer
 */
void gnc_html_set_urltype_cb( GncHtml* html, GncHTMLUrltypeCB urltype_cb );
void gnc_html_set_load_cb( GncHtml* html, GncHTMLLoadCB load_cb, gpointer data );
void gnc_html_set_flyover_cb( GncHtml* html, GncHTMLFlyoverCB newwin_cb, gpointer data );
void gnc_html_set_button_cb( GncHtml* html, GncHTMLButtonCB button_cb, gpointer data );

/**
 * gnc_html_get_embedded_param:
 * @eb: gpointer
 * @param_name: gpointer
 * return: (transfer none) : returned params
 */
const gchar* gnc_html_get_embedded_param( gpointer eb, const gchar* param_name );

#endif
