
# this is a re-coded update of menu items for python reports
# note this only used for old python_only_reports
# and not really used so not tested out or updated
# only left for legacy reasons at the moment
# menu extension handled by python_menu_extensions now

from gi.repository import Gtk

from gi.repository import GObject


import pdb


#import pythoncallback



# this works with the pythoncallback module
# pass a callback saver object for the moment
class MyCallbacks(object):

    def __init__ (self):
        self.user_data = None
        self.callbacks = {}


class MyMenuAdditions(GObject.GObject):

    def __init__ (self, window):
        self.window = window
        self.ui_manager = None
        self.group = None
        self.merge_id = None

        #self.menu_list = []

        self.menu_callbacks = {}



    def add_menu_item (self, menuitm):
        # we need to switch the callback
        # ooh - we may not need this - pythoncallback essentially does this
        # - and all action_cb does is call the original callback!!
        #self.menu_callbacks[menuitm.ae.name] = menuitm.ae.callback
        #menuitm.ae.callback = self.action_cb
        # although it says add actions we are actually adding one
        #print("group",self.group)
        #print("menuitem",menuitm)
        #print("menuitem",menuitm.ae.as_tuple())
        #pdb.set_trace()
        #pythoncallback.add_actions(self.save_callbacks, self.group, [menuitm.ae.as_tuple()], user_data=self.window)
        self.group.add_actions([menuitm.ae.as_tuple()],user_data=self.window)
        # so this implements the xml
        # with path giving the menu position
        #   <menuitem name="Python Reports" action="pythonreportsAction"/>
        #print(" preui",self.ui_manager.get_ui())
        #print("add_ui",self.merge_id,menuitm.path,menuitm.name,menuitm.action,menuitm.type)
        self.ui_manager.add_ui(self.merge_id,menuitm.path,menuitm.name,menuitm.action,menuitm.type,False)
        #print("postui",self.ui_manager.get_ui())
        self.ui_manager.ensure_update()

    def add_to_window (self, menu_list):
        self.ui_manager = self.window.get_uimanager()
        self.group = Gtk.ActionGroup("PythonMenuAdditions")
        #gnc_gtk_action_group_set_translation_domain (per_window.group, GETTEXT_PACKAGE);
        self.merge_id = self.ui_manager.new_merge_id()
        self.ui_manager.insert_action_group(self.group,0)
        # sort list
        # do accelerators
        # then add
        #self.save_callbacks = MyCallbacks()
        for menuitm in menu_list:
            self.add_menu_item(menuitm)
        # ah - this does not update any gtk stuff just gnc stuff handling the menu additions
        #gnc_main_window_manual_merge_actions("gnc-plugin-menu-additions-actions",self.group,self.merge_id)
        self.window.manual_merge_actions("gnc-plugin-menu-additions-actions",self.group,self.merge_id)

    def action_cb (self, action_obj, **kywds):
        print("action_cb",action_obj,kywds)
        print("name",action_obj.get_name())
        #self.menu_callbacks[menuitem.ae.name](args)
        pass
