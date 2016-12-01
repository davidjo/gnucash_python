# menu items are added for each report

# this is a translation as close as possible to the Scheme/C

from gi.repository import GObject

from gi.repository import Gtk

# I dont get this yet - for the example plugin this adds GUI menu elements
# through an .xml file which is loaded on plugin load (a lot through gnc_module_load_common)
# the report menu extensions are collected as reports loaded
# but only added in gnc_main_gui_init 

# gdb trace back for creation
#0  0x000000010021bc87 in gnc_plugin_menu_additions_new ()
#1  0x00000001000a80fd in gnc_main_gui_init ()

# and for addition per plugin
# note that the signal PLUGIN_ADDED is emitted in gnc_plugin_manager_add_plugin
# (that is PLUGIN_ADDED is sent to newly loaded plugin)
# which invokes gnc_plugin_add_to_window
#0  0x00000001002122b3 in gnc_main_window_manual_merge_actions ()
#1  0x000000010021bfd1 in gnc_plugin_menu_additions_add_to_window ()
#2  0x000000010021fbd3 in gnc_plugin_add_to_window ()
#3  0x0000000104f4d7f1 in g_cclosure_marshal_VOID__OBJECTv ()
#4  0x0000000104f4ada6 in _g_closure_invoke_va ()
#5  0x0000000104f6143e in g_signal_emit_valist ()
#6  0x0000000104f625d4 in g_signal_emit ()
#7  0x000000010021b77a in gnc_plugin_manager_add_plugin ()
#8  0x00000001000a8110 in gnc_main_gui_init ()



class GncActionEntry(object):
    # this should contain data for an action entry

    def __init__ (self):
        pass

# OK so this class is the data storage for SCM menu extensions

class MenuExtension(object):

    def __init__ (self):
        # copied from gnome-utils/gnc-menu-extensions.scm
        # ;; The type of extension item, either 'menu, 'menu-item, or 'separator
        self.type = None
        # ;; The name of the extension in the menu
        self.name = None
        # ;; The guid of object the menu will refer to
        self.guid = None
        # ;; The tooltip
        self.documentation_string = None
        # ;; A list of names indicating the menus under which this item is
        # ;; located. The last item indicates the item *after* which this
        # ;; extension will go.
        self.path = None
        # ;; The script to call when the menu item is selected
        self.script = None


    @classmethod
    def make_menu_item (cls,name,guid,documentation_string,path,script):
        newobj = cls()
        newobj.type = 'menu-item'
        newobj.name = name
        newobj.guid = guid
        newobj.documentation_string = documentation_string
        newobj.path = path
        newobj.script = script
        return newobj

    @classmethod
    def make_menu (cls,name,path):
        newobj.type = 'menu'
        newobj.name = name
        newobj.guid = name
        newobj.path = path
        return newobj

    @classmethod
    def make_separator_path (cls,path):
        newobj.type = 'separator'
        newobj.path = path
        return newobj


# this is the actual Gtk menu generator class
# no - this is another middle class which converts from SCM
# to a list ready to actually call Gtk functions

extension_list = []

class GncMenuExtensionInfo(object):

    def __init__ (self, menu_extension):
        # this is equivalent of gnc_create_extension_info
        self.extension = menu_extension
        self.path = menu_extension.path
        self.type = self.get_extension_type(menu_extension)
        if self.type == None:
            # how to handle errors??
            #raise
            return
        self.name = menu_extension.name
        self.guid = menu_extension.guid
        # this essentially builds a Gtk.ActionEntry
        self.ae = GncActionEntry()
        self.ae.label = self.name
        self.ae.name = self.guid
        self.ae.tooltip = self.documentation_string
        self.ae.stock_id = None
        self.ae.accelerator = None
        self.ae.callback = None
        # construct the path for sorting
        # do we need this - should call g_utf8_collate_key
        # self.sort_key = "%s/%s"%(self.path,self.ae.label)
        if self.type == Gtk.Menu:
            self.typeStr = "menu"
        elif self.type == Gtk.MenuItem:
            self.typeStr = "menuitem"
        else:
            self.typeStr = "unk"

        #DEBUG( "extension: %s/%s [%s] tip [%s] type %s",
        #       ext_info.path, ext_info.ae.label, ext_info.ae.name,
        #       ext_infoi.ae.tooltip, ext_info.typeStr )

        # the primary goal is adding to this list to get added to menus later
        extension_list.append(self)


    def get_extension_type (self, menu_extension):
        if menu_extension.type == 'menu-item':
            return Gtk.MenuItem
        elif menu_extension.type == 'menu':
            return Gtk.Menu
        elif menu_extension.type == 'separator':
            return Gtk.SeparatorMenuItem
        #PERR("bad type")
        return None


# finally - we are in gnc-plugin-menu-additions
# which creates a new GObject GncPluginMenuAdditions as a subclass of GncPlugin 

# can we create a totally new class here
# or do we need to wrap this class or make a subclass of GncPlugin 

class GncPluginMenuAdditionsPerWindow(object):
    # this is primarily a data storage class
    pass

class GncPluginMenuAdditions(GObject.GObject):

    def __init__ (self):
        pass


    def menu_setup_one (self, ext_info, per_window):
        # this function actually adds individual new menu items

        #DEBUG( "Adding %s/%s [%s] as [%s]", ext_info.path, ext_info.ae.label,
        #       ext_info.ae.name, ext_info.typeStr )

        #cb_data = g_new0 (GncMainWindowActionData, 1);
        #cb_data->window = per_window->window;
        #cb_data->data = ext_info->extension;
        cb_data = GncMainWindowActionData()
        cb_data.window = per_window.window
        cb_data.data = per_window.extension

        # self.action_cb eventually invokes the script item of the MenuExtension
        if ext_info.type == Gtk.MenuItem:
            ext_info.ae.callback = self.action_cb

        # this is an actionentry list of 1
        per_window.group.add_actions(ext_info.ae, user_data=cb_data)
        per_window.ui_manager.add_ui(per_window.merge_id,
                              ext_info.path, ext_info.ae.label, ext_info.ae.name,
                              ext_info.type, False)
        per_window.ui_manager.ensure_update()



    def add_to_window (self, window, type):
        # this is the function that actually adds the new menu items
        per_window = GncPluginMenuAdditionsPerWindow()
        per_window.window = window
        per_window.ui_manager = window.get_uimanager()
        per_window.group = Gtk.ActionGroup("PythonMenuAdditions")
        #per_window.group.set_translation_domain(GETTEXT_PACKAGE)
        per_window.merge_id = per_window.ui_manager.new_merge_id()

        #menu_list = sorted(gnc_extension_get_menu_list,key=gnc_menu_additions_sort)

        # mess with accelerators
        # /* Assign accelerators */
        # table = g_once(&accel_table_init, gnc_menu_additions_init_accel_table, NULL);
        # g_slist_foreach(menu_list,
        #                 (GFunc)gnc_menu_additions_do_preassigned_accel, table);
        # g_slist_foreach(menu_list, (GFunc)gnc_menu_additions_assign_accel, table);

        # /* Add to window. */
        # g_slist_foreach(menu_list, (GFunc)gnc_menu_additions_menu_setup_one,
        #                 &per_window);

        window.manual_merge_actions("gnc-plugin-menu-additions-actions",per_window.group,per_window.merge_id)
