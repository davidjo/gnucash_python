# finally we need to create a new class
# to run plugins in python

import sys

import os

import json

import pdb

import traceback


from gi.repository import GObject

from gi.repository import Gtk

import girepo


#pdb.set_trace()


import ctypes


import sw_app_utils


import gnucash_log
from gnucash_log import ENTER

import gnc_plugin

#from gnc_plugin import BaseGncPlugin,BaseGncPluginClass
from gnc_plugin import GncPluginPython


import gnc_main_window

import python_menu_extensions

from python_menu_extensions import GncMenuItem, GncActionEntry

import tool_objects


#
# these dont seem to exist any more (except in the dict of Gtk.UIManagerItemType
GTK_UI_MANAGER_MENUBAR = 1
GTK_UI_MANAGER_MENU = 2
GTK_UI_MANAGER_TOOLBAR = 4
GTK_UI_MANAGER_PLACEHOLDER = 8
GTK_UI_MANAGER_POPUP = 16
GTK_UI_MANAGER_MENUITEM = 32
GTK_UI_MANAGER_TOOLITEM = 64
GTK_UI_MANAGER_SEPARATOR = 128
GTK_UI_MANAGER_ACCELERATOR = 256
GTK_UI_MANAGER_POPUP_WITH_ACCELS = 512

# define a function equivalent to N_ for internationalization
def N_(msg):
    return msg


# define a simple function to convert the 64 bit hash to 32 bit
def hash32 (inhsh):
    return (inhsh - (inhsh >> 32)) & (2**32 - 1) 


def close_handler (arg):
    gnucash_log.dbglog_err("close handler called")
    pdb.set_trace()
    pass



