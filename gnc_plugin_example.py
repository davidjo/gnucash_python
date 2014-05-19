import sys
import os
import pdb
try:
    import _sw_app_utils
    from gnucash import *
    from _sw_core_utils import gnc_prefs_is_extra_enabled
    import gtk
except Exception, errexc:
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()


from ctypes import *

from gobject import GObject

# try creating a plugin

gchar = c_char
gcharp = POINTER(gchar)
GQuark = c_uint32
gsize = c_uint32
GType = gsize

GCallback = c_void_p

# pigs there is no good way to do this
# to use the GncPlugin functions in python via ctypes
# we need to know the exact lengths of the GObject structures


class GtkActionEntry(Structure):
    pass
GtkActionEntry._fields_ = [
                           ('name', gcharp),
                           ('stock_id', gcharp),
                           ('label', gcharp),
                           ('accelerator', gcharp),
                           ('tooltip', gcharp),
                           ('callback', GCallback),
                          ]

class GtkToggleActionEntry(Structure):
    pass

class GtkMainWindow(Structure):
    pass


class GncPlugin(Structure):
    pass
GncPlugin._fields_ = [
                       ('gobject', GObject),
                     ]


plugincb = CFUNCTYPE(None,POINTER(GncPlugin),POINTER(GncMainWindow),GQuark)

class GncPluginClass(Structure):
    pass
GncPluginClass._fields_ = [
                           ('gobject', GncPlugin),
                           ('plugin_name', gcharp),
                           ('actions_name', gcharp),
                           ('actions', POINTER(GtkActionEntry)),
                           ('n_actions', guint),
                           ('toggle_actions', POINTER(GTkToggleActionEntry)),
                           ('n_toogle_actions', guint),
                           ('important_actions', POINTER(gcharp)),
                           ('ui_filename', gcharp),
                           # should this be pointer or not??
                           # punt for the moment
                           ('add_to_window', c_void_p), # this is plugincb type
                           ('remove_to_window', c_void_p), # this is plugincb type
                          ]

class GncPluginExample(Structure):
    pass
GncPluginExample._fields_ = [
                             ('gnc_plugin', GncPlugin),
                            ]

class GncPluginExampleClass(Structure):
    pass
GncPluginExampleClass._fields_ = [
                                  ('gnc_plugin', GncPluginClass),
                                 ]

gnc_plugin_callback = CFUNCTYPE(None,POINTER(GtkAction),POINTER(GncMainWindowActionData))

gnc_plugin_example_cmd_test_cb = gnc_plugin_callback(gnc_plugin_example_cmd_test)

gnc_plugin_actions = [ \
      [ "exampleAction", None, "example description...", None, "example tooltip", gnc_plugin_example_cmd_test_cb ],
                     ]

gnc_plugin_n_actions = len(gnc_plugin_actions)


def gnc_plugin_example_get_type():
    return "gnc-plugin-example"

def gnc_plugin_example_new():
    return GncPluginExample()

def gnc_plugin_example_class_init(gncpluginclass):
    object_class = gncpluginclass
    plugin_class = gncpluginclass

    object_class.finalize = gnc_plugin_example_finalize

    plugin_class.plugin_name = "gnc-plugin-example"

    plugin_class.actions_name = "gnc-plugin-example-actions"
    plugin_class.actions = gnc_plugin_actions
    plugin_class.n_actions = gnc_plugin_n_actions
    plugin_class.ui_filename = "gnc-plugin-example-ui.xml"
    

def gnc_plugin_example_create_plugin():
    pass

def gnc_plugin_example_init(plugin):
    pass

def gnc_plugin_example_finalize(gobject):
    pass

def gnc_plugin_example_cmd_test(action, data):
    pass

