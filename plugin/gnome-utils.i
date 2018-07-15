/********************************************************************\
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
 *                                                                  *
\********************************************************************/

%module sw_gnome_utils
%{
/* Includes the header in the wrapper code */
#include <config.h>
#include <gtk/gtk.h>
#include <glib-object.h>
#include <dialog-options.h>
#include <gnc-main-window.h>
#include <gnc-plugin.h>
#include <gnc-plugin-page.h>
#include <gnc-plugin-manager.h>
%}
#if defined(SWIGGUILE)
%{
#include "guile-mappings.h"

SCM scm_init_sw_gnome_utils_module (void);
%}
#endif

%import "base-typemaps.i"

GNCOptionWin * gnc_options_dialog_new(gchar *title, GtkWindow* parent);
void gnc_options_dialog_destroy(GNCOptionWin * win);
void gnc_options_dialog_build_contents(GNCOptionWin *propertybox,
                                       GNCOptionDB  *odb);
#if defined(SWIGGUILE)
void gnc_options_dialog_set_scm_callbacks (GNCOptionWin *win,
        SCM apply_cb, SCM close_cb);

gboolean
gnc_verify_dialog (GtkWindow *parent, gboolean yes_is_default,
		   const gchar *format, ...);

void
gnc_warning_dialog (GtkWindow *parent,
                    const gchar *format, ...);
void
gnc_error_dialog (GtkWindow *parent,
		  const char *format, ...);
void
gnc_info_dialog (GtkWindow *parent,
		 const char *format, ...);

#if defined(SWIGGUILE)
void gnc_add_scm_extension (SCM extension);
#endif

void gnc_set_busy_cursor (GtkWidget *w, gboolean update_now);
void gnc_unset_busy_cursor (GtkWidget *w);
void gnc_window_show_progress (const char *message, double percentage);

gboolean gnucash_ui_is_running(void);

TaxTableWindow * gnc_ui_tax_table_window_new (GtkWindow *parent, QofBook *book);
#endif

/* this is a very limited wrap - for python we need a lot more */

#if defined(SWIGPYTHON)

/* un fucking believable - apparently I need to define G_BEGIN_DECLS in swig */
/* and of course G_END_DECLS */
/* because glib/gmacros.h is not included in swig - could explicitly include it here
   but as its just a null macro (not c++) lets just define here
   - wont get any extraneous wrapping */
#define G_BEGIN_DECLS
#define G_END_DECLS

%include <dialog-options.h>
%include <gnc-main-window.h>
%include <gnc-plugin.h>
%include <gnc-plugin-page.h>


/* so importing engine.i gets us the swig types but does not include any C code generation for objects in engine.i */
%import "engine.i"

%include <gnc-plugin-manager.h>

#endif
