
import types

from gi.repository import Gtk

import pdb

pdb.set_trace()

#from function_class import \
#     ClassFromFunctions, extract_attributes_with_prefix, \
#     default_arguments_decorator, method_function_returns_instance, \
#     methods_return_instance, process_list_convert_to_instance, \
#     method_function_returns_instance_list, methods_return_instance_lists

from gnucash.gnucash_core import methods_return_instance,method_function_returns_instance, \
                                 method_function_returns_instance_list

# this is a problem - the Gtk functions are wrapped using GObject wrapping
# the gnucash methods are designed to work with swig wrapped functions
# - so the methods of function_class wont work to return GObject wrapped
# objects
# also need to deal with passing in objects that need to be converted to GObject objects

from pygobjectcapi import PyGObjectCAPI

INSTANCE_ARGUMENT = "instance"

def method_function_returns_gobject_instance(method_function, cls):
    """A function decorator that is used to decorate method functions that
    return instance data, to return instances instead.
    modified to deal with returning GObject wrapped objects
    - the swig wrap creates a simple swig pointer object

    You can't use this decorator with @, because this function has a second
    argument.
    """
    pdb.set_trace()
    assert( 'instance' == INSTANCE_ARGUMENT )
    def new_function(*args):
        print("new_function being CALLED")
        pdb.set_trace()
        kargs = { INSTANCE_ARGUMENT : method_function(*args) }
        if kargs['instance'] == None:
            # interesting I think this is a bugfix for my problem
            # - but it returns None so still have to test it
            #return None
            raise RuntimeError("Instance does not exist for class %s"%cls.__name__)
        else:
            #newobj = cls( **kargs )
            # note that here we loose the SWIG wrapper!!
            Cgobject = PyGObjectCAPI()
            obj_ptr = kargs[INSTANCE_ARGUMENT].__int__()
            newobj = Cgobject.to_object(obj_ptr)
            #if newobj.instance == None:
            #    raise RuntimeError("Instance does not exist for class 2 %s"%newobj.__class__.__name__)
            return newobj
            #return cls( **kargs )

    return new_function



from gnucash.gnucash_core import GnuCashCoreClass


import gnome_utils_c

import swighelpers


class GtkUIManager(GnuCashCoreClass):
    # the main window instance
    # must re-define _module
    _module = gnome_utils_c
    #_new_instance = 'xaccMallocAccount'
    pass


class GncMainWindow(GnuCashCoreClass):
    # the main window instance
    # must re-define _module
    _module = gnome_utils_c
    #_new_instance = 'xaccMallocAccount'
    pass

# we have a problem - the 3rd argument of gnc_main_window_manual_merge_actions
# in SWIG is SWIG GtkActionGroup type - we are passing pygobject objects
# this a big problem in gnucash - in python the GUI stuff will be GObject
# wrapped (manually or via introspection) whereas the gnucash objects
# (even if GObjects) are in this case wrapped by SWIG
# we could use type mapping in SWIG - but may need changing for introspection

# re-define the manual_merge_actions function to deal with GObject argument
def manual_merge_actions (self, group_name, group, merge_id):

    # this is really stupid but quick
    group_ptr = hash(group)
    group = swighelpers.int_to_swig(group_ptr,"_p_GtkActionGroup")

    self.swig_manual_merge_actions(group_name, group, merge_id)

# GncMainWindow
GncMainWindow.add_constructor_and_methods_with_prefix('gnc_main_window_', 'new')

GncMainWindow.get_uimanager = method_function_returns_gobject_instance(
    GncMainWindow.get_uimanager, Gtk.UIManager )

#setattr(GncMainWindow,"swig_manual_merge_actions") = GncMainWindow.manual_merge_actions
#setattr(GncMainWindow,"manual_merge_actions") = manual_merge_actions
GncMainWindow.swig_manual_merge_actions = GncMainWindow.manual_merge_actions
GncMainWindow.manual_merge_actions = manual_merge_actions

pdb.set_trace()

#GncMainWindow.get_book = method_function_returns_instance(
#    GncMainWindow.get_book, Book )

#GncMainWindow.book = property( GncMainWindow.get_book )

print("junk")

class GncPluginPage(GnuCashCoreClass):
    # the main window instance
    # must re-define _module
    _module = gnome_utils_c
    #_new_instance = 'xaccMallocAccount'
    pass

# GncPluginPage
pdb.set_trace()
GncPluginPage.add_constructor_and_methods_with_prefix('gnc_plugin_page_', 'new')

#GncPluginPage.get_book = method_function_returns_instance(
#    Session.get_book, Book )

#GncPluginPage.book = property( GncPluginPage.get_book )


print("junk")
