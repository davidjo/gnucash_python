
#include <glib-object.h>

#include <gtk/gtk.h>

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

    /* The window that triggered this URL request */
    GtkWindow *parent;

    /* The following members are used if the handler fails (returns FALSE). */
    gchar* error_message;
} GNCURLResult;

