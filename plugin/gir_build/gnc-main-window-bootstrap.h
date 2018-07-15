/*
 * gnc-main-window.h -- GtkWindow which represents the
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

/*  @addtogroup Windows
    @{ */
/*  @addtogroup GncMainWindow Main Window functions.
    @{ */
/*  @file gnc-main-window.h
    @brief Functions for adding content to a window.
    @author Copyright (C) 2003 Jan Arne Petersen <jpetersen@uni-bonn.de>
    @author Copyright (C) 2003,2005 David Hampton <hampton@employees.org>
*/

#ifndef __GNC_MAIN_WINDOW_H
#define __GNC_MAIN_WINDOW_H

#include <gtk/gtk.h>
#include "gnc-plugin-page.h"

/* type macros */
#define GNC_TYPE_MAIN_WINDOW            (gnc_main_window_get_type ())
#define GNC_MAIN_WINDOW(obj)            (G_TYPE_CHECK_INSTANCE_CAST ((obj), GNC_TYPE_MAIN_WINDOW, GncMainWindow))
#define GNC_MAIN_WINDOW_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST ((klass), GNC_TYPE_MAIN_WINDOW, GncMainWindowClass))
#define GNC_IS_MAIN_WINDOW(obj)         (G_TYPE_CHECK_INSTANCE_TYPE ((obj), GNC_TYPE_MAIN_WINDOW))
#define GNC_IS_MAIN_WINDOW_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE ((klass), GNC_TYPE_MAIN_WINDOW))
#define GNC_MAIN_WINDOW_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS ((obj), GNC_TYPE_MAIN_WINDOW, GncMainWindowClass))

#define PLUGIN_PAGE_IMMUTABLE    "page-immutable"

/* typedefs & structures */

/*  The instance data structure for a main window object. */
typedef struct GncMainWindow
{
    GtkWindow gtk_window;	/* < The parent object for a main window. */
    GtkUIManager *ui_merge; /* < A pointer to the UI Manager data
				   structure for the whole window. */
} GncMainWindow;

/*  The class data structure for a main window object. */
typedef struct
{
    GtkWindowClass gtk_window;	/* < The parent class for a
					   main window. */

    /* callbacks */
    void (*page_added)   (GncMainWindow *window,
                          GncPluginPage *page);
    void (*page_changed) (GncMainWindow *window,
                          GncPluginPage *page);
} GncMainWindowClass;

typedef struct
{
    GncMainWindow *window;
    gpointer data;
} GncMainWindowActionData;

typedef void (*GncMainWindowFunc) (GncMainWindow *window, GncPluginPage *page);
typedef void (*GncMainWindowPageFunc) (GncPluginPage *page, gpointer user_data);

/* function prototypes */

/**
 * gnc_main_window_get_type:
 *
 *  Get the type of a gnc main window.
 *
 *  @return A GType.
 */
GType gnc_main_window_get_type (void);



#endif /* __GNC_MAIN_WINDOW_H */

/*  @} */
/*  @} */
