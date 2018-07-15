
# the issue with crashes has been resolved as using transfer full instead
# of transfer none for the returned Account objects or list of Account objects
# using transfer full Im assuming that the py-gobject wrapping done in
# do_(g/s)et_selected_accounts of the swig account objects is releasing the
# underlying account gobject when the py-gobject wrapper is freed

# I suppose one solution would be to start with py-gobject wrapped accounts
# in the report options setup itself - and only convert to swig wrap
# when rendering report


import sys

import types

import gobject

import ctypes


import pdb

import gc


import sw_app_utils

import glib_ctypes

import gnome_utils_ctypes

import swighelpers

#import qof_ctypes


import gnucash

import gnucash.gnucash_core_c

from gnucash.gnucash_core_c import string_to_guid as gnucash_core_string_to_guid

#pdb.set_trace()

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

# check for introspection
# if so add current path to girepository paths

import os

# this is only for testing
if __name__ == '__main__':

    try:
        from gi.repository import GIRepository
    except ImportError:
        pass
    else:
        #pdb.set_trace()
        rep = GIRepository.Repository.get_default()
        addrep = os.path.join(sys.path[0],"girepository")
        rep.prepend_search_path(addrep)
        print("junk")
        # new feature - we apparently have no sys.argv
        # - fake up a null entry
        sys.argv = [ 'gnucash' ]


# be careful - if use wrong shared library can end up with
# weird errors eg not a subclass of GObject

#pdb.set_trace()

# so we can load these at this point
# (this probably will define GncTreeViewAccount, GncTreeView GTypes)
try:
    import gi
    # so we have big problems with circular references
    # if use full Qof definition instant crash on import of GncTreeViewAccount here
    # bootstrap version seems to work
    #gi.require_version('GncTreeView', '0.1')
    #gi.require_version('GncAccount', '0.1')
    #gi.require_version('QofIdType', '0.1')
    #gi.require_version('Qof', '0.1')
    #from gi.repository import GncTreeView
    #from gi.repository import QofIdType
    #from gi.repository import Qof
    #from gi.repository import GncAccount
    gi.require_version('GncTreeViewAccount', '0.1')
    from gi.repository import GncTreeViewAccount
    #from gi.repository import QofBook
    #from gi.repository import GLib
except Exception as errexc:
    pdb.set_trace()
    print("junk")

# so we have to use the following to create new GncTreeViewAccount objects
# but we do not get access to the additional functions the class defines
# only get access to the functions we have mapped for the parent classe(s)
# looks as though we need to add functions to the python side

#pdb.set_trace()

def new_with_root (root, show_root):
    pdb.set_trace()
    #newaccview = GncTreeViewAccountPython.new_with_root(root, show_root)
    newaccview = GncTreeViewAccount.TreeViewAccount.new_with_root(root, show_root)
    WrapTreeViewAccount(newaccview)
    return newaccview


def new (show_root):
    #pdb.set_trace()
    #newaccview = GncTreeViewAccount.TreeViewAccount.new(show_root)
    newaccview = GncTreeViewAccountPython.new(show_root)
    WrapTreeViewAccount(newaccview)
    return newaccview


# lets try a python subclass
# - no such luck - apparently the C constructors cannot be used to
# create subclasses (according to error message)
# and the following doesnt work - the class type returned from
# the new methods is the base class (GncTreeViewAccountPython.new)
# not the subclass

class GncTreeViewAccountPython(GncTreeViewAccount.TreeViewAccount):

    def __init__ (self):
        super(GncTreeViewAccountPython,self).__init__()

    @classmethod
    def new_with_root (cls, root, show_root):
        newobj = GncTreeViewAccount.TreeViewAccount.new_with_root(root, show_root)
        return newobj

    @classmethod
    def new (cls, show_root):
        newobj = GncTreeViewAccount.TreeViewAccount.new(show_root)
        return newobj

# lets go with a wrap
# well thats not going to work we need a widget object
# I guess we will just have to dynamically extend
# the issue is we need to replace some routines for argument
# fixing
# lets rename the routines with do_ as though a subclass virtual function


def WrapTreeViewAccount (newaccview):


    #for gtyp in gobject.type_children(gobject.type_from_name('GObject')):
    #    print("GType:",gtyp, file=sys.stderr)

    #for gtyp in gobject.type_children(gobject.type_from_name('QofInstance')):
    #    print("QofInstance GType:",gtyp, file=sys.stderr)

    # can we add an instance variable - yes but not useful!!
    #pdb.set_trace()
    #newaccview.accdict = {}

    # we dont really need to map these - we just call the base GObject function

    newaccview.do_get_headers_visible = types.MethodType(do_get_headers_visible, newaccview)

    newaccview.do_set_headers_visible = types.MethodType(do_set_headers_visible, newaccview)

    newaccview.do_get_selection = types.MethodType(do_get_selection, newaccview)

    newaccview.do_set_selection = types.MethodType(do_set_selection, newaccview)


    newaccview.do_get_view_info = types.MethodType(do_get_view_info, newaccview)

    newaccview.do_set_view_info = types.MethodType(do_set_view_info, newaccview)

    newaccview.do_get_cursor_account = types.MethodType(do_get_cursor_account, newaccview)

    newaccview.do_select_subaccounts = types.MethodType(do_select_subaccounts, newaccview)

    newaccview.do_set_selected_accounts = types.MethodType(do_set_selected_accounts, newaccview)

    newaccview.do_get_selected_accounts = types.MethodType(do_get_selected_accounts, newaccview)


