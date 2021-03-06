

import sys

import types

#import gobject

#import gtk

import ctypes


import pdb

import gc


import sw_app_utils

import gnome_utils_ctypes

import glib_ctypes

#import qof_ctypes

import gnucash

import gnucash.gnucash_core_c

from gnucash.gnucash_core_c import string_to_guid as gnucash_core_string_to_guid

import swighelpers


def string_to_new_guid (cls, str):
    #pdb.set_trace()
    guid = cls()
    retval = gnucash_core_string_to_guid(str,guid.instance)
    if retval:
        return guid
    else:
        raise Exception("Unable to convert string to GUID")

gnucash.GUID.string_to_guid = classmethod(string_to_new_guid)


from pygobjectcapi import PyGObjectCAPI
#from pygobjectcapi_gi import PyGObjectCAPI

# call like this:
# Cgobject = PyGObjectCAPI()
# Cgobject.to_object(memory_address)

# to get memory address from a gobject:
#  address = hash(obj)


#pdb.set_trace()


Cgobject = PyGObjectCAPI()


NUM_ACCOUNT_TYPES = gnucash.gnucash_core_c.NUM_ACCOUNT_TYPES


class AccountOpaque(ctypes.Structure):
    pass


gboolean = ctypes.c_int

class AccountViewInfo(ctypes.Structure):
    pass
AccountViewInfo._fields_ = [
                            ('include_type', gboolean*NUM_ACCOUNT_TYPES),
                            ('show_hidden', gboolean),
                           ]

AccountViewInfoPtr = ctypes.POINTER(AccountViewInfo)


# great - GncTreeView or GncTreeViewAccount are not defined at the load point

# so we have to use the following to create new GncTreeViewAccount objects
# but we do not get access to the additional functions the class defines
# only get access to the functions we have mapped for the parent classe(s)
# looks as though we need to add functions to the python side

# unfortunately just using gobject.new does not work - gnc_tree_view_account defines
# specific constructor functions which do things just calling gobject.new does not


def new_with_root (root, show_root):

    # but they are defined at this point

    #pdb.set_trace()

    #tmptreeview = GObject.new(GObject.type_from_name('GncTreeView'))
    #tmptreeviewaccount = GObject.new(GObject.type_from_name('GncTreeViewAccount'))
    #print("trying 1")
    #print(tmptreeviewaccount)
    #print("trying 2")
    #newaccview = GObject.new(GObject.type_from_name('GncTreeViewAccount'))


    account_ptr = ctypes.cast( root.instance.__int__(), ctypes.POINTER( AccountOpaque ) )

    newaccview_ptr = gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_view_account_new_with_root(account_ptr, show_root)

    # call like this:
    newaccview = Cgobject.to_object(newaccview_ptr)


    newaccview.do_get_headers_visible = types.MethodType(do_get_headers_visible, newaccview)

    newaccview.do_set_headers_visible = types.MethodType(do_set_headers_visible, newaccview)

    newaccview.do_get_selection = types.MethodType(do_get_selection, newaccview)

    newaccview.do_set_selection = types.MethodType(do_set_selection, newaccview)


    newaccview.do_get_view_info = types.MethodType(get_view_info, newaccview)

    newaccview.do_set_view_info = types.MethodType(set_view_info, newaccview)

    newaccview.do_get_cursor_account = types.MethodType(get_cursor_account, newaccview)

    newaccview.do_select_subaccounts = types.MethodType(select_subaccounts, newaccview)

    newaccview.do_set_selected_accounts = types.MethodType(set_selected_accounts, newaccview)

    newaccview.do_get_selected_accounts = types.MethodType(get_selected_accounts, newaccview)

    return newaccview


def new (show_root):
    curbook = sw_app_utils.get_current_book()
    rootacc = curbook.get_root_account()
    return new_with_root(rootacc,show_root)


def do_get_headers_visible (self):
    return self.get_headers_visible()

def do_set_headers_visible (self, make_visible):
    self.set_headers_visible(make_visible)

def do_get_selection (self):
    return self.get_selection()

def do_set_selection (self, slctn):
    self.set_get_selection(slctn)


def get_view_info (self):

    #pdb.set_trace()

    vwinfo = AccountViewInfo()

    print("0x%x"%ctypes.addressof(vwinfo), file=sys.stderr)
    print("0x%x"%ctypes.addressof(vwinfo.include_type), file=sys.stderr)

    vwptr = ctypes.pointer(vwinfo)
    print("0x%x"%ctypes.addressof(vwptr), file=sys.stderr)
    print("0x%x"%ctypes.addressof(vwptr.contents), file=sys.stderr)

    trvwptr = hash(self)
    print("tree view",self, file=sys.stderr)
    print("tree view 0x%x"%trvwptr, file=sys.stderr)

    gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_view_account_get_view_info(trvwptr, ctypes.cast( vwptr, ctypes.c_void_p ) )

    return vwinfo

