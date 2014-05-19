/*
 * gnc-plugin-python-generic.c --
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
 * @internal
 * @file gnc-plugin-python-generic.c
 * @brief Plugin registration of the python generic plugin
 * @author Copyright (C) 2009 ?enter your name here? <your-email@python_generic.com>
 */


#include "config.h"

#include <glib/gi18n.h>

#include "gnc-plugin-python-generic.h"

#include <stdio.h>

// define the external functions
//extern void python_plugin_class_init(GObjectClass *, GncPluginClass *);
//extern void python_plugin_init(GncPluginpythongeneric *);
//extern void python_plugin_finalize(GObject *);

/* This static indicates the debugging module that this .o belongs to.  */
static QofLogModule log_module = G_LOG_DOMAIN;

struct _plugin_functions {
    void (*python_callback_class_init)(GObjectClass *, GncPluginClass *);
    void (*python_callback_init)(GncPluginpythongeneric *);
    void (*python_callback_finalize)(GObject *);
};

struct _plugin_functions *get_plugin_callbacks();

// static void gnc_plugin_python_generic_class_init         (GncPluginpythongenericClass *klass);
// static void gnc_plugin_python_generic_init               (GncPluginpythongeneric *plugin);
// static void gnc_plugin_python_generic_finalize           (GObject *object);


/************************************************************
 *                   Object Implementation                  *
 ************************************************************/

G_DEFINE_TYPE(GncPluginpythongeneric, gnc_plugin_python_generic, GNC_TYPE_PLUGIN)

GncPlugin *
gnc_plugin_python_generic_new (void)
{
    fprintf(stderr,"generic new called\n");
    return GNC_PLUGIN (g_object_new (GNC_TYPE_PLUGIN_python_generic, (gchar*) NULL));
}

static void
gnc_plugin_python_generic_class_init (GncPluginpythongenericClass *klass)
{
    GObjectClass *object_class = G_OBJECT_CLASS (klass);
    GncPluginClass *plugin_class = GNC_PLUGIN_CLASS(klass);

    fprintf(stderr,"generic class init called\n");

    /* plugin info */
    plugin_class->plugin_name  = GNC_PLUGIN_python_generic_NAME;

    (get_plugin_callbacks())->python_callback_class_init(object_class, plugin_class);

}

static void
gnc_plugin_python_generic_init (GncPluginpythongeneric *plugin)
{
    fprintf(stderr,"generic init called\n");
    (get_plugin_callbacks())->python_callback_init(plugin);
}

static void
gnc_plugin_python_generic_finalize (GObject *object)
{
    fprintf(stderr,"generic finalize called\n");
    (get_plugin_callbacks())->python_callback_finalize(object);
}

/************************************************************
 *                    Command Callbacks                     *
 ************************************************************/

// this is done in the python plugin module now
