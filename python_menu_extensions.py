
# this is a python object for helping in extending the menus
# it is sort of based on the gnc-menu-extensions but does not use
# the separate gnc-plugin-menu-additions plugin - it is simply
# part of a python plugin module  
# it is a generic class in that could be used with many different
# python plugins where the menu list is not predefined but is
# determined at runtime

import sys

import gtk

import gobject


import pdb


import gnucash_log
from gnucash_log import ENTER



class PythonMenuAdditions(gobject.GObject):

    def __init__ (self, group_name, menu_list):

        #pdb.set_trace()

        super(PythonMenuAdditions,self).__init__()

        # the group_name MUST be different for each python plugin

        self.group_name = group_name
        self.menu_list = menu_list

        self.saved_windows = {}


    def add_to_window (self, window, window_type):

        #pdb.set_trace()

        #if hash(window) in self.saved_windows:
        #    # what to do!!
        #    print "add called more than once same window!!"
        #    pdb.set_trace()
        #    print "add called more than once same window!!"

        per_window = PythonPerWindowMenuAdditions(window, self)

        per_window.add_to_window(window, window_type)

    def remove_from_window (self, window, window_type):

        pdb.set_trace()

        #if hash(window) in self.saved_windows:

        per_window.remove_from_window(window, window_type)


    # can these be done once - or do they need to be done in the  per window??
    # I think so - they are only required to be unique within a given menu
    # the lookup is by the menu path

    def do_preassigned_accel (self, info, table):

        if info.assigned:
            return

        ## need utf8 validation
        #if g_utf8_validate(info.ae.label, -1, None):
        #    info.accel_assigned = True
        #    g_warning("Extension menu label '%s' is not valid utf8.", info->ae.label)
        #    return

        # check for pre-assigned accelerator - that is contains(begins?) _
        ptr = info.ae.label.find('_')
        if ptr < 0:
            return

        accel_key = info.ae.label[ptr+1]
        #DEBUG("Accelerator preassigned: '%s'", accel_key)

        # create python dict for C glib hash table
        if info.path in table:
            map = table[info.path]
        else:
            map = None

        #DEBUG("path '%s', map '%s' -> '%s'", info->path, map, new_map)

        table[info.path] = map + accel_key

        info.accel_assigned = True

    def assign_accel (self, info, table):

        if info.accel_assigned:
            return

        if info.path in table:
            map = table[info.path]
        else:
            map = ""

        #DEBUG("map '%s', path %s", map, info->path)

        found_ptr = ""
        found_buf = ""
        for ptr in info.ae.label:
            if not ptr.isalpha():
                continue
            ptr = ptr.lower()
            found_buf = ptr
            if map.find(ptr) < 0:
                found_ptr = ptr
                break

        if found_ptr == "":
            info.accel_assigned = True
            return

        start = info.ae.label[0:found_ptr]
        new_label = start + '_' + found_ptr

        info.ae.label = new_label

        new_map = map + found_buf

        table[info.path] = new_map

        info.accel_assigned = True



class PythonPerWindowMenuAdditions(gobject.GObject):

    def __init__ (self, window, menu_additions):

        #pdb.set_trace()

        super(PythonPerWindowMenuAdditions,self).__init__()

        self.menu_additions = menu_additions

        self.window = window
        self.merge_id = None


    def add_menu_item (self, ui_manager, group, menuitm):

        # although it says add actions we are actually adding one

        # this is a version of the gnc_menu_additions_menu_setup_one function
        # in gnc-plugin-menu-additions.c

        #DEBUG( "Adding %s/%s [%s] as [%s]", ext_info->path, ext_info->ae.label,
        #       ext_info->ae.name, ext_info->typeStr );

        #print "group",group
        #print "menuitem",menuitm
        #print "menuitem",menuitm.ae.as_tuple()
        #pdb.set_trace()

        group.add_actions([menuitm.ae.as_tuple()],user_data=self.window)

        # so this implements the xml
        # with path giving the menu position
        #   <menuitem name="Python Reports" action="pythonreportsAction"/>
        #print " preui",ui_manager.get_ui()
        #print "add_ui",self.merge_id,menuitm.path,menuitm.name,menuitm.action,menuitm.type
        ui_manager.add_ui(self.merge_id,menuitm.path,menuitm.name,menuitm.action,menuitm.type,False)

        #print "postui",ui_manager.get_ui()
        ui_manager.ensure_update()


    def add_to_window (self, window, window_type):

        print >> sys.stderr, "called add_to_window"
        #pdb.set_trace()

        ui_manager = self.window.get_uimanager()
        group = gtk.ActionGroup(self.menu_additions.group_name)

        window.set_translation_domain(group, "gnucash");

        self.merge_id = ui_manager.new_merge_id()

        ui_manager.insert_action_group(group,0)

        # sort list
        # do accelerators
        # maybe we can do the above earlier

        # then add
        for menuitm in self.menu_additions.menu_list:
            self.add_menu_item(ui_manager,group,menuitm)

        ui_manager.ensure_update()

        # remember this function stores the group and merge_id to remove later
        # when the GncPlugin remove_from_window function is called
        # ah - this does not update any gtk stuff just gnc stuff handling the menu additions
        #gnc_main_window_manual_merge_actions("gnc-plugin-menu-additions-actions",group,self.merge_id)
        self.window.manual_merge_actions(self.menu_additions.group_name,group,self.merge_id)


    def remove_from_window (self, window, window_type):

        print >> sys.stderr, "called remove_from_window"
        pdb.set_trace()
        print >> sys.stderr, "called remove_from_window"

        # weird - I think both this code is done and the super class
        # because the subclass actions are done first in C

        # if we call manual_merge_actions I dont think we need the following

        group = window.get_action_group(self.menu_additions.group_name)

        if group != None:
            window.ui_merge.remove_action_group(group)

        # what I dont understand is the original C code does not attempt
        # to remove the UI for gcn-plugin-menu-additions - but does for
        # any other plugin 
        window.ui_merge.remove_ui(self.merge_id)


        # another miss - in remove window the subclass actions are done first
        # then the superclass
        super(GncPluginPythonMenuAdditions,self).remove_from_window(window, window_type)

