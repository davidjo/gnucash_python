

import re

import pdb


import gnucash_log
from gnucash_log import ENTER


# gnucash has another GncPlugin, GncPluginMenuAdditions (gnc-plugin-menu-additions)
# which is used to load menu additions - mainly for the scheme reports
# where the number of items (reports) changes and the menu callback
# executed runs scheme code

# we cannot use the gnc-menu-extensions and gnc-plugin-menu-additions
# as they are tied to scheme - because gnc-plugin-menu-additions gets its
# list from gnc-menu-extensions which is totally tied to scheme

# here we implement a version of gnc-menu-extensions in python


class GncMenuItem(object):
    def __init__ (self,path=None,ae=None,action=None,type=None):
        self.path = path
        self.ae = ae
        self.action = action
        self.type = type

class GncActionEntry(object):
    def __init__ (self,name=None,stock_id=None,label=None,accelerator=None,tooltip=None,callback=None):
        self.name = name
        self.stock_id = stock_id
        self.label = label
        self.accelerator = accelerator
        self.tooltip = tooltip
        self.callback = callback

    def as_tuple (self):
        return (self.name,self.stock_id,self.label,self.accelerator,self.tooltip,self.callback)


# dict??
# have a feeling dict will be more useful
menu_list = []

class ExtensionInfo(object):


    def __init__ (self, ext_path, ext_type, ext_name, ext_doc):

        self.ae = None
        self.path = None
        self.sort_key = None
        self.typeStr = None
        self.type = None
        self.accel_assigned = None

        self.path = self.extension_path(ext_path)

        self.type = self.extension_type(ext_type)

        self.ae = GtkActionEntry()

        self.ae.label = N_(ext_name)
        self.ae.name = self.gen_action_name(ext_name)
        self.ae.tooltip = ext_doc
        self.ae.stock_id = None
        self.ae.callback = None
        self.ae.sort_key = "%s/%s"%(self.path, self.ae.label)

        if self.type == Gtk.UIManagerItemType.MENU:
            self.typeStr =  "menu"
        elif self.type == Gtk.UIManagerItemType.MENUITEM:
            self.typeStr =  "menuitem"
        else:
            self.typeStr =  "unk"

        #DEBUG( "extension: %s/%s [%s] tip [%s] type %s\n",
        #       ext_info->path, ext_info->ae.label, ext_info->ae.name,
        #       ext_info->ae.tooltip, ext_info->typeStr );



    @staticmethod
    def extension_path (menu_path):

        # in scheme menu_path seems to be a list of path components
        # the original code simply joins them with '/' and prepending '/menubar'
        # for the moment assume full path so just pre-concatenate /menubar

        # strictly need to do something like
        menu_list = menu_path.split('/')
        for mindx,mitm in enumerate(menu_list):
            if mindx > 0:
                menu_list[mindx] = N_(menu_list)
        new_menu = '/'.join(menu_list)

        fullpath =  '/menubar' + '/' + new_menu

        return fullpath


    @staticmethod
    def extension_type (menu_type):

        if menu_type == "menu-item":
            ext_type = Gtk.UIManagerItemType.MENUITEM
        elif menu_type == "menu":
            ext_type = Gtk.UIManagerItemType.MENU
        elif menu_type == "separator":
            ext_type = Gtk.UIManagerItemType.SEPARATOR
        else:
            raise ValueError("unknown menu type string %s"%menu_type)

        return ext_type

    @staticmethod
    def gen_action_name (name):

        new_name = re.sub(r'\W+', '',name)

        new_name = new_name + 'Action'

        return new_name


def create_extension_info (ext_path, ext_type, ext_name, ext_doc):

    global menu_list
    
    newitm = ExtensionInfo(self, ext_path, ext_type, ext_name, ext_doc)

    menu_list.append(newitm)


def add_extension (ext_path, ext_type, ext_name, ext_doc):

    create_extension_info (ext_path, ext_type, ext_name, ext_doc)

    # we already raise exceptions on errors
    #if not retval:
    #    raise TypeError("invalid extension")
