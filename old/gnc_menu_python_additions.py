

from gi.repository import Gtk

import pdb


import gnucash_log
from gnucash_log import ENTER


import gnc_plugin

from gnc_plugin import GncPluginPython



# gnucash has another GncPlugin, GncPluginMenuAdditions (gnc-plugin-menu-additions)
# which is used to load menu additions - mainly for the scheme reports
# where the number of items (reports) changes and the menu callback
# executed runs scheme code

# we cannot use the gnc-menu-extensions and gnc-plugin-menu-additions
# as they are tied to scheme - because gnc-plugin-menu-additions gets its
# list from gnc-menu-extensions which is totally tied to scheme

# what we can do is create a new plugin in python that will load
# menu items from python list and execute python code in the menu
# callback



class GncPluginPythonMenuAdditions(GncPluginPython):

    # ah - this is something I think Ive missed - we can name the GType here
    __gtype_name__ = 'GncPluginPythonMenuAdditions'

    # add properties/signals here
    #__gproperties__ =

    # I think these are more consistent if they are class variables
    # unfortunately cant figure out how to have a method of the class
    # in a class variable

    # the analysis is that essentially in gnucash plugins are single
    # instance classes

    # local class to save the per window data
    class GncPluginMenuAdditionsPerWindow(object):

        def __init__ (self, window=None):
            self.window = window
            self.ui_manager = None
            self.group = None
            self.merge_id = None


    def __init__ (self):

        #pdb.set_trace()

        super(GncPluginPythonMenuAdditions,self).__init__()
        #GncPluginPython.__init__(self)

        self.class_init()


    def class_init (self):

        super(GncPluginPythonMenuAdditions,self).class_init()

        #self.plugin_name = "gnc-plugin-menu-additions"
        self.plugin_name = "GncPluginPythonMenuAdditions"

        # NOTA BENE - we do NOT set actions_name for this plugin
        # this disables the base class actions in add_to_window/remove_from_window
        #self.actions_name = "gnc-plugin-menu-additions-actions"
        #self.actions_name = "GncPluginPythonMenuAdditionsActions"

        self.set_class_init_data(plugin_name=self.plugin_name)

        self.set_callbacks()


    # note that in the C the primary version of these functions are defined in
    # gnc-plugin.c - and at the end of their code they call the functions saved
    # in the GncPlugin class private data - if they are defined
    # in python this gets sort of inverted - we define functions here to call
    # the parent GncPluginPython class version of these functions - before doing
    # extra work - and the GncPluginPython version of these functions does not
    # call functions of the subclass (how could it)

    def add_to_window (self, window, window_type):

        print("called add_to_window", file=sys.stderr)

        super(GncPluginPythonMenuAdditions,self).add_to_window(window, window_type)

        pdb.set_trace()

        # missed that - the per_window is only needed to pass the structure members
        # to the setup_one function

        per_window = GncPluginMenuAdditionsPerWindow(window)
        per_window.ui_manager = window.ui_merge
        per_window.group = Gtk.ActionGroup('PythonMenuAdditions')
        per_window.window.set_translation_domain(per_window.group, "gnucash")
        per_window.merge_id = window.ui_merge.new_merge_id()
        window.ui_merge.insert_action_group(per_window.group, 0);

        menu_list = sorted(gnc_extensions_get_menu_list())

        # assign accelerators
        # use python dict for hash table
        table = {}

        for menuitm in menu_list:
            self.do_preassigned_accel(menuitm, table)

        for menuitm in menu_list:
            self.assign_accel(menuitm, table)

        # add to window
        for menuitm in menu_list:
            self.menu_setup_one(menuitm, per_window)

        # I dont know why this is being done
        # - because I dont see it being removed as the actions_name is not set in the
        # base GncPlugin class - which is what leads to the call to
        # gnc_main_window_unmerge_actions which removes this addition
        #  the difference seems to be gnc_main_window_unmerge_actions removes both the
        # action group and the ui whereas this classes remove_from_window just removes
        # the action group - why??
        # yes - stepping through with gdb shows there is no call to gnc_main_window_unmerge_actions
        # for the menu additions plugin on window removal
        # but there is a call to gnc_main_window_manual_merge_actions when
        # gnc_plugin_menu_additions_add_to_window is called
        window.manual_merge_actions("GncPluginPythonMenuAdditionsActions",per_window.group, per_window.merge_id)


    def remove_from_window (self, window, window_type):

        print("called remove_from_window", file=sys.stderr)
        pdb.set_trace()
        print("called remove_from_window", file=sys.stderr)

        # need to map the window somehow to a window object
        window = gnc_main_window.main_window_wrap(window)

        # weird - I think both this code is done and the super class
        # because the subclass actions are done first in C

        group = window.get_action_group("GncPluginPythonMenuAdditionsActions")

        if group != None:
            window.ui_merge.remove_action_group(group)

        # another miss - in remove window the subclass actions are done first
        # then the superclass

        super(GncPluginPythonMenuAdditions,self).remove_from_window(window, window_type)


    def setup_one (self, ext_info, per_window):

        #DEBUG( "Adding %s/%s [%s] as [%s]", ext_info->path, ext_info->ae.label,
        #       ext_info->ae.name, ext_info->typeStr );

        pdb.set_trace()

        cb_data = GncMainWindowActionData()

        cb_data.window = per_window.window
        cb_data.data = ext_info.extension

        if ext_info.type == Gtk.UIManagerItemType.MENUITEM:
            ext_info.ae.callback = action_cb

        # not needed in python - free uses python garbage collection
        #per_window.group.add_actions_full(info.ae, cb_data, free)
        per_window.group.add_actions(info.ae, cb_data)

        per_window.ui_manager.add_ui(per_window.merge_id, ext_info.path, ext_info.ae.label, ext_info.ae.name, ext_info.type, False)

        per_window.ui_manager.ensure_update()


    def actions_cb (self, window)
        pass



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
