
# utilities for combo objects


import types


#from gi.repository import GObject

from gi.repository import Gtk

from datetime import datetime

import pdb


import sw_app_utils

import gnucash


import qof_ctypes


def N_(msg):
    return msg


# define this response constant here
RESPONSE_NEW = 1

if True:

    def set_by_string (self, text):
        model = self.get_model()
        iter = model.get_iter_first()
        if not iter:
            self.set_active(-1)
            return
        column = self.get_entry_text_column()
        while True:
            tree_string = model.get_value(iter,column)
            if tree_string != text:
                 iter = model.iter_next(iter)
                 if not iter:
                     break
                 continue
            id = self.get_data("changed_id")
            self.handler_block(id)
            self.set_active_iter(iter)
            self.handler_unblock(id)

            index = self.get_active()
            self.set_data("last_index",index)
            return

    def add_completion (self):

        entry = self.get_child()
        completion = entry.get_completion()
        if completion:
            return

        completion = Gtk.EntryCompletion()
        model = self.get_model()
        completion.set_model(model)
        completion.set_text_column(0)
        completion.set_inline_completion(True)
        entry.set_completion(completion)

    def require_list_item (self):

        self.add_completion()

        entry = self.get_child()
        completion = entry.get_completion()
        index = self.get_active()
        if index == -1:
            model = completion.get_model()
            iter = model.get_iter_first()
            if iter:
                self.set_active(0)
        self.set_data("last_index",index)
        id = self.connect("changed", self.changed_cb)
        completion.connect("match_selected", self.match_selected_cb)
        entry.connect("focus-out-event", self.focus_out_cb)

        self.set_data("changed_id", id)

    def focus_out_cb (self, entry, event):
        print "gnc_cbwe_focus_out_cb"
        text = entry.get_text()
        self.set_by_string(text)
        index = self.get_data("last_index")
        self.set_active(index)
        return False

    def changed_cb (self, *args):
        print "gnc_cbwe_changed_cb",args
        widget = args[0]
        index = widget.get_active()
        if index == -1:
            return
        self.set_data("last_index",index)

    def match_selected_cb (self, *args):
        print "gnc_cbwe_match_selected_cb",args
        column = self.get_entry_text_column()
        text = comp_model.get(comp_iter,0)


# unfortunately unless I can figure out how to do dynamic subclasses
# this seems to be the only way
# define the functions at the module level
# store them in the Mixin class
# hopefully can then use them as Mixin and objects

class GncCBWEMixin(object):
    pass
GncCBWEMixin.set_by_string = set_by_string
GncCBWEMixin.add_completion = add_completion
GncCBWEMixin.require_list_item = require_list_item
GncCBWEMixin.focus_out_cb = focus_out_cb
GncCBWEMixin.changed_cb = changed_cb
GncCBWEMixin.match_selected_cb = match_selected_cb


def add_utils (combo_object):
    # try adding directly as attributes
    # this seems to work
    combo_object.set_by_string = types.MethodType(set_by_string, combo_object, combo_object.__class__)
    combo_object.add_completion = types.MethodType(add_completion, combo_object, combo_object.__class__)
    combo_object.require_list_item = types.MethodType(require_list_item, combo_object, combo_object.__class__)
    combo_object.focus_out_cb = types.MethodType(focus_out_cb, combo_object, combo_object.__class__)
    combo_object.changed_cb = types.MethodType(changed_cb, combo_object, combo_object.__class__)
    combo_object.match_selected_cb = types.MethodType(match_selected_cb, combo_object, combo_object.__class__)



# new attempt - make a proper class using the mixin
# - then use instantiation of this where need to

class GncCBWE(GncCBWEMixin):

    def __init__ (self):
        #self.gnc_cbwe = GncCBWEMixin()
        pass

    # try using classmethods
    # this is probably not going to work
    # may need static methods
    @classmethod
    def gnc_cbwe_set_by_string (cls, text):
        cls.set_by_string(text)
    def gnc_cbwe_add_completion (self):
        pass
    @classmethod
    def gnc_cbwe_require_list_item (cls):
        cls.require_list_item()
    def gnc_cbwe_focus_out_cb (self, *args):
        pass
    def gnc_cbwe_changed_cb (self, *args):
        pass
    def gnc_cbwe_match_selected_cb (self, *args):
        pass
    def gnc_cbwe_set_by_string (self, text):
        pass

