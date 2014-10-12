
# ctypes implementation of GncMainWindow


import os

import sys

import gobject

from ctypes import *


import pdb

import gnucash_log

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


if False:

    # use swig wrapped functions (with a little ctypes)

    import gnome_utils

    import swighelpers

    def gnc_gui_init ():

        pdb.set_trace()

        main_window_ptr = libgnc_gnomeutils.gnc_gui_init()

        main_window_inst = swighelpers.int_to_swig(main_window_ptr,"_p_GncMainWindow")
        main_window = gnome_utils.GncMainWindow(instance=main_window_inst)

        #pdb.set_trace()

        return main_window

elif False:

    # use pygobject wrapped functions

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
        #gnucash_log.dbglog_err("main window call of gnc_gui_init - probably not what you want!!")
        gnucash_log.dbglog_err("gnc_gui_init: main_window_ptr %x"%hash(main_window))

        return main_window


else:

    # use pygobject and ctypes access to gnc_main_window

    # call the gnome_utils gnc_gui_init
    # then wrap as appropriate
    # do it this way so dont get circular imports - gnc_gui_init needs
    # the gnc_main_window type and this module needs gnome_utils

    import types

    from pygobjectcapi import PyGObjectCAPI


    class GtkUIManagerOpaque(Structure):
        pass

    GtkUiManagerOpaquePtr = POINTER(GtkUIManagerOpaque)

    #libgnc_gnomeutils.gnc_main_window_get_uimanager.argtypes = [ GncMainWindowOpaquePtr ]
    #libgnc_gnomeutils.gnc_main_window_get_uimanager.restype = GtkUiManagerOpaquePtr

    libgnc_gnomeutils.gnc_main_window_get_uimanager.argtypes = [ c_void_p ]
    libgnc_gnomeutils.gnc_main_window_get_uimanager.restype = c_void_p

    libgnc_gnomeutils.gnc_main_window_manual_merge_actions.argtypes = [ c_void_p, c_char_p, c_void_p, guint ]
    libgnc_gnomeutils.gnc_main_window_manual_merge_actions.restype = None

    Cgobject = PyGObjectCAPI()

    def gnc_gui_init ():

        global Cgobject

        #pdb.set_trace()

        main_window_ptr = libgnc_gnomeutils.gnc_gui_init()
        gnucash_log.dbglog_err("main_window_ptr %x"%main_window_ptr)

        # call like this:
        #Cgobject = PyGObjectCAPI()
        main_window = Cgobject.pygobject_new(main_window_ptr)

        gnucash_log.dbglog_err("main_window ",main_window)

        # we now need to add functions to the GncMainWindow object - mainly get_uimanager
        # using PyGObject/GTypes just gets storage - does not associate the functions with an object

        main_window.get_uimanager = types.MethodType(get_uimanager, main_window, main_window.__class__)

        main_window.manual_merge_actions = types.MethodType(manual_merge_actions, main_window, main_window.__class__)

        return main_window

    def get_uimanager (self):

        global Cgobject

        mnwndw_ptr = hash(self)

        ui_mgr_ptr = libgnc_gnomeutils.gnc_main_window_get_uimanager(mnwndw_ptr)

        # need to wrap ui_mgr
        #Cgobject = PyGObjectCAPI()
        ui_mgr = Cgobject.pygobject_new(ui_mgr_ptr)

        return ui_mgr

    def manual_merge_actions (self, group_name, group, merge_id):

        #pdb.set_trace()

        mnwndw_ptr = hash(self)

        group_ptr = hash(group)

        libgnc_gnomeutils.gnc_main_window_manual_merge_actions(mnwndw_ptr, group_name, group_ptr, merge_id)

