
# ctypes implementation of GncMainWindow


import os

import sys

import gobject

from ctypes import *

try:
    #import _sw_app_utils
    #from gnucash import *
    #from _sw_core_utils import gnc_prefs_is_extra_enabled
    import gtk
    pass
except Exception, errexc:
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()


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

    libgnc_gnomeutils.gnc_main_window_get_action_group.argtypes = [ c_void_p, c_char_p ]
    libgnc_gnomeutils.gnc_main_window_get_action_group.restype = c_void_p

    libgnc_gnomeutils.gnc_gtk_action_group_set_translation_domain.argtypes = [ c_void_p, c_char_p ]
    libgnc_gnomeutils.gnc_gtk_action_group_set_translation_domain.restype = None

    Cgobject = PyGObjectCAPI()


    def gnc_gui_init ():

        global Cgobject

        #pdb.set_trace()

        main_window_ptr = libgnc_gnomeutils.gnc_gui_init()
        gnucash_log.dbglog_err("main_window_ptr %x"%main_window_ptr)

        # call like this:
        #Cgobject = PyGObjectCAPI()
        main_window = Cgobject.pygobject_new(main_window_ptr)

        return main_window_wrap(main_window)


    def main_window_wrap (main_window):

        #pdb.set_trace()

        # this argument must be a GObject wrapped gtk.Window

        gnucash_log.dbglog_err("main_window ",main_window)

        # we now need to add functions to the GncMainWindow object - mainly get_uimanager
        # using PyGObject/GTypes just gets storage - does not associate the functions with an object

        main_window.get_uimanager = types.MethodType(get_uimanager, main_window, main_window.__class__)

        main_window.manual_merge_actions = types.MethodType(manual_merge_actions, main_window, main_window.__class__)

        main_window.merge_actions = types.MethodType(merge_actions, main_window, main_window.__class__)

        main_window.unmerge_actions = types.MethodType(unmerge_actions, main_window, main_window.__class__)

        main_window.set_translation_domain = types.MethodType(set_translation_domain, main_window, main_window.__class__)

        main_window.get_action_group = types.MethodType(get_action_group, main_window, main_window.__class__)

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

        # the only thing this does in C is add the group_name and merge_id as an entry structure
        # to the merged_actions_table
        # which on unload of a main window will remove the action_group and ui updates
        # automatically

        mnwndw_ptr = hash(self)

        group_ptr = hash(group)

        libgnc_gnomeutils.gnc_main_window_manual_merge_actions(mnwndw_ptr, group_name, group_ptr, merge_id)

    def set_translation_domain (self, group, domain_name):

        #pdb.set_trace()

        group_ptr = hash(group)

        libgnc_gnomeutils.gnc_gtk_action_group_set_translation_domain(group_ptr, domain_name)

    def get_action_group (self, group_name):

        #pdb.set_trace()

        mnwndw_ptr = hash(self)

        group_ptr = libgnc_gnomeutils.gnc_main_window_get_action_group(mnwndw_ptr, group_name)

        # need to wrap group
        #Cgobject = PyGObjectCAPI()
        group = Cgobject.pygobject_new(group_ptr)

        return group



    def merge_actions (self, group_name, actions, toggle_actions, ui_xml_str, user_data):

        #pdb.set_trace()

        # self is a GObject wrapped gtk.Window runthrough main_window_wrap

        # this is a re-implementation of gnc_main_window_merge_actions - because
        # rather than calling the gnucash version its easier to call the gtk functions
        # directly - saves converting the input data

        # passing the ui_xml_str as a string and use directly
        # this code moved to external code
        # assuming pass full path directly for the moment
        #pathname = gnc_main_window.gnc_filepath_locate_ui_file(filename)

        # this is based on the code in python_only_plugin

        # yes - we now can add menu items in python
        # we simply need the main window object wrapped either using
        # a gncmainwindow module or ctypes and pygobject_new from gobject module
        # (ctypes works now got right argument and return types)
        # currently using ctypes version
        # we apparently have to use the main window ui_merge object

        main_ui_merge = self.get_uimanager()

        merge_id = 0

        #accelgroup = main_ui_merge.get_accel_group()
        #self.add_accel_group(accelgroup)


        # Create an ActionGroup
        actiongroup = gtk.ActionGroup(group_name)
        #self.actiongroup = actiongroup

        # call the gnucash function - domain is a string
        # or direct call of gtk_action_group_set_translate_func??
        # domain is GETTEXT_PACKAGE which appears to be the name "gnucash"
        self.set_translation_domain(actiongroup, "gnucash")

        print "actions",actions


        #actiongroup.add_actions([ 
        #    ("PythonReportsAction", None, "Python Reports...", None, "python reports tooltip", None),
        #    ("PythonToolsAction", None, "Python Tools...", None, "python tools tooltip", None),
        #    ("pythongenericAction", None, "Python tools description...", None, "python tools tooltip", self.tools_cb),
        #         ], user_data=self.main_window)

        #    #("pythonreportsAction", None, "Python reports description...", None, "python reports tooltip", self.reports_cb),
        #    #("pythongenericAction", None, "Python tools description...", None, "python tools tooltip", self.tools_cb),
        #    #     ], user_data=self.main_window)

        actiongroup.add_actions(actions,user_data=user_data)

        main_ui_merge.insert_action_group(actiongroup,0)

        merge_id = main_ui_merge.add_ui_from_string(ui_xml_str)

        if merge_id != None:

             main_ui_merge.ensure_update()

             # merge_actions essentially does the same code as this function - so just call it!!
             # wait a bit we have decided not to call this - if we do then we need to remove
             # entry it creates
             # - we are returning the actiongroup and merge_id for saving externally
             #self.manual_merge_actions(group_name, actiongroup, merge_id)

        gnucash_log.dbglog("merge_id",merge_id)

        # in the gnucash code the groupname and merge_id are stored in an entry structure
        # stored in a merged_actions_table
        # so far looks as though this is merely used to remove these actions
        # - so return them to be saved somewhere in gnucash

        return (actiongroup, merge_id)


    def unmerge_actions (self, group_name, actiongroup, merge_id):

        # self is a GObject wrapped gtk.Window runthrough main_window_wrap
        #pdb.set_trace()

        # this is a re-implementation of gnc_main_window_unmerge_actions
        # except here we pass the actiongroup and merge_id rather than looking it up

        main_ui_merge = self.get_uimanager()

        main_ui_merge.remove_action_group(actiongroup)

        main_ui_merge.remove_ui(merge_id)

        main_ui_merge.ensure_update()

