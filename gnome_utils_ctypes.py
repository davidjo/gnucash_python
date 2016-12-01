
# ctypes implementation for access to gnome-utils


import os

import sys

from gi.repository import GObject


import pdb


from ctypes.util import find_library
from ctypes import *


from pygobjectcapi import PyGObjectCAPI


import gnucash_log


# junkily define this for the moment
# define a function equivalent to N_ for internationalization
def N_(msg):
    return msg


#gboolean = c_byte
gboolean = c_int
gpointer = c_void_p
guint = c_uint
gsize = c_uint

GType = gsize

time64 = c_ulonglong


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


# Im undecided how to partition these calls as gnome-utils has calls for a lot
# of different objects
# for the moment Im going to move the call definitions into the python
# ctypes module for an object
# only generic calls will be done here


libgnc_gnomeutils.gnc_shutdown.argtypes = [ c_int ]
libgnc_gnomeutils.gnc_shutdown.restype = None

# oh boy - by missing the restype this screws up using the return
# - you get a different integer - ah - because the default return is a c_int
# but a pointer on 64 bit machine is not a c_int - the address gets truncated
# even though the resulting python type is an integer in both cases
libgnc_gnomeutils.gnc_gui_init.argtypes = []
libgnc_gnomeutils.gnc_gui_init.restype = c_void_p


# do not use this - use the function in gnc_main_window

def gnc_gui_init ():

    # OK - this does work if I use the right restype for gnc_gui_init!!
    # note that the gnc_gui_init just returns main window object pointer
    # if already called - we assume gnc_gui_init has already been called here
    main_window_ptr = libgnc_gnomeutils.gnc_gui_init()

    gnucash_log.dbglog_err("gnc_gui_init: main_window_ptr %x"%main_window_ptr)

    #pdb.set_trace()

    # now understand what the problem is
    # although the following converts the GType to a python gobject
    # it ONLY covers the GType data - it does NOT appear to apply the functions
    # that is a GType class consists of data and functions
    # (this is because we need to register a python object type to be associated
    # with a GType via pygobject C function pygobject_register_class)
    # using pygobject_new wraps the data but not the functions - as they are
    # defined as simple C functions
    # to add the functions to the python gobject looks like we need to define
    # new python functions which call the underlying C functions from the library
    # using ctypes

    # call like this:
    Cgobject = PyGObjectCAPI()
    main_window = Cgobject.pygobject_new(main_window_ptr)

    pdb.set_trace()

    return main_window


libgnc_gnomeutils.gnc_window_set_progressbar_window.argtypes = [ c_void_p ]
libgnc_gnomeutils.gnc_window_set_progressbar_window.restype = None

libgnc_gnomeutils.gnc_window_get_progressbar_window.argtypes = []
libgnc_gnomeutils.gnc_window_get_progressbar_window.restype = c_void_p

libgnc_gnomeutils.gnc_window_show_progress.argtypes = [ c_char_p, c_double ]
libgnc_gnomeutils.gnc_window_show_progress.restype = None



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

libgnc_gnomeutils.gnc_tree_view_account_get_selected_account.argtypes = [ c_void_p ]
libgnc_gnomeutils.gnc_tree_view_account_get_selected_account.restype = c_void_p


libgnc_gnomeutils.gnc_tree_view_account_new_with_root.argtypes = [ c_void_p, c_bool ]
libgnc_gnomeutils.gnc_tree_view_account_new_with_root.restype = c_void_p

libgnc_gnomeutils.gnc_tree_view_account_new.argtypes = [ c_bool ]
libgnc_gnomeutils.gnc_tree_view_account_new.restype = c_void_p



libgnc_gnomeutils.gnc_tree_model_account_types_new.argtypes = [ c_uint ]
libgnc_gnomeutils.gnc_tree_model_account_types_new.restype = c_void_p

libgnc_gnomeutils.gnc_tree_model_account_types_filter_using_mask.argtypes = [ c_uint ]
libgnc_gnomeutils.gnc_tree_model_account_types_filter_using_mask.restype = c_void_p

libgnc_gnomeutils.gnc_tree_model_account_types_set_mask.argtypes = [ c_void_p, c_uint ]
libgnc_gnomeutils.gnc_tree_model_account_types_set_mask.restype = None

libgnc_gnomeutils.gnc_tree_model_account_types_get_mask.argtypes = [ c_void_p ]
libgnc_gnomeutils.gnc_tree_model_account_types_get_mask.restype = c_uint

libgnc_gnomeutils.gnc_tree_model_account_types_get_selection.argtypes = [ c_void_p ]
libgnc_gnomeutils.gnc_tree_model_account_types_get_selection.restype = c_uint

libgnc_gnomeutils.gnc_tree_model_account_types_get_selection_single.argtypes = [ c_void_p ]
libgnc_gnomeutils.gnc_tree_model_account_types_get_selection_single.restype = c_uint

libgnc_gnomeutils.gnc_tree_model_account_types_set_selection.argtypes = [ c_void_p, c_uint ]
libgnc_gnomeutils.gnc_tree_model_account_types_set_selection.restype = None



libgnc_gnomeutils.gnc_date_edit_get_type.argtypes = []
libgnc_gnomeutils.gnc_date_edit_get_type.restype = GType

libgnc_gnomeutils.gnc_date_edit_new.argtypes = [ time64, c_int, c_int ]
libgnc_gnomeutils.gnc_date_edit_new.restype = c_void_p


libgnc_gnomeutils.gnc_handle_date_accelerator.argtypes = [ c_void_p, c_void_p, c_char_p ]
libgnc_gnomeutils.gnc_handle_date_accelerator.restype = c_bool


libgnc_gnomeutils.gnc_ui_get_toplevel.argtypes = []
libgnc_gnomeutils.gnc_ui_get_toplevel.restype = c_void_p


# this definition needs to be here as otherwise get circular definitions
# if in gnc_main_window.py

def ui_get_toplevel ():

    #global Cgobject

    ui_top_ptr = libgnc_gnomeutils.gnc_ui_get_toplevel()

    if ui_top_ptr != None:
        # need to wrap returned gtk widget
        Cgobject = PyGObjectCAPI()
        ui_toplevel = Cgobject.pygobject_new(ui_top_ptr)
    else:
        ui_toplevel = None

    return ui_toplevel


# unfortunately gnc_error_dialog uses variable argument lists
# for the moment lets reimplement in python - its pretty trivial
# this does mean need to import Gtk here
# also just pass string



from gi.repository import Gtk


def gnc_error_dialog (parent, errmsg):

    if parent == None:
        parent = ui_get_toplevel()

    dialog = Gtk.MessageDialog(parent,Gtk.DialogFlags.DIALOG_MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.ERROR,Gtk.ButtonsType.CLOSE,N_(errmsg))

    if parent == None:
        dialog.set_skip_taskbar_hint(False)

    dialog.show()

    dialog.destroy()


def gnc_verify_dialog (parent, yes_is_default, errmsg):

    if parent == None:
        parent = ui_get_toplevel()

    dialog = Gtk.MessageDialog(parent,Gtk.DialogFlags.MODAL|Gtk.FialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.QUESTION,Gtk.ButtonsType.YES_NO,N_(errmsg))

    if parent == None:
        dialog.set_skip_taskbar_hint(False)

    dialog.set_default_response(Gtk.ResponseType.YES if yes_is_default else Gtk.ResponseType.NO)

    result = dialog.run()

    dialog.destroy()

    return result == Gtk.ResponseType.YES

