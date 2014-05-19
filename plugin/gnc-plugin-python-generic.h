/*
 * gnc-plugin-python-generic.h --
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

/**
 * @addtogroup Tools
 * @{
 * @file gnc-plugin-python-generic.h
 * @brief Plugin registration of the example module
 * @author Copyright (C) 2009 ?enter your name here? <your-email@example.com>
 */

#ifndef GNC_PLUGIN_python_generic_H
#define GNC_PLUGIN_python_generic_H

#include <glib.h>

#include "gnc-plugin.h"

G_BEGIN_DECLS

/* type macros */
#define GNC_TYPE_PLUGIN_python_generic            (gnc_plugin_python_generic_get_type())
#define GNC_PLUGIN_python_generic(obj)            (TYPE_CHECK_INSTANCE_CAST((obj), GNC_TYPE_PLUGIN_python_generic, GncPluginpythongeneric))
#define GNC_PLUGIN_python_generic_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass),  GNC_TYPE_PLUGIN_python_generic, GncPluginpythongenericClass))
#define GNC_IS_PLUGIN_python_generic(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), GNC_TYPE_PLUGIN_python_generic))
#define GNC_IS_PLUGIN_python_generic_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass),  GNC_TYPE_PLUGIN_python_generic))
#define GNC_PLUGIN_python_generic_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj),  GNC_TYPE_PLUGIN_python_generic, GncPluginpythongenericClass))

#define GNC_PLUGIN_python_generic_NAME "gnc-plugin-python-generic"

/* typedefs & structures */
typedef struct {
    GncPlugin gnc_plugin;
} GncPluginpythongeneric;

typedef struct {
    GncPluginClass gnc_plugin;
} GncPluginpythongenericClass;

/* function prototypes */
/**
 * @return The glib runtime type of an python generic plugin page
 **/
GType gnc_plugin_python_generic_get_type (void);

/**
 * @return A new GncPluginpythongeneric object
 */
GncPlugin* gnc_plugin_python_generic_new (void);

/**
 * Create a new GncPluginpythongeneric object and register it.
 */
void gnc_plugin_python_generic_create_plugin (void);

G_END_DECLS

/** @} */

#endif /* GNC_PLUGIN_python_generic_H */