def set_view_info (self, vwinfo):

    #pdb.set_trace()
    #print("set_view_info 1",self)
    #gc.collect()

    print("0x%x"%ctypes.addressof(vwinfo), file=sys.stderr)
    print("0x%x"%ctypes.addressof(vwinfo.include_type), file=sys.stderr)

    vwptr = ctypes.pointer(vwinfo)

    print("0x%x"%ctypes.addressof(vwptr), file=sys.stderr)
    print("0x%x"%ctypes.addressof(vwptr.contents), file=sys.stderr)

    trvwptr = hash(self)

    gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_view_account_set_view_info(trvwptr, ctypes.cast( vwptr, ctypes.c_void_p ) )

    #print("set_view_info 2")
    #gc.collect()


def get_cursor_account (self):

    pdb.set_trace()
    print("get_cursor_account")

    trvwptr = hash(self)

    account_ptr = gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_view_account_get_cursor_account(trvwptr)

    if account_ptr == None:
        return None

    ## bugger - we now hit the big problem - how to convert raw C pointers to swig instances
    ## ah - got a way - stupid but what can we do
    ## get the account guid and look it up 
    #curbook = sw_app_utils.get_current_book()
    #qof_ptr = ctypes.cast( account_ptr, ctypes.POINTER( qof_ctypes.QofInstanceOpaque ) )
    #acc_guid = qof_ctypes.libgnc_qof.qof_instance_get_guid(qof_ptr)
    #acc_guid_str = "".join([ "%02x"%x for x in acc_guid.contents.data ])
    #acc_guid = gnucash.GUID.string_to_guid(acc_guid_str)
    #account = gnucash.GUID.AccountLookup(acc_guid,curbook)


    accinst = swighelpers.int_to_swig(account_ptr,"_p_Account")
    account = gnucash.Account(instance=accinst)


    return account

def select_subaccounts (self, account):

    #pdb.set_trace()
    print("select_subaccounts")

    print(self)
    print(account)

    account_ptr = ctypes.cast( account.instance.__int__(), ctypes.POINTER( AccountOpaque ) )

    trvwptr = hash(self)

    gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_view_account_select_subaccounts(trvwptr, account_ptr)


def set_selected_accounts (self, account_list, show_last):

    pdb.set_trace()
    #print("set_selected_accounts 1",self)
    #gc.collect()

    if len(account_list) > 0:

        # construct a g_list from list of accounts
        glst_ptr = None
        for elm in account_list:
            acc_ptr = ctypes.cast( elm.instance.__int__(), ctypes.POINTER( AccountOpaque ) )
            glst_ptr = glib_ctypes.libglib.g_list_prepend(glst_ptr,acc_ptr)
        glst_ptr = glib_ctypes.libglib.g_list_reverse(glst_ptr)

        print("0x%x"%ctypes.addressof(glst_ptr), file=sys.stderr)
        #print("0x%x"%ctypes.addressof(vwptr.contents), file=sys.stderr)
        #pdb.set_trace()

        trvwptr = hash(self)

        gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_view_account_set_selected_accounts(trvwptr, glst_ptr, show_last)

    #print("set_selected_accounts 2")
    #gc.collect()


def get_selected_accounts (self):

    pdb.set_trace()
    #print("get_selected_accounts 1",self)
    #gc.collect()

    trvwptr = hash(self)
    print("tree view",self, file=sys.stderr)
    print("tree view 0x%x"%trvwptr, file=sys.stderr)

    glst_ptr = gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_view_account_get_selected_accounts(trvwptr)

    print(glst_ptr)
    glst_ptr = ctypes.cast( glst_ptr, ctypes.POINTER( glib_ctypes.GListRaw ) )
    print(glst_ptr)
    
    glst_len = glib_ctypes.libglib.g_list_length(glst_ptr)
    print(glst_ptr)
    print(glst_len)

    curbook = sw_app_utils.get_current_book()

    # we need a much better way of doing this
    # need to be able to hook into the SWIG base functions using the
    # ctypes integer pointer value
    # - indexing through the list is slow as we scan the pointers each time
    acctype = swighelpers.get_swig_type("_p_Account")
    acc_lst = []
    glst_ptr_base = glst_ptr
    for irng in range(glst_len):
        #gelm1 = glib_ctypes.libglib.g_list_nth_data(glst_ptr_base,irng)
        gelm = glst_ptr.contents.data
        glst_ptr = glib_ctypes.g_list_next(glst_ptr)
        account_ptr = gelm
        print("account_ptr 0x%x"%account_ptr, file=sys.stderr)
        accinst = swighelpers.int_to_swig(account_ptr,acctype);
        #accinst = swighelpers.int_to_swig(account_ptr,"_p_Account")
        #qof_ptr = ctypes.cast( account_ptr, ctypes.POINTER( qof_ctypes.QofInstanceOpaque ) )
        #acc_guid = qof_ctypes.libgnc_qof.qof_instance_get_guid(qof_ptr)
        #acc_guid_str = "".join([ "%02x"%x for x in acc_guid.contents.data ])
        #acc_guid = gnucash.GUID.string_to_guid(acc_guid_str)
        #account = gnucash.GUID.AccountLookup(acc_guid,curbook)
        account = gnucash.Account(instance=accinst)
        acc_lst.append(account)

    #pdb.set_trace()

    glib_ctypes.libglib.g_list_free(glst_ptr_base)

    return acc_lst
