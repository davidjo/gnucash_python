
# special general select widget

import gobject

import gtk

from datetime import datetime

import pdb


import sw_app_utils

import gnucash


import qof_ctypes


def N_(msg):
    return msg


class GncGeneralSelect(gtk.HBox):

    GNC_GENERAL_SELECT_TYPE_SELECT = 1
    GNC_GENERAL_SELECT_TYPE_EDIT = 2
    GNC_GENERAL_SELECT_TYPE_VIEW = 3

    # ah - this is something I think Ive missed - we can name the GType here
    __gtype_name__ = 'GncGeneralSelect'

    # OK Im now thinking gobject warning messages were happening previously but just did not get the message

    cmtstr = """
    __gproperties__ = {
                       'mnemonic' : (gobject.TYPE_STRING,                     # type
                                      N_("Active currency's mnemonic"),       # nick name
                                      N_("Active currency's mnemonic"),       # description
                                      "USD",                                  # default value
                                      gobject.PARAM_READWRITE),               # flags
                      }
    """

    __gsignal__ = {
                   'changed' : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (int,))
                  }


    def __init__ (self, type, get_string, new_select, cb_arg):

        super(GncGeneralSelect,self).__init__()

        self.disposed = False
        self.selected_item = None

        self.create_children(type)

        self.get_string = get_string
        self.new_select = new_select
        self.cb_arg = cb_arg


    def dispose (self):

        if self.disposed:
            return

        self.disposed = True

        self.entry.destroy()
        self.button.destroy()


    def select_cb (self, *args):
        print "select_cb", args
        toplevel = self.get_toplevel()
        new_selection = self.new_select(self.cb_arg, self.selected_item, toplevel)
        if new_selection == None:
            return
        self.set_selected(new_selection)


    def create_children (self, type):
 
        self.entry = gtk.Entry()
        self.entry.set_editable(False)
        self.pack_start(self.entry,expand=True,fill=True,padding=0)

        if type == GncGeneralSelect.GNC_GENERAL_SELECT_TYPE_SELECT:
            self.button = gtk.Button(label=N_("Select..."))
        elif type == GncGeneralSelect.GNC_GENERAL_SELECT_TYPE_EDIT:
            self.button = gtk.Button(label=N_("Edit..."))
        elif type == GncGeneralSelect.GNC_GENERAL_SELECT_TYPE_VIEW:
            self.button = gtk.Button(label=N_("View..."))

        self.pack_start(self.button,expand=False,fill=False,padding=0)

        self.button.connect("clicked",self.select_cb)

        self.button.show()



    def get_printname (self, selection):

        retval = self.get_string(seleciton)

        return retval

    def set_selected (self, selection):

        self.selected_item = selection

        if selection:
            text = ""
        else:
            text = self.get_printname(selection)

        self.entry.set_text(text)

        self.emit("changed",0)

    def get_selected (self):

        return self.selection_item

    def make_mnemonic_target (self, label):

        label.set_mnemonic_widget(self.entry)