class GncPluginPythonTools(GncPluginPython, metaclass=girepo.GncPluginSubClassMeta):

    #__girmetaclass__ = BaseGncPluginClass

    plugin_name = "GncPluginPythonTools"


    # ah - this is something I think Ive missed - we can name the GType here
    __gtype_name__ = 'GncPluginPythonTools'

    # add properties/signals here
    #prop_name = GObject.Property(type=int,...)

    # I think these are more consistent if they are class variables
    # unfortunately cant figure out how to have a method of the class
    # in a class variable

    # the analysis is that essentially in gnucash plugins are single
    # instance classes

    def __init__ (self):

        #pdb.set_trace()

        super(GncPluginPythonTools,self).__init__()
        #GncPluginPython.__init__(self)

        #pdb.set_trace()

        self.class_init()

        # gobjects have constructor function
        #self.constructor(report)


        # load the report classes and create instances
        # first import the report definitions
        tool_objects.load_python_tools()

        # now setup the menus
        self.load_python_tools_menu()



    # to follow the C code in python this should be a classmethod
    # however this does not appear to work for the codegen wrapped functions
    # - looks like you cannot use cls. as the prefix - complains about
    # missing argument - which Im assuming is the self object - so Im assuming
    # the cls object is not being passed as 1st argument
    #@classmethod
    #def class_init (cls):
    #    pass

    def class_init (self):

        # this is the class init function
        # unfortunately Im not seeing anyway to access the private data from python

        # this follows the C code - the GncPlugin class private data is set in the
        # subclass class_init function - not by calling the GncPlugin classes own
        # class_init function!!

        #pdb.set_trace()

        # following the C code we set the parent GncPlugin class variables
        # in the subclass

        # dont quite see why these are class variables - this just follows the
        # C code currently

        GncPluginPythonTools.actions_name = "GncPluginPythonToolsActions"


        GncPluginPythonTools.plugin_actions = [ \
            ("PythonToolsAction", None, "Python Tools...", None, "python tools tooltip", None),
            ("pythongenericAction", None, "Python tools description...", None, "python tools tooltip", self.tools_cb),
            #("exampleAction", None, N_("example description..."), None,
            # N_("example tooltip"),
            # self.cmd_test,
            #),
            ]

        GncPluginPythonTools.plugin_toggle_actions = []

        GncPluginPythonTools.plugin_important_actions = []

        GncPluginPythonTools.ui_filename = None

        GncPluginPythonTools.ui_xml_str = """
<ui>
  <menubar>
    <menu name="Tools" action="ToolsAction" >
      <placeholder name="ToolsPlaceholder">
        <menu name="PythonTools" action="PythonToolsAction">
          <placeholder name="PythonToolsholder">
          </placeholder>
        </menu>
     </placeholder>
    </menu>
  </menubar>
</ui>
"""

        #fdes = open("/Users/djosg/.gnucash/ui/python-tools-plugin.xml",'w')
        #fdes.write(ui_xml)
        #fdes.close()


        # first call the parent class_init - this is only way to do this
        # if we add the parent class_init call to the parent __init__
        # we will call the subclass class_init at that time
        # watch positioning!! - do after class variable defines for safety
        #super(GncPluginPythonTools,self).class_init()


        #pdb.set_trace()

        #print("before access class", file=sys.stderr)

        #priv = girepo.access_class_data(self)

        #print("after access class", file=sys.stderr)


    # note that in the C the primary version of these functions are defined in
    # gnc-plugin.c - and at the end of their code they call the functions saved
    # in the GncPlugin class private data - if they are defined
    # in python this gets sort of inverted - we define functions here to call
    # the parent GncPluginPython class version of these functions - before doing
    # extra work - and the GncPluginPython version of these functions does not
    # call functions of the subclass (how could it)

    def do_add_to_window (self, window, window_type):

        #pdb.set_trace()

        print("called do_add_to_window", file=sys.stderr)

        super(GncPluginPythonTools,self).add_to_window(window, window_type)

        # need to map the window somehow to a window object
        window = gnc_main_window.main_window_extend(window)

        self.menu_extensions.add_to_window(window, window_type)


    def do_remove_from_window (self, window, window_type):

        #pdb.set_trace()

        # need to map the window somehow to a window object
        save_window = window
        window = gnc_main_window.main_window_extend(window)

        self.menu_extensions.remove_from_window(window, window_type)

        #printr("called do_remove_from_window", file=sys.stderr)
        #pdb.set_trace()
        #print("called do_remove_from_window", file=sys.stderr)

        super(GncPluginPythonTools,self).remove_from_window(save_window, window_type)



    def add_menuitems (self, name, tool):

        # this function needs to be defined in this module as it varies per python module

        # create the data needed for Gtk.ActionGroup.add_actions
        title = N_("Tools")+": "+N_(name)

        menuitm = GncMenuItem()
        ae = GncActionEntry()

        ae.name = tool.tool_guid
        if tool.menu_name:
            ae.label = tool.menu_name
        elif tool.name:
            ae.label = tool.name
        else:
            ae.label = name
        if tool.menu_tip:
            ae.tooltip = tool.menu_tip
        else:
            ae.tooltip = N_("Run the %s tool"%name)
        if tool.stock_id:
            ae.stock_id = tool.stock_id
        else:
            ae.stock_id = None
        ae.accelerator = None
        ae.callback = self.tools_cb
        menuitm.ae = ae
        if tool.menu_path:
            #menuitm.path = "ui/menubar/Tools/"+tool.menu_path
            menuitm.path = "ui/menubar/Tools/ToolsPlaceholder/PythonTools/PythonToolsholder/"
        else:
            menuitm.path = "ui/menubar/Tools/ToolsPlaceholder/PythonTools/PythonToolsholder/"
        menuitm.name = ae.label
        menuitm.action = ae.name
        menuitm.type = Gtk.UIManagerItemType.MENUITEM
        return menuitm

    def load_python_tools_menu (self):

        #pdb.set_trace()

        menu_list = []
        for tool in sorted(tool_objects.python_tools_by_name.keys()):
            menu_list.append(self.add_menuitems(tool,tool_objects.python_tools_by_name[tool]))

        group_name = self.actions_name+'MenuItems'

        # now need to update menu
        self.menu_extensions = python_menu_extensions.PythonMenuAdditions(group_name, menu_list)


    def tools_cb (self, actionobj, user_data=None):

        pdb.set_trace()

        gnucash_log.dbglog_err("tools_cb",actionobj,user_data)
        gnucash_log.dbglog_err("tools_cb",actionobj.get_name())

        window = user_data

        print("tools_cb",actionobj)
        print("tools_cb",actionobj.get_name())

        #pdb.set_trace()

        # junk test
        #trybook = sw_app_utils.get_current_book()

        print("tools_cb","after book")

        try:
            tool_guid = actionobj.get_name()
            tool_obj = tool_objects.python_tools_by_guid[tool_guid]
            tool_obj.run()
            gnucash_log.dbglog("call back done")
        except Exception as errexc:
            traceback.print_exc()
            print("error in tools_cb callback for ",str(errexc), file=sys.stderr)


#pdb.set_trace()

GObject.type_register(GncPluginPythonTools)


