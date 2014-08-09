
# ctypes implementation of GncMainWindow


import os

import sys

import gobject

from ctypes import *


import pdb


from gnome_utils_ctypes import libgnc_gnomeutils

import gncmainwindow

from pygobjectcapi import PyGObjectCAPI

# call like this:
# Cgobject = PyGObjectCAPI()
# Cgobject.pygobject_new(memory_address)

# to get memory address from a gobject:
#  address = hash(obj)


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

libgnc_gnomeutils.gnc_main_window_open_page.argtypes = [ c_void_p, c_void_p ]
libgnc_gnomeutils.gnc_main_window_open_page.restype = None

libgnc_gnomeutils.gnc_main_window_close_page.argtypes = [ c_void_p ]
libgnc_gnomeutils.gnc_main_window_close_page.restype = None


def gnc_gui_init ():

    main_window = gncmainwindow.gnc_gui_init()

    #pdb.set_trace()

    print >> sys.stderr, "main window call of gnc_gui_init - probably not what you want!!"
    print >> sys.stderr, "main_window_ptr %x"%hash(main_window)

    return main_window

