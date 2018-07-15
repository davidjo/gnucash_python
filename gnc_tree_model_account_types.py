
# very preliminary attempt at ctypes wrap of functions
# in gnc-tree-model-account-types.c
# NOTE not used at the moment

import sys

import types

from gi.repository import GObject

from gi.repository import Gtk

import ctypes


import pdb

import gc


import sw_app_utils

import gnome_utils_ctypes

import glib_ctypes

import gnucash

import gnucash.gnucash_core_c

from gnucash.gnucash_core_c import string_to_guid as gnucash_core_string_to_guid

import swighelpers

import gnucash_log



from pygobjectcapi import PyGObjectCAPI

# call like this:
# Cgobject = PyGObjectCAPI()
# Cgobject.pygobject_new(memory_address)

# to get memory address from a gobject:
#  address = hash(obj)


#pdb.set_trace()


Cgobject = PyGObjectCAPI()


NUM_ACCOUNT_TYPES = gnucash.gnucash_core_c.NUM_ACCOUNT_TYPES

GNC_TREE_MODEL_ACCOUNT_TYPES_COL_TYPE = 0
GNC_TREE_MODEL_ACCOUNT_TYPES_COL_NAME = 1
GNC_TREE_MODEL_ACCOUNT_TYPES_COL_SELECTED = 2
GNC_TREE_MODEL_ACCOUNT_TYPES_NUM_COLUMNS = 3


gboolean = ctypes.c_int


# dont know if GncTreeModelAccountTypes is defined at load time
# (as GncTreeViewAccount is not)

# following the GncTreeViewAccount way to create GncTreeModelAccountTypes objects
# but we do not get access to the additional functions the class defines
# only get access to the functions we have mapped for the parent classe(s)
# looks as though we need to add functions to the python side

# dont know if GObject.new does not work - just in case assuming like
# gnc_tree_view_account that defines specific constructor functions which
# do things just calling GObject.new does not


def new (selected):

    # but they are defined at this point

    #pdb.set_trace()

    #tmptreeview = GObject.new(GObject.type_from_name('GncTreeView'))
    #tmptreeviewaccount = GObject.new(GObject.type_from_name('GncTreeViewAccount'))
    #print("trying 1")
    #print(tmptreeviewaccount)
    #print("trying 2")
    #newaccview = GObject.new(GObject.type_from_name('GncTreeViewAccount'))


    newtreemdl_ptr = gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_model_account_types_new(selected)

    # call like this:
    newtreemdl = Cgobject.pygobject_new(newtreemdl_ptr)

    init_functions(newtreemdl)

    return newtreemdl



def init_functions (newtreemdl):

    newtreemdl.set_mask = types.MethodType(set_mask, newtreemdl, newtreemdl.__class__)

    newtreemdl.get_mask = types.MethodType(get_mask, newtreemdl, newtreemdl.__class__)




def set_mask (self, acc_types):

    #pdb.set_trace()
    #print("set_selected_accounts 1",self)
    #gc.collect()

    trmdlptr = hash(self)

    gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_model_account_types_set_mask(trmdlptr, acc_types)

def get_mask (self):

    #pdb.set_trace()
    #print("set_selected_accounts 1",self)
    #gc.collect()

    trmdlptr = hash(self)

    retval = gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_model_account_types_get_mask(trmdlptr)

    return retval


def filter_using_mask (acc_types):

    #pdb.set_trace()
    gnucash_log.dbglog("filter_using_mask")

    #gnucash_log.dbglog(acc_types)

    f_model_ptr = gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_model_account_types_filter_using_mask(acc_types)

    f_model = Cgobject.pygobject_new(f_model_ptr)

    return f_model

def get_selection (sel):

    # oh boy - this is another GObject type - GtkTreeSelection

    #pdb.set_trace()
    gnucash_log.dbglog("get_selection",sel)
    #gc.collect()

    selptr = hash(sel)
    #gnucash_log.dbglog_err("tree view",self)
    #gnucash_log.dbglog_err("tree view 0x%x"%trvwptr)

    retval = gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_model_account_types_get_selection(selptr)

    return retval

def get_selection_single (sel):

    # oh boy - this is another GObject type - GtkTreeSelection

    #pdb.set_trace()
    gnucash_log.dbglog("get_selection_single",sel)
    #gc.collect()

    selptr = hash(sel)
    #gnucash_log.dbglog_err("tree view",self)
    #gnucash_log.dbglog_err("tree view 0x%x"%trvwptr)

    retval = gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_model_account_types_get_selection_single(selptr)

    # this is GNCAccountType enum
    return retval

def set_selection (sel, selected):

    # oh boy - this is another GObject type - GtkTreeSelection

    #pdb.set_trace()
    gnucash_log.dbglog("set_selection",sel)
    #gc.collect()

    selptr = hash(sel)
    #gnucash_log.dbglog_err("tree view",self)
    #gnucash_log.dbglog_err("tree view 0x%x"%trvwptr)

    gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_model_account_types_set_selection(selptr, selected)


