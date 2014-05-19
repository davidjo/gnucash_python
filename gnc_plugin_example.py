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

import gobject


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

libgnc_module.gnc_module_load.argtypes = [c_char_p, gint, gboolean]
libgnc_module.gnc_module_load.restype = GNCModulePointer

libgnc_module.gnc_module_load("gnucash/plugins/example",0)



# well first attempt failed - lets try creating the gnc_plugin type

gncplugintype = gobject.type_from_name('GncPlugin')

# amazing this just worked!!
# we now have the GncPlugin as a type in python
# the problem is there seems to be no python access to the extra functions
# of the gnc-plugin class

pdb.set_trace()

# lets try and create subclass

tmpplugin = gobject.new(gobject.type_from_name('GncPlugin'))

class GncPluginExampleClass(type(tmpplugin)):
    pass

gobject.type_register(GncPluginExampleClass)

tmpexampl = gobject.new(GncPluginExampleClass)


# we need the module functions
# unfortunately I think we cannot do this in pure python
# the gnucash module system seems to rely on specific symbol names
# being available
# - and do not know how to create such symbols in python
