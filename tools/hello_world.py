

import gtk

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

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_default_size(800,600)
        self.window.set_border_width(0)
        self.window.connect('destroy-event', self.destroy_cb)
        self.window.connect('delete-event', self.delete_cb)
        button = gtk.Button(label="My Button")
        self.window.add(button)
        self.window.show_all()

    def destroy_cb (self, actionobj, userdata=None):
        self.window.destroy()

    def delete_cb (self, actionobj, userdata=None):
        self.window.destroy()