if True:

    # these are simple call maps
    # we could just use these directly

    def do_set_headers_visible (self, make_visible):
        #pdb.set_trace()
        self.set_headers_visible(make_visible)

    def do_get_headers_visible (self):
        pdb.set_trace()
        return self.get_headers_visible()

    def do_get_selection (self):
        #pdb.set_trace()
        slctn = self.get_selection()
        return slctn

    def do_set_selection (self, slctn):
        # not used yet
        pdb.set_trace()
        self.set_selection(slctn)


    #  these functions need some emulation/type mapping

    def do_get_view_info (self):

        #pdb.set_trace()

        #vwinfo = AccountViewInfo()

        vwinfo = GncTreeViewAccount.AccountViewInfo()

        print(str(vwinfo),"0x%x"%hash(vwinfo), file=sys.stderr)

        self.get_view_info(vwinfo)

        return vwinfo

    def do_set_view_info (self, vwinfo):

        #pdb.set_trace()
        #print("set_view_info 1",self, file=sys.stderr)
        #gc.collect()

        print("0x%x"%hash(vwinfo), file=sys.stderr)

        self.set_view_info(vwinfo)

        #print("set_view_info 2", file=sys.stderr)
        #gc.collect()


    def do_get_cursor_account (self):

        pdb.set_trace()
        print("get_cursor_account", file=sys.stderr)

        # yet again calling the direct introspection returns a py-gobject wrapped object
        # which gets destroyed after this routine - and destroys the underlying Account object!!
        # NO - this is all because I had set the return as transfer full
        # - transfer none works!!

        #trvwptr = hash(self)
        #account_ptr = gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_view_account_get_cursor_account(trvwptr)

        #if account_ptr == None:
        #    return None

        accobj = self.get_cursor_account()

        if accobj == None:
            return None

        account_ptr = hash(accobj)

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

    def do_select_subaccounts (self, account):

        pdb.set_trace()
        print("select_subaccounts", file=sys.stderr)

        print(self, file=sys.stderr)
        print(account, file=sys.stderr)

        #account_ptr = ctypes.cast( account.instance.__int__(), ctypes.POINTER( AccountOpaque ) )

        #trvwptr = hash(self)

        #gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_view_account_select_subaccounts(trvwptr, account_ptr)

        accgobj = Cgobject.to_object(account.instance.__int__())

        self.select_subaccounts(accgobj)


    def do_set_selected_accounts (self, account_list, show_last):

        #pdb.set_trace()
        print("set_selected_accounts 1",str(self), file=sys.stderr)
        gc.collect()

        # the issue seems to be the initial SWIG wrapped account list objects
        # are being lost on 2nd option instantiation
        # my current guess is that the py-gobject wrapping done here of the
        # swig account objects is releasing the underlying account gobject
        # when the py-gobject wrapper is freed

        # so one option would be to just implement the ctypes version here

        # the quark key for instance data is PyGObject::instance-data
        # this seems to contain the type info as PyTypeObject

        print("set_selected_accounts 1",str(account_list), file=sys.stderr)

        if len(account_list) > 0:

            # the issue is we need to map from the SWIG bindings to py-gobject bindings!!
            # as it looks as though we need to store the py-gobject wraps
            # lets store them as a dict (hash) - then can look them up
            # in do_get_selected_accounts - rather than generating new swig wraps
            # each time
            acclst = []
            for accobj in account_list:
                acc_ptr = accobj.instance.__int__()
                print("set_selected_accounts 1a",str(accobj),accobj.GetName(), file=sys.stderr)
                print("set_selected_accounts 1a","%x"%acc_ptr, file=sys.stderr)
                accgobj = Cgobject.to_object(acc_ptr)
            #    if accgobj == None: pdb.set_trace()
            #    print("set_selected_accounts 1a",str(accgobj), file=sys.stderr)
            #    print("set_selected_accounts 1a","%x"%hash(accgobj), file=sys.stderr)
            #    if not hash(accgobj) in self.accdict:
            #        self.accdict[hash(accgobj)] = [accobj, accgobj]
                acclst.append(accgobj)
            #    # another option would be to create a GLib.List here
            #    # no such luck - it does not appear to be a true implementation
            #    # just a type definition

            print("set_selected_accounts 2",str(acclst), file=sys.stderr)

            self.set_selected_accounts(acclst, show_last)


            ## construct a g_list from list of accounts
            #glst_ptr = None
            #for accobj in account_list:
            #    acc_ptr = ctypes.cast( accobj.instance.__int__(), ctypes.POINTER( AccountOpaque ) )
            #    print("set_selected_accounts 1a",str(accobj),accobj.GetName(), file=sys.stderr)
            #    print("swig  0x%x"%accobj.instance.__int__(), file=sys.stderr)
            #    print("ctyps 0x%x"%ctypes.addressof(acc_ptr.contents), file=sys.stderr)
            #    glst_ptr = glib_ctypes.libglib.g_list_prepend(glst_ptr,acc_ptr)
            #    #self.accdict[accobj.instance.__int__()] = accobj
            #glst_ptr = glib_ctypes.libglib.g_list_reverse(glst_ptr)


            #print("0x%x"%ctypes.addressof(glst_ptr), file=sys.stderr)
            ##pdb.set_trace()


            #trvwptr = hash(self)
            #gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_view_account_set_selected_accounts(trvwptr, glst_ptr, show_last)


            #print("glst ptr 0x%x"%ctypes.addressof(glst_ptr), file=sys.stderr)
            #glib_ctypes.libglib.g_list_free(glst_ptr)


        print("set_selected_accounts 3", file=sys.stderr)
        gc.collect()


    def do_get_selected_accounts (self):

        #pdb.set_trace()
        print("get_selected_accounts 1",str(self), file=sys.stderr)
        gc.collect()

        # annoying - using introspection here isnt going to work either
        # - the gnucash C routine returns a list of py-gobject wrapped accounts
        # which get destroyed when the py-gobject wrapper is destroyed
        # NO - this is all because I had set the return as transfer full
        # - transfer none works!!

        # we cant use the do_set_selected_account SWIG wraps as we may
        # select something else entirely

        # this appears to be a plain python list of gobject wrapped account objects
        glst = self.get_selected_accounts()

        # this does not convert!!
        #print("tree view glst"%str(glst), file=sys.stderr)

        # we need a much better way of doing this
        # need to be able to hook into the SWIG base functions using the
        # ctypes integer pointer value
        # - indexing through the list is slow as we scan the pointers each time
        acc_lst = []
        acctype = swighelpers.get_swig_type("_p_Account")
        for gelm in glst:
            print("gelm ",str(gelm), file=sys.stderr)
            account_ptr = hash(gelm)
            print("account_ptr 0x%x"%account_ptr, file=sys.stderr)
            accinst = swighelpers.int_to_swig(account_ptr,acctype);
            account = gnucash.Account(instance=accinst)
        #    #accinst = swighelpers.int_to_swig(account_ptr,"_p_Account")
            acc_lst.append(account)

        #print("get_selected_accounts 1a",str(acc_lst), file=sys.stderr)


        #trvwptr = hash(self)
        #print("tree view",self, file=sys.stderr)
        #print("tree view 0x%x"%trvwptr, file=sys.stderr)

        #glst_ptr = gnome_utils_ctypes.libgnc_gnomeutils.gnc_tree_view_account_get_selected_accounts(trvwptr)

        #print(glst_ptr, file=sys.stderr)
        #glst_ptr = ctypes.cast( glst_ptr, ctypes.POINTER( glib_ctypes.GListRaw ) )
        #print(glst_ptr, file=sys.stderr)

        #glst_len = glib_ctypes.libglib.g_list_length(glst_ptr)
        #print(glst_ptr, file=sys.stderr)
        #print(glst_len, file=sys.stderr)

        ##curbook = sw_app_utils.get_current_book()

        ## we need a much better way of doing this
        ## now using dict lookup
        ## need to be able to hook into the SWIG base functions using the
        ## ctypes integer pointer value
        ## - indexing through the list is slow as we scan the pointers each time
        #acctype = swighelpers.get_swig_type("_p_Account")
        #acc_lst = []
        #glst_ptr_base = glst_ptr
        #for irng in range(glst_len):
        #    #gelm1 = glib_ctypes.libglib.g_list_nth_data(glst_ptr_base,irng)
        #    gelm = glst_ptr.contents.data
        #    glst_ptr = glib_ctypes.g_list_next(glst_ptr)
        #    account_ptr = gelm
        #    print("account_ptr 0x%x"%account_ptr, file=sys.stderr)
        #    accinst = swighelpers.int_to_swig(account_ptr,acctype);
        #    #accinst = swighelpers.int_to_swig(account_ptr,"_p_Account")
        #    account = gnucash.Account(instance=accinst)
        #    #qof_ptr = ctypes.cast( account_ptr, ctypes.POINTER( qof_ctypes.QofInstanceOpaque ) )
        #    #acc_guid = qof_ctypes.libgnc_qof.qof_instance_get_guid(qof_ptr)
        #    #acc_guid_str = "".join([ "%02x"%x for x in acc_guid.contents.data ])
        #    #acc_guid = gnucash.GUID.string_to_guid(acc_guid_str)
        #    #account = gnucash.GUID.AccountLookup(acc_guid,curbook)
        #    acc_lst.append(account)


        #pdb.set_trace()

        return acc_lst

