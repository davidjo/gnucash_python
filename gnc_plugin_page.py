import sys
import os
import pdb

print >> sys.stderr, "trying plugin page"

try:
    #import _sw_app_utils
    #from gnucash import *
    #from _sw_core_utils import gnc_prefs_is_extra_enabled
    #import gtk
    pass
except Exception, errexc:
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

print >> sys.stderr, "trying plugin page"

from ctypes import *

import gobject


from ctypes.util import find_library



gchar = c_char
gint = c_int
gboolean = gint
gcharp = POINTER(gchar)
GQuark = c_uint32
gsize = c_uint32
GType = gsize

GCallback = c_void_p


# attempt access to the gnc-plugin-page plugin

# amazing this just worked!!
# we now have the GncPlugin as a type in python
# the problem is there seems to be no python access to the extra functions
# of the gnc-plugin class

# so GncPluginPage has no SCM stuff
# but the question is still how to use such types in python
# so far I think we can get the type but all functions associated with it
# are not in the type object and also dont know how to get to the private data
# in python

# it appears the basic GObject address is given by the hash of the python object

# looks as though the only way to use subclassed GObject entities
# is to create a python class which calls the functions via eg ctypes
# or swig or an extension module

# NOTA BENE - a GncPluginPage is NOT a subclass of GncPlugin!!


gncpluginpagetype = gobject.type_from_name('GncPluginPage')

gncpluginpagereporttype = gobject.type_from_name('GncPluginPageReport')


# this lists the properties
print >> sys.stderr, gobject.list_properties(gncpluginpagetype)

# this lists the signal names
print >> sys.stderr, gobject.signal_list_names(gncpluginpagetype)


# can we create a new page
#pdb.set_trace()

#newpage = gobject.new(gncpluginpagetype)


import gncpluginpage

from pygkeyfile import GKeyFile


#pdb.set_trace()


#libgnc_gnomeutilnm = find_library("libgncmod-gnome-utils")
#if libgnc_gnomeutilnm is None:
#    pdb.set_trace()
#    raise RuntimeError("Can't find a libgncmod-gnome-utils library to use.")

libgnc_gnomeutilnm = "/opt/local/lib/gnucash/libgncmod-gnome-utils.dylib"
if not os.path.exists(libgnc_gnomeutilnm):
    pdb.set_trace()
    raise RuntimeError("Can't find a libgncmod-gnome-utils library to use.")

libgnc_gnomeutils = CDLL(libgnc_gnomeutilnm)


class GncMainWindowOpaque(Structure):
    pass

class GncPluginPageOpaque(Structure):
    pass


libgnc_gnomeutils.gnc_main_window_open_page.argtypes = [ c_void_p, c_void_p ]
libgnc_gnomeutils.gnc_main_window_open_page.restype = None


libgnc_apputilnm = "/opt/local/lib/gnucash/libgncmod-app-utils.dylib"
if not os.path.exists(libgnc_apputilnm):
    pdb.set_trace()
    raise RuntimeError("Can't find a libgncmod-app-utils library to use.")

libgnc_apputils = CDLL(libgnc_apputilnm)

#libgnc_apputils.gnc_register_gui_component("window-report", None, close_handler, self)
libgnc_apputils.gnc_register_gui_component.argtypes = [ c_char_p, c_void_p, c_void_p, c_void_p ]
libgnc_apputils.gnc_register_gui_component.restype = c_int

libgnc_apputils.gnc_get_current_session.argtypes = []
libgnc_apputils.gnc_get_current_session.restype = c_void_p

libgnc_apputils.gnc_unregister_gui_component.argtypes = [ c_int ]
libgnc_apputils.gnc_unregister_gui_component.restype = None

libgnc_apputils.gnc_unregister_gui_component_by_data.argtypes = [ c_char_p, c_void_p ]
libgnc_apputils.gnc_unregister_gui_component_by_data.restype = None


#pdb.set_trace()

# OK attempt to create a Python class for gnc_plugin_page
# we will use a helper module to do the 
#import pythonpage


#tmpplugin = gobject.new(gobject.type_from_name('GncPlugin'))

#class GncPluginExampleClass(type(tmpplugin)):
#    pass

#gobject.type_register(GncPluginExampleClass)

#tmpexampl = gobject.new(GncPluginExampleClass)

