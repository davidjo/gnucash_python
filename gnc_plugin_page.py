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

pdb.set_trace()

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


gncpluginpagetype = gobject.type_from_name('GncPluginPage')


# amazing this just worked!!
# we now have the GncPlugin as a type in python
# the problem is there seems to be no python access to the extra functions
# of the gnc-plugin class



libgnc_gnomeutilnm = find_library("libgncmod-gnome-utils")
if libgnc_gnomeutilnm is None:
    pdb.set_trace()
    raise RuntimeError("Can't find a libgncmod-gnome-utils library to use.")

libgnc_gnomeutils = cdll.LoadLibrary(libgnc_gnomeutilnm)

pdb.set_trace()

# looks as though the main return for gnc_module_load is the GNCLoadedModule structure

class GModule(Structure):
    pass

class GNCModuleInfo(Structure):
    pass

init_func_class = CFUNCTYPE(c_int,c_int)

class GNCLoadedModule(Structure):
    pass
GNCLoadedModule._fields_ = [
                            ('gmodule', POINTER(GModule)),
                            ('filename', gcharp),
                            ('load_count', c_int),
                            ('info', POINTER(GNCModuleInfo)),
                            ('init_func', init_func_class),
                           ]


GNCModulePointer = c_void_p

#libgnc_module.gnc_module_load.argtypes = [c_char_p, gint, gboolean]
#libgnc_module.gnc_module_load.restype = GNCModulePointer

