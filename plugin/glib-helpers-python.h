/********************************************************************\
 * glib-helpers-python.h -- gnucash glib helper functions for python*
 * Copyright (C) 2000 Linas Vepstas                                 *
 * Copyright (C) 2006 Chris Shoemaker <c.shoemaker@cox.net>         *
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
 *                                                                  *
\********************************************************************/

#ifndef GLIB_HELPERS_PYTHON_H
#define GLIB_HELPERS_PYTHON_H

#include <glib.h>
#include <Python.h>

PyObject *gnc_glist_to_python_list(GList *glist, gchar *wct);
GList* gnc_python_list_to_glist(PyObject *list);

PyObject *gnc_glist_string_to_python(GList *list);
GList * gnc_python_to_glist_string(PyObject *list);
int     gnc_glist_string_p(PyObject *list);

GSList * gnc_python_to_gslist_string(PyObject *list);



#endif
