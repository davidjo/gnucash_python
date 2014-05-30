
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

pythonapi.PyCObject_AsVoidPtr.restype = c_void_p
pythonapi.PyCObject_AsVoidPtr.argtypes = [ py_object ]

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
        print "pygobject addr 1",gobject._PyGObject_API
        addr = pythonapi.PyCObject_AsVoidPtr(
            py_object(gobject._PyGObject_API))
        print "pygobject addr %x"%addr
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

libgnc_gnomeutils.gnc_gui_init.argtypes = []



def gnc_gui_init ():

    # well I cant get this to work
    if False:
        main_window_ptr = libgnc_gnomeutils.gnc_gui_init()

        #main_window_adrs = hash(main_window_ptr)

        print >> sys.stderr, "main_window_ptr %x"%main_window_ptr

        #pdb.set_trace()

        # call like this:
        print "pass1"
        Cgobject = PyGObjectCPAI()
        print "pass2"
        main_window = Cgobject.pygobject_new(main_window_ptr)
        print "pass3"

        #pdb.set_trace()

    main_window = gncmainwindow.gnc_gui_init()

    return main_window

