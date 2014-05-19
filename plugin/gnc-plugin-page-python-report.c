/* gnc-plugin-page-report.c
 * Copyright (C) 2004 Joshua Sled <jsled@asynchronous.org>
 * Copyright (C) 2005 David Hampton <hampton@employees.org>
 *
 * Originally from window-report.c:
 * Copyright (C) 1997 Robin D. Clark
 * Copyright (C) 1998 Linas Vepstas
 * Copyright (C) 1999 Jeremy Collins ( gtk-xmhtml port )
 * Copyright (C) 2000 Dave Peticolas
 * Copyright (C) 2000 Bill Gribble
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of
 * the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, contact:
 *
 * Free Software Foundation           Voice:  +1-617-542-5942
 * 51 Franklin Street, Fifth Floor    Fax:    +1-617-542-2652
 * Boston, MA  02110-1301,  USA       gnu@gnu.org
 */

/** @addtogroup GUI
    @{ */
/** @addtogroup GuiReport Reports
    @{ */
/** @file gnc-plugin-page-report.c
    @brief  Report page.
    @author Copyright (C) 2004 Joshua Sled <jsled@asynchronous.org>
    @author Copyright (C) 2005 David Hampton <hampton@employees.org>
*/

#include "config.h"

#include <gtk/gtk.h>
#include <glib/gi18n.h>
#include <glib/gstdio.h>
#include <libguile.h>
#include <sys/stat.h>
#include <errno.h>

#include "gfec.h"
#include "dialog-custom-report.h"
#include "gnc-component-manager.h"
#include "gnc-engine.h"
#include "gnc-gnome-utils.h"
#include "gnc-guile-utils.h"
#include "gnc-html-history.h"
#include "gnc-html.h"
#include "gnc-html-factory.h"
#include "gnc-file.h"
#include "gnc-plugin.h"
#include "gnc-plugin-page-report.h"
#include "gnc-plugin-file-history.h"
#include "gnc-prefs.h"
#include "gnc-report.h"
#include "gnc-session.h"
#include "gnc-ui-util.h"
#include "gnc-ui.h"
#include "gnc-window.h"
#include "option-util.h"
#include "window-report.h"
#include "app-utils/business-options.h"
#include "gnome-utils/gnc-icons.h"
#include "gnome-utils/print-session.h"

#define WINDOW_REPORT_CM_CLASS "window-report"

/* NW: you can add GNC_MOD_REPORT to gnc-engine.h
or simply define it locally. Any unique string with
a gnucash- prefix will do. Then just set a log level
with qof_log_set_level().*/
static QofLogModule log_module = GNC_MOD_GUI;

static GObjectClass *parent_class = NULL;

// A static GHashTable to record the usage count for each printer
// output name. FIXME: Currently this isn't cleaned up at program
// shutdown because there isn't a place to easily insert a finalize()
// function for this. Oh well.
static GHashTable *static_report_printnames = NULL;

// Property-id values.
enum
{
    PROP_0,
    PROP_REPORT_ID,
};

typedef struct GncPluginPageReportPrivate
{
    int dummy;
} GncPluginPageReportPrivate;

#define GNC_PLUGIN_PAGE_REPORT_GET_PRIVATE(o)  \
   (G_TYPE_INSTANCE_GET_PRIVATE ((o), GNC_TYPE_PLUGIN_PAGE_REPORT, GncPluginPageReportPrivate))

static void gnc_plugin_page_report_class_init( GncPluginPageReportClass *klass );
static void gnc_plugin_page_report_init( GncPluginPageReport *plugin_page );
static GObject *gnc_plugin_page_report_constructor(GType this_type, guint n_properties, GObjectConstructParam *properties);
static void gnc_plugin_page_report_finalize (GObject *object);

static void gnc_plugin_page_report_constr_init(GncPluginPageReport *plugin_page, gint reportId);


