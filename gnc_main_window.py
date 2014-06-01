
# ctypes implementation of GncMainWindowActionData


import os

import sys

import gobject

import gncmainwindow

import pdb


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


gboolean = c_byte
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

#libgnc_gnomeutilnm = find_library("libgncmod-gnome-utils")
#if libgnc_gnomeutilnm is None:
#    pdb.set_trace()
#    raise RuntimeError("Can't find a libgncmod-gnome-utils library to use.")

libgnc_gnomeutilnm = "/opt/local/lib/gnucash/libgncmod-gnome-utils.dylib"
if not os.path.exists(libgnc_gnomeutilnm):
    pdb.set_trace()
    raise RuntimeError("Can't find a libgncmod-gnome-utils library to use.")

libgnc_gnomeutils = CDLL(libgnc_gnomeutilnm)


libgnc_gnomeutils.gnc_main_window_open_page.argtypes = [ c_void_p, c_void_p ]
libgnc_gnomeutils.gnc_main_window_open_page.restype = None

libgnc_gnomeutils.gnc_main_window_close_page.argtypes = [ c_void_p ]
libgnc_gnomeutils.gnc_main_window_close_page.restype = None


# oh boy - by missing the restype this screws up using the return
# - you get a different integer - ah - because the default return is a c_int
# but a pointer on 64 bit machine is not a c_int - the address gets truncated
# even though the resulting python type is an integer in both cases
libgnc_gnomeutils.gnc_gui_init.argtypes = []
libgnc_gnomeutils.gnc_gui_init.restype = c_void_p


def gnc_gui_init ():

    # OK - this does work if I use the right restype for gnc_gui_init!!
    if True:
        main_window_ptr = libgnc_gnomeutils.gnc_gui_init()

        print >> sys.stderr, "main_window_ptr %x"%main_window_ptr

        #pdb.set_trace()

        # call like this:
        Cgobject = PyGObjectCPAI()
        main_window = Cgobject.pygobject_new(main_window_ptr)

        #pdb.set_trace()

    else:

        main_window = gncmainwindow.gnc_gui_init()

        #pdb.set_trace()

        print >> sys.stderr, "main_window_ptr %x"%hash(main_window)

    return main_window

