import sys
import os
import pdb
try:
    #import _sw_app_utils
    #from gnucash import *
    #from _sw_core_utils import gnc_prefs_is_extra_enabled
    #import gtk
    pass
except Exception, errexc:
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()


from ctypes import *

#import gobject


from ctypes.util import find_library


# we need access to the module load function

gchar = c_char
gint = c_int
gboolean = gint
gcharp = POINTER(gchar)
GQuark = c_uint32
gsize = c_uint32
GType = gsize

GCallback = c_void_p


libgnc_modulenm = find_library("libgnc-module")
if libgnc_modulenm is None:
    raise RuntimeError("Can't find a libgnc-module library to use.")

libgnc_module = cdll.LoadLibrary(libgnc_modulenm)

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

libgnc_module.gnc_module_load.argtypes = [c_char_p, gint]
libgnc_module.gnc_module_load.restype = GNCModulePointer

# we have a problem - if we get some form of error message while doing this
# we crash because the g_log function seems to point to a python error function
# which crashes for some reason
# however doing this early (possibly before importing gtk etc) seems to solve the problem

retvl = libgnc_module.gnc_module_load("gnucash/plugins/python_generic",0)

print >> sys.stderr, "loaded module from python!!",retvl

pdb.set_trace()
