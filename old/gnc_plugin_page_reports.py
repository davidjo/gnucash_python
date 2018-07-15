
# wrapping gnucash GObjects is quite complicated
# we need to determine if we need to copy the data from python into the C class variables
# because the primary functions gnc_plugin_add_to_window and gnc_plugin_remove_from_window
# are called directly in gnc_main_window_add_plugin - so we cant override them
# - and these functions copy from the C class structure 
# to confuse matters there are class callbacks add_to_window, remove_from_window - but
# these are additional subclass only extension functions

# if we have to copy the data from python into the class structure
# then we need a function for this in the codegen bindings - it does not seem to
# automatically handle the private class structure variables unless they are also
# properties!!

# when SWIG is applied to GObjects it creates 2 python classes
# one for the GType instance structure  and one for the class structure for the GType 
# (remember there is only one instantiation of the GType class structure - except that
# subclasses of the GType have a separate version of their parent GType class structure!!)
# the swig class has mechanisms to access the components of the structure
# - however SWIG does not seem to combine the two objects into an overall python class
# representing the GType

# however have now decided we DO only need to set the callback functions - we dont need
# to copy the data - on the analysis that the prime functions in gnc-plugin.c check
# if the class variables are NULL - and I assume they are if they are not set
# - but we MUST then re-implement gnc_plugin_add_to_window and gnc_plugin_remove_from_window
# functionality in python


import sys

import os

import traceback
import pdb


import gnc_main_window


# now create a new plugin in python


try:
    from gi.repository import GObject
    from gi.repository import GncPluginPage
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()



if True:

    pdb.set_trace()


    BaseGncPluginPage = GncPluginPage.PluginPageClass


#pdb.set_trace()


# for the moment save the plugins
python_plugins = {}


class GncPluginPagePython(BaseGncPluginPage):

    # now create a python subclass of the basic GObject
    # here we re-implement the gnc_plugin_add_to_window and gnc_plugin_remove_from_window
    # functionality

    # interesting - for GncPluginPage the class structure contains callbacks
    # but the primary function definition (eg gnc_plugin_page_create_widget) simply
    # calls the class callback - so dont have the same issue as for GncPlugin
    # - just need to assign the callbacks


    # when load a plugin
    # the plugin calls add to manager
    # the manager then calls the add to window function of the plugin


    # ah - this is something I think Ive missed - we can name the GType here
    __gtype_name__ = 'GcnPluginPagePython'


    def __init__ (self):

        pdb.set_trace()

        # do we need to init the parent class - GncPluginPage
        super(GncPluginPagePython,self).__init__()

