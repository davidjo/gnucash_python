

#import gtk

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

import pdb

# how to do internationalization in python
#import gettext
#gettext.bindtextdomain('myapplication', '/path/to/my/language/directory')
#gettext.textdomain('myapplication')
#_ = gettext.gettext
# dummy function for internationalization
def N_(msg):
    return msg

import datetime

from tool_objects import ToolTemplate


class MyWindow(Gtk.Window):

    def __init__ (self):
        super(MyWindow, self).__init__(title="MyWindow")


class HelloWorld(ToolTemplate):

    def __init__ (self):

        super(HelloWorld,self).__init__()

        # need to set the  base variables
        self.version = 1
        self.name = N_("Hello, World")
        self.tool_guid = "1244f648c6c14dcbb5bf5c95061a3a83"
        self.menu_name = N_("Sample Tool Action")
        self.menu_tip = N_("A sample tool.")
        #self.menu_path = N_("Tool Path")
        #self.stock_id = None

    def run (self):

        #pdb.set_trace()

        # oh bog - Gtk introspection seems to be weirdly broken for tools
        # so GObject creation seems to fail in a weird way

        # as far as I can see a window is now by definition toplevel
        #self.window = Gtk.Window(Gtk.WINDOW_TOPLEVEL)
        self.window = Gtk.Window()
        # and I dont know how to set this either
        # there seems a dearth of information about how to set flags
        # with introspection
        #self.window.set_position(Gtk.WIN_POS_CENTER)
        #self.window.set_default_size(800,600)
        #self.window.set_border_width(0)
        #self.window.connect('destroy-event', self.destroy_cb)
        #self.window.connect('delete-event', self.delete_cb)
        #button = Gtk.Button(label="My Button")
        #self.window.add(button)
        self.window.show_all()

    def destroy_cb (self, actionobj, userdata=None):
        print("sample tool destroy_cb")
        self.window.destroy()
        print("sample tool destroy_cb after")

    def delete_cb (self, actionobj, userdata=None):
        print("sample tool delete_cb")
        self.window.destroy()
        print("sample tool delete_cb after")


