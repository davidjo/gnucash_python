/*
 * gnc-plugin-page.h -- A page, which can be added to the
 *	GnuCash main window.
 *
 * Copyright (C) 2003 Jan Arne Petersen <jpetersen@uni-bonn.de>
 * Copyright (C) 2003,2005 David Hampton <hampton@employees.org>
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

/*  @addtogroup ContentPlugins
    @{ */
/*  @addtogroup ContentPluginBase Common object and functions
    @{ */
/*  @file gnc-plugin-page.h
    @brief Functions for adding plugins to a GnuCash window.
    @author Copyright (C) 2003 Jan Arne Petersen
    @author Copyright (C) 2003,2005 David Hampton <hampton@employees.org>
*/

#ifndef __GNC_PLUGIN_PAGE_H
#define __GNC_PLUGIN_PAGE_H

#include <glib.h>
//#include "qof.h"

// why the hell is this missing in the new gnucash
// how is this included???
// bleeding eejits - we now only include the gtk.h in the .c file
// and this file is included AFTER that include so all entities are defined
#include <gtk/gtk.h>

// still having issues with GncMainWindow even if use bootstrap version
//#include "qofbook_bootstrap.h"
// this is how the type should appear if use QofBook
// but we have problems using it (circular references??)
// make dummy type definition then replace with correct version
//<type name="QofBook.Book" c:type="QofBook*"/>
//typedef void       QofBook;
typedef struct _QofBook       QofBook;


G_BEGIN_DECLS

#define GNC_PREF_SUMMARYBAR_POSITION_TOP    "summarybar-position-top"
#define GNC_PREF_SUMMARYBAR_POSITION_BOTTOM "summarybar-position-bottom"

/* type macros */
#define GNC_TYPE_PLUGIN_PAGE            (gnc_plugin_page_get_type ())
#define GNC_PLUGIN_PAGE(o)              (G_TYPE_CHECK_INSTANCE_CAST ((o), GNC_TYPE_PLUGIN_PAGE, GncPluginPage))
#define GNC_PLUGIN_PAGE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST ((klass), GNC_TYPE_PLUGIN_PAGE, GncPluginPageClass))
#define GNC_IS_PLUGIN_PAGE(o)           (G_TYPE_CHECK_INSTANCE_TYPE ((o), GNC_TYPE_PLUGIN_PAGE))
#define GNC_IS_PLUGIN_PAGE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE ((klass), GNC_TYPE_PLUGIN_PAGE))
#define GNC_PLUGIN_PAGE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS ((obj), GNC_PLUGIN_PAGE, GncPluginPageClass))

/* typedefs & structures */

/*  The instance data structure for a content plugin. */
typedef struct GncPluginPage
{
    GObject gobject;		/* < The parent object data. */

    GtkWidget *window;		/* < The window that contains the
					 *   display widget for this plugin.
					 *   This field is private to the
					 *   gnucash window management
					 *   code.  */
    GtkWidget *notebook_page;	/* < The display widget for this
					 *   plugin.  This field is private to
					 *   the gnucash window management
					 *   code.  */
    GtkWidget *summarybar;		/* < The summary bar widget (if any)
					 *   that is associated with this
					 *   plugin.  This field is private to
					 *   the gnucash window management
					 *   code.  */
} GncPluginPage;


/*  The class data structure for a content plugin. */
typedef struct
{
    GObjectClass gobject;

    /*  The relative name of the icon that should be shown on the
     *  tab for this page. */
    const gchar *tab_icon;
    /*  The textual name of this plugin. */
    const gchar *plugin_name;

    /* Signals */
    void (* inserted) (GncPluginPage *plugin_page);
    void (* removed) (GncPluginPage *plugin_page);
    void (* selected) (GncPluginPage *plugin_page);
    void (* unselected) (GncPluginPage *plugin_page);

    /* Virtual Table */

    /*  Function called to create the display widget for a
     *  particular type of plugin.  The returned widget should
     *  encompass all information that goes with this page,
     *  including scroll bars, a summary bar, etc.
     *
     *  @param plugin_page A pointer to the plugin for which a
     *  display widget should be created.
     *
     *  @return A displayable gtk widget. */
    GtkWidget *(* create_widget) (GncPluginPage *plugin_page);
    /*  Function called to destroy the display widget for a
     *  particular type of plugin.
     *
     *  @param plugin_page A pointer to the plugin whose display
     *  widget should be destroyed. */
    void (* destroy_widget) (GncPluginPage *plugin_page);

    /*  Save enough information about this page so that it can be
     *  recreated next time the user starts gnucash.
     *
     *  @param page The page to save.
     *
     *  @param key_file A pointer to the GKeyFile data structure where the
     *  page information should be written.
     *
     *  @param group_name The group name to use when writing data.
     *  The name is specific to this page instance. */
    void (* save_page) (GncPluginPage *page, GKeyFile *file,
                        const gchar *group);

    /*  Create a new page based on the information saved during a
     *  previous instantiation of gnucash.  This function may or
     *  may not install the new page in the window as it sees fit.
     *  Generally the function will install the page int the
     *  window in order to manipulate the menu items that are
     *  created at install time.
     *
     *  @param window The window where this new page will be
     *  installed.
     *
     *  @param key_file A pointer to the GKeyFile data structure where the
     *  page information should be retrieved.
     *
     *  @param group_name The group name to use when retrieving
     *  data.  The name is specific to this page instance.
     *
     *  @return A pointer to the new page. */
    GncPluginPage * (* recreate_page) (GtkWidget *window, GKeyFile *file,
                                       const gchar *group);

    /*  Perform plugin specific actions when a page is added to a
     *  window (or has been removed from one window and added to a
     *  new window).  This function is called after the page is
     *  installed in the window, just before the window's
     *  PAGE_ADDED signal is generated.
     *
     *  @param page The page that was added to a window.
     *
     *  @param window The window where the page was added. */
    void (* window_changed) (GncPluginPage *plugin_page, GtkWidget *window);

    /*  This function vector allows page specific actions to occur
     *  when the page name is changed.
     *
     *  @param page The page to update.
     *
     *  @param name The new name for this page. */
    void (* page_name_changed) (GncPluginPage *plugin_page,
                                const gchar *name);

    /*  This function vector allows page specific actions to
     *  override the generic code for setting the sensitivity of
     *  items in the Edit menu.
     *
     *  @param page The front page in a main window..
     *
     *  @param hide Whether the widgets should be shown or
     *  hidden. */
    void (* update_edit_menu_actions) (GncPluginPage *plugin_page, gboolean hide);

    /*  This function vector is called to finish any outstanding
     *  activities.  It will be called for such things as closing a
     *  page, saving the data file, etc.
     *
     *  @param page The page in a main window.
     *
     *  @return FALSE if the page could not or would not comply,
     *  which should cancel the pending operation.  TRUE
     *  otherwise */
    gboolean (* finish_pending) (GncPluginPage *plugin_page);
} GncPluginPageClass;


/**
 * gnc_plugin_page_get_type:
 *
 *  Get the type of a content plugin.
 *
 *  @return A GType.
 */
GType gnc_plugin_page_get_type (void);



G_END_DECLS

#endif /* __GNC_PLUGIN_PAGE_H */
/*  @} */
/*  @} */