GType
gnc_plugin_page_report_get_type (void)
{
    static GType gnc_plugin_page_report_type = 0;

    if (gnc_plugin_page_report_type == 0)
    {
        static const GTypeInfo our_info =
        {
            sizeof (GncPluginPageReportClass),
            NULL,
            NULL,
            (GClassInitFunc) gnc_plugin_page_report_class_init,
            NULL,
            NULL,
            sizeof (GncPluginPageReport),
            0,
            (GInstanceInitFunc) gnc_plugin_page_report_init
        };

        gnc_plugin_page_report_type = g_type_register_static (GNC_TYPE_PLUGIN_PAGE,
                                      "GncPluginPageReport",
                                      &our_info, 0);
    }

    return gnc_plugin_page_report_type;
}

static void
gnc_plugin_page_report_class_init (GncPluginPageReportClass *klass)
{
    GObjectClass *object_class = G_OBJECT_CLASS (klass);
    GncPluginPageClass *gnc_plugin_page_class = GNC_PLUGIN_PAGE_CLASS(klass);

    parent_class = g_type_class_peek_parent (klass);

    object_class->constructor = gnc_plugin_page_report_constructor;
    object_class->finalize = gnc_plugin_page_report_finalize;

    object_class->set_property = gnc_plugin_page_report_set_property;
    object_class->get_property = gnc_plugin_page_report_get_property;

    // FIXME: stock reporting icon?
    //gnc_plugin_page_class->tab_icon        = GNC_STOCK_ACCOUNT;
    gnc_plugin_page_class->plugin_name     = GNC_PLUGIN_PAGE_REPORT_NAME;

    gnc_plugin_page_class->create_widget   = gnc_plugin_page_report_create_widget;
    gnc_plugin_page_class->destroy_widget  = gnc_plugin_page_report_destroy_widget;
    gnc_plugin_page_class->save_page       = gnc_plugin_page_report_save_page;
    gnc_plugin_page_class->recreate_page   = gnc_plugin_page_report_recreate_page;
    gnc_plugin_page_class->page_name_changed = gnc_plugin_page_report_name_changed;
    gnc_plugin_page_class->update_edit_menu_actions = gnc_plugin_page_report_update_edit_menu;
    gnc_plugin_page_class->finish_pending   = gnc_plugin_page_report_finish_pending;

    g_type_class_add_private(klass, sizeof(GncPluginPageReportPrivate));

    // create the "reportId" property
    g_object_class_install_property( object_class,
                                     PROP_REPORT_ID,
                                     g_param_spec_int( "report-id",
                                             _("The numeric ID of the report."),
                                             _("The numeric ID of the report."),
                                             -1, G_MAXINT, -1, G_PARAM_CONSTRUCT_ONLY | G_PARAM_READWRITE ) );

    /* JSLED: report-selected?
    	plugin_page_signals[ACCOUNT_SELECTED] =
    	  g_signal_new ("account_selected",
    			G_OBJECT_CLASS_TYPE (object_class),
    			G_SIGNAL_RUN_FIRST,
    			G_STRUCT_OFFSET (GncPluginPageReportClass, account_selected),
    			NULL, NULL,
    			g_cclosure_marshal_VOID__POINTER,
    			G_TYPE_NONE, 1,
    			G_TYPE_POINTER);
    */

    // Also initialize the report name usage count table
    if (!static_report_printnames)
        static_report_printnames = g_hash_table_new_full(g_str_hash,
                                   g_str_equal, g_free, NULL);
}

static void
gnc_plugin_page_report_finalize (GObject *object)
{
    g_return_if_fail (GNC_IS_PLUGIN_PAGE_REPORT (object));

    ENTER("object %p", object);
    G_OBJECT_CLASS (parent_class)->finalize (object);
    LEAVE(" ");
}

gnc_plugin_page_report_init ( GncPluginPageReport *plugin_page )
{
}

