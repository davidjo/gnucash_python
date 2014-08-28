
# ctypes implementation of GncMainWindow


import os

import sys

import gobject

from ctypes import *


import pdb


from gnome_utils_ctypes import libgnc_gnomeutils

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


if True:

    import gncmainwindow

    def gnc_gui_init ():

        # ah - get why this works - because wrapping using codegen
        # registers the python type as the wrapper for the GType
        # so when call pygobject_new with a gobject the GType
        # is looked up and the appropriate python wrapper used

        # note that gnc_gui_init is a special function I added
        # to the wrapper to call the gnome-utils library gnc_gui_init

        main_window = gncmainwindow.gnc_gui_init()

        #pdb.set_trace()

        # why did I add this
        #print >> sys.stderr, "main window call of gnc_gui_init - probably not what you want!!"
        print >> sys.stderr, "main_window_ptr %x"%hash(main_window)

        return main_window


else:

    # call the gnome_utils gnc_gui_init
    # then wrap as appropriate
    # do it this way so dont get circular imports - gnc_gui_init needs
    # the gnc_main_window type and this module needs gnome_utils

    # partial implementation as not used

    import types

    from pygobjectcapi import PyGObjectCAPI


    class GtkUIManagerOpaque(Structure):
        pass

    GtkUiManagerOpaquePtr = POINTER(GtkUIManagerOpaque)

    #libgnc_gnomeutils.gnc_main_window_get_uimanager.argtypes = [ GncMainWindowOpaquePtr ]
    #libgnc_gnomeutils.gnc_main_window_get_uimanager.restype = GtkUiManagerOpaquePtr

    libgnc_gnomeutils.gnc_main_window_get_uimanager.argtypes = [ c_void_p ]
    libgnc_gnomeutils.gnc_main_window_get_uimanager.restype = c_void_p

    def gnc_gui_init ():

        main_window = libgnc_gnomeutils.gnc_gui_init()

        # we now need to add functions to this - mainly get_uimanager

        main_window.get_uimanager = types.MethodType(get_ui_manager, main_window, main_window.__class__)

        return main_window

    def get_uimanager (self):

        mnwndw_ptr = hash(self)

        ui_mgr_ptr = libgnc_gnomeutils.gnc_main_window_get_uimanager(mnwndw_ptr)

        # need to wrap ui_mgr
        Cgobject = PyGObjectCAPI()
        ui_mgr = Cgobject.pygobject_new(ui_mgr_ptr)

        return ui_mgr

