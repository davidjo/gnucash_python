
# utilities for combo objects

import gobject

import gtk

from datetime import datetime

import pdb


import sw_app_utils

import gnucash


import qof_ctypes


def N_(msg):
    return msg


#class GncCBWEMixin(object):

if True:

    def gnc_cbwe_set_by_string (self, text):

        model = self.get_model()

        iter = model.get_iter_first()

        if iter == None:
            self.set_active(-1)

        column = self.get_entry_text_column()

        while True:

            tree_string = model.get(iter,column)

            # this could be utf-8
            match = text == tree_string

            if not match:
                iter = model.iter_next(iter)
                continue

            id = self.get_data("changed_id")

            self.handler_block(id)
            self.set_active(iter)
            self.handler_unblock(id)

            index = self.get_active()

            self.set_data("last_index",index)

            return

    def gnc_cbwe_add_completion (self):

        entry = self.get_child()
        completion = entry.get_completion()
        if completion:
            return

        completion = gtk.EntryCompletion()
        model = self.get_model()
        completion.set_model(model)
        completion.set_text_column(0)
        completion.set_inline_completion(True)
        entry.set_completion(completion)

    def gnc_cbwe_require_list_item (self):

        pdb.set_trace()

        self.gnc_cbwe_add_completion()

        entry = self.get_child()
        completion = entry.get_completion()
        index = self.get_active()
        if index == -1:
            model = completion.get_model()
            iter = model.get_iter_first()
            if iter:
                self.set_active(0)
        self.set_data("last_index",index)
        id = self.connect("changed", self.gnc_cbwe_changed_cb)
        completion.connect("match_selected", self.gnc_cbwe_match_selected_cb)
        entry.connect("focus-out-event", self.gnc_cbwe_focus_out_cb)

        self.set_data("changed_id", id)

    def gnc_cbwe_focus_out_cb (self, *args):
        print "gnc_cbwe_focus_out_cb",args
        text = self.get_text()
        self.set_by_string(text)
        index = self.get_data("last_index")
        self.set_active(index)
        return False

    def gnc_cbwe_changed_cb (self, *args):
        print "gnc_cbwe_changed_cb",args
        widget = args[0]
        pdb.set_trace()
        index = widget.get_active()
        if index == -1:
            return
        self.set_data("last_index",index)

    def gnc_cbwe_match_selected_cb (self, *args):
        print "gnc_cbwe_match_selected_cb",args
        column = self.get_entry_text_column()
        text = comp_model.get(comp_iter,0)

    def gnc_cbwe_set_by_string (self, text):
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
                 continue
            id = self.get_data("changed_id")
            self.handler_block(id)
            self.set_active_iter(iter)
            self.handler_unblock(id)

            index = self.get_active()
            self.set_data("last_index",index)
            return