static GObject*
gnc_plugin_page_report_constructor(GType this_type, guint n_properties, GObjectConstructParam *properties)
{
    GObject *obj;
    GncPluginPageReportClass *our_class;
    GObjectClass *parent_class;
    gint reportId = -42;
    int i;

    our_class = GNC_PLUGIN_PAGE_REPORT_CLASS (
                    g_type_class_peek (GNC_TYPE_PLUGIN_PAGE_REPORT));
    parent_class = G_OBJECT_CLASS (g_type_class_peek_parent (our_class));
    obj = parent_class->constructor(this_type, n_properties, properties);

    for (i = 0; i < n_properties; i++)
    {
        GObjectConstructParam prop = properties[i];
        if (strcmp(prop.pspec->name, "report-id") == 0)
        {
            reportId = g_value_get_int(prop.value);
        }
    }

    gnc_plugin_page_report_constr_init(GNC_PLUGIN_PAGE_REPORT(obj), reportId);

    return obj;
}

static void
gnc_plugin_page_report_constr_init(GncPluginPageReport *plugin_page, gint reportId)
{
    GncPluginPageReportPrivate *priv;
    GtkActionGroup *action_group;
    GncPluginPage *parent;
    gboolean use_new;
    gchar *name;

    DEBUG( "property reportId=%d", reportId );
    priv = GNC_PLUGIN_PAGE_REPORT_GET_PRIVATE(plugin_page);
    priv->reportId = reportId;

    gnc_plugin_page_report_setup( GNC_PLUGIN_PAGE(plugin_page) );

    /* Init parent declared variables */
    parent = GNC_PLUGIN_PAGE(plugin_page);
    use_new = gnc_prefs_get_bool (GNC_PREFS_GROUP_GENERAL_REPORT, GNC_PREF_USE_NEW);
    name = gnc_report_name( priv->initial_report );
    g_object_set(G_OBJECT(plugin_page),
                 "page-name",      name,
                 "page-uri",       "default:",
                 "ui-description", "gnc-plugin-page-report-ui.xml",
                 "use-new-window", use_new,
                 NULL);
    g_free(name);

    /* change me when the system supports multiple books */
    gnc_plugin_page_add_book(parent, gnc_get_current_book());

    /* Create menu and toolbar information */
    action_group =
        gnc_plugin_page_create_action_group(parent,
                                            "GncPluginPageReportActions");
    gtk_action_group_add_actions( action_group,
                                  report_actions,
                                  num_report_actions,
                                  plugin_page );
    gnc_plugin_update_actions(action_group,
                              initially_insensitive_actions,
                              "sensitive", FALSE);
    gnc_plugin_init_short_names (action_group, toolbar_labels);
}

GncPluginPage*
gnc_plugin_page_report_new( int reportId )
{
    GncPluginPageReport *plugin_page;

    DEBUG( "report id = %d", reportId );
    plugin_page = g_object_new( GNC_TYPE_PLUGIN_PAGE_REPORT,
                                "report-id", reportId, NULL );
    DEBUG( "plugin_page: %p", plugin_page );
    DEBUG( "set %d on page %p", reportId, plugin_page );
    return GNC_PLUGIN_PAGE( plugin_page );
}

    g_free (default_dir);

    if (!filepath)
        return NULL;

    default_dir = g_path_get_dirname(filepath);
    gnc_set_default_directory (GNC_PREFS_GROUP_REPORT, default_dir);
    g_free(default_dir);

    rc = g_stat (filepath, &statbuf);

    /* Check for an error that isn't a non-existent file. */
    if (rc != 0 && errno != ENOENT)
    {
        /* %s is the strerror(3) string of the error that occurred. */
        const char *format = _("You cannot save to that filename.\n\n%s");

        gnc_error_dialog (NULL, format, strerror(errno));
        g_free(filepath);
        return NULL;
    }

    /* Check for a file that isn't a regular file. */
    if (rc == 0 && !S_ISREG (statbuf.st_mode))
    {
        const char *message = _("You cannot save to that file.");

        gnc_error_dialog (NULL, "%s", message);
        g_free(filepath);
        return NULL;
    }

    if (rc == 0)
    {
        const char *format = _("The file %s already exists. "
                               "Are you sure you want to overwrite it?");

        if (!gnc_verify_dialog (NULL, FALSE, format, filepath))
        {
            g_free(filepath);
            return NULL;
        }
    }

    return filepath;
}


/** @} */
/** @} */
