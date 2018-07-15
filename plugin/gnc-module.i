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


/* all these includes need to be base-typemaps.i */


%module sw_gnc_module
%{
#include <gnc-module.h>
%}
#if defined(SWIGGUILE)
%{
#include "guile-mappings.h"

SCM scm_init_sw_gnc_module_module (void);
%}
#endif

%import "base-typemaps.i"

/* so importing engine.i gets us the swig types but does not include any C code generation for objects in engine.i */
%import "engine.i"


void            gnc_module_system_init(void);
void            gnc_module_system_refresh(void);
GList         * gnc_module_system_modinfo(void);
GNCModule       gnc_module_load(gchar * module_name, gint interface);
GNCModule       gnc_module_load_optional(gchar * module_name, gint interface);
int             gnc_module_unload(GNCModule mod);
