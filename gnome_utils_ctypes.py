
# ctypes implementation for access to gnome-utils


import os

import sys

import gobject

import gncmainwindow

import pdb


from ctypes.util import find_library
from ctypes import *


# this is taken from pygtk FAQ 23.41

# this boilerplate can convert a memory address
# into a proper python gobject.

# this fixup is needed as the apparent return type for PyCObject_AsVoidPtr
# is c_int!!

pythonapi.PyCObject_AsVoidPtr.argtypes = [ py_object ]
pythonapi.PyCObject_AsVoidPtr.restype = c_void_p

class _PyGObject_Functions(Structure):
    _fields_ = [
        ('register_class',
         PYFUNCTYPE(c_void_p, c_char_p,
                           c_int, py_object,
                           py_object)),
        ('register_wrapper',
         PYFUNCTYPE(c_void_p, py_object)),
        ('register_sinkfunc',
         PYFUNCTYPE(py_object, c_void_p)),
        ('lookupclass',
         PYFUNCTYPE(py_object, c_int)),
        ('newgobj',
         PYFUNCTYPE(py_object, c_void_p)),
        ]
    
class PyGObjectCPAI(object):
    def __init__(self):
        #print "pygobject addr 1",gobject._PyGObject_API
        addr = pythonapi.PyCObject_AsVoidPtr(
            py_object(gobject._PyGObject_API))
        #print "pygobject addr %x"%addr
        self._api = _PyGObject_Functions.from_address(addr)

    def pygobject_new(self, addr):
        return self._api.newgobj(addr)


# call like this:
# Cgobject = PyGObjectCPAI()
# Cgobject.pygobject_new(memory_address)

# to get memory address from a gobject:
#  address = hash(obj)


#gboolean = c_byte
gboolean = c_int
gpointer = c_void_p
guint = c_uint
gsize = c_uint


class GncMainWindowOpaque(Structure):
    pass

GncMainWindowOpaquePtr = POINTER(GncMainWindowOpaque)

class GncPluginPageOpaque(Structure):
    pass

class GncMainWindowActionData(Structure):
    pass
GncMainWindowActionData._fields_ = [
                                    ('window', POINTER(GncMainWindowOpaque)),
                                    ('data', gpointer),
                                   ]


# find core-utils then add gnucash to path to get to gnome-utuils

libgnccorenm = find_library("libgnc-core-utils")
if libgnccorenm is None:
    raise RuntimeError("Can't find a libgnc-core-utils library to use.")

libpth = os.path.dirname(libgnccorenm)

libgnc_gnomeutilnm = os.path.join(libpth,"gnucash","libgncmod-gnome-utils.dylib")
if not os.path.exists(libgnc_gnomeutilnm):
    pdb.set_trace()
    raise RuntimeError("Can't find a libgncmod-gnome-utils library to use.")

libgnc_gnomeutils = CDLL(libgnc_gnomeutilnm)



libgnc_gnomeutils.gnc_main_window_open_page.argtypes = [ c_void_p, c_void_p ]
libgnc_gnomeutils.gnc_main_window_open_page.restype = None

libgnc_gnomeutils.gnc_main_window_close_page.argtypes = [ c_void_p ]
libgnc_gnomeutils.gnc_main_window_close_page.restype = None


libgnc_gnomeutils.gnc_shutdown.argtypes = [ c_int ]
libgnc_gnomeutils.gnc_shutdown.restype = None

# oh boy - by missing the restype this screws up using the return
# - you get a different integer - ah - because the default return is a c_int
# but a pointer on 64 bit machine is not a c_int - the address gets truncated
# even though the resulting python type is an integer in both cases
libgnc_gnomeutils.gnc_gui_init.argtypes = []
libgnc_gnomeutils.gnc_gui_init.restype = c_void_p



libgnc_gnomeutils.gnc_tree_view_account_get_view_info.argtypes = [ c_void_p, c_void_p ]
libgnc_gnomeutils.gnc_tree_view_account_get_view_info.restype = c_void_p

libgnc_gnomeutils.gnc_tree_view_account_set_view_info.argtypes = [ c_void_p, c_void_p ]
libgnc_gnomeutils.gnc_tree_view_account_set_view_info.restype = None

libgnc_gnomeutils.gnc_tree_view_account_get_cursor_account.argtypes = [ c_void_p ]
libgnc_gnomeutils.gnc_tree_view_account_get_cursor_account.restype = c_void_p

libgnc_gnomeutils.gnc_tree_view_account_select_subaccounts.argtypes = [ c_void_p, c_void_p ]
libgnc_gnomeutils.gnc_tree_view_account_select_subaccounts.restype = None

libgnc_gnomeutils.gnc_tree_view_account_set_selected_accounts.argtypes = [ c_void_p, c_void_p ]
libgnc_gnomeutils.gnc_tree_view_account_set_selected_accounts.restype = None

libgnc_gnomeutils.gnc_tree_view_account_get_selected_accounts.argtypes = [ c_void_p ]
libgnc_gnomeutils.gnc_tree_view_account_get_selected_accounts.restype = c_void_p


libgnc_gnomeutils.gnc_tree_view_account_new_with_root.argtypes = [ c_void_p, c_bool ]
libgnc_gnomeutils.gnc_tree_view_account_new_with_root.restype = c_void_p

libgnc_gnomeutils.gnc_tree_view_account_new.argtypes = [ c_bool ]
libgnc_gnomeutils.gnc_tree_view_account_new.restype = c_void_p


