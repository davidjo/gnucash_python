
# wrapping gnucash GObjects is quite complicated
# we need to determine if we need to copy the data from python into the C class variables
# because the primary functions gnc_plugin_add_to_window and gnc_plugin_remove_from_window
# are called directly in gnc_main_window_add_plugin - so we cant override them
# - and these functions copy from the C class structure 
# to confuse matters there are class callbacks add_to_window, remove_from_window - but
# these are additional subclass only extension functions

# if we have to copy the data from python into the class structure
# then we need a function for this in the gir bindings - it does not seem to
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

#pdb.set_trace()

import gi

# now create a new plugin in python

from gi.repository import Gtk


try:
    from gi.repository import GObject
    from gi.repository import GncPlugin
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()


import girepo

#pdb.set_trace()

# with introspection GncPlugin needs a GncMainWindow definition
# we now have a proper GncMainWindow introspection gir/typelib
# thus when add_to_window is called the argument passed is
# a fully wrapped GncMainWindow object
# however this does not solve the issue of passing eg action entries
# as tuples - GncMainWindow is passing the C structures
import gnc_main_window


# define a function equivalent to N_ for internationalization
def N_(msg):
    return msg

if True:

    #pdb.set_trace()

    # whats the difference between these two items
    # GncPlugin.Plugin and GncPlugin.PluginClass??
    # well GncPlugin.Plugin is the GObject object for subclassing
    # GncPlugin.PluginClass is the class structure object

    print >> sys.stderr, GObject.type_query(GncPlugin.Plugin)
    typptr = GObject.type_query(GncPlugin.Plugin)
    print >> sys.stderr, "gtype",typptr.type_name
    print >> sys.stderr, "gtype",typptr.type
    print >> sys.stderr, "gtype",typptr.class_size
    print >> sys.stderr, "gtype",typptr.instance_size

    # this lists the properties
    print >> sys.stderr, GObject.list_properties(GncPlugin.Plugin)

    # this lists the signal names
    print >> sys.stderr, GObject.signal_list_names(GncPlugin.Plugin)

    BaseGncPlugin = GncPlugin.Plugin
    BaseGncPluginClass = GncPlugin.PluginClass


# for the moment save the plugins
python_plugins = {}


# lets not use subclasses of subclasses yet - NO
# - switching back to subclass of subclass - using multiple inheritance with
# metaclass seems fraught - unless manually merge the various base class attributes
# in __new__ other base class attributes seem to be ignored
# - still dont quite understand why a python subclass of a python subclass
# using __metaclass__ still calls parent metaclass functions if the sub subclass
# does not define __metaclass__

class GncPluginPython(BaseGncPlugin):

    __metaclass__ = girepo.GncPluginMeta

    __girmetaclass__ = GncPlugin.PluginClass

    # now create a python subclass of the basic GObject

    # this class must NOT define a valid plugin_name - that is the function of its subclasses
    # - we need to define the class variable name here so we get access to
    # the C GncPlugin.PluginClass structure - this is the function of the GncPluginMeta class
    # - to provide access to the C class structure
    # (we need to add the __girmetaclass__ class variable to define the gir class definition to use)

    plugin_name = None

    # we use the girepo tricks to 
    # create accessor functions for all structure items)
    # (SWIG could access these as wraps both structures (instance and class))

    # - this class provides a pure python re-implementation of gnc_plugin
    # - it needs to be a sub-class of GncPlugin in order to use the plugin manager
    # gnc_plugin_manager_add_plugin function
    # we use the trick that if the C GncPlugin class variables define nothing
    # (no actions, toggle_actions, important_actions or ui_filename) then
    # the base C gnc_plugin functions do nothing except call the class virtual
    # functions - add_to_window and remove_from_window
    # here we re-implement the gnc_plugin_add_to_window and gnc_plugin_remove_from_window
    # functionality in python

    # interesting - for GncPluginPage the class structure contains callbacks
    # but the primary function definition (eg gnc_plugin_page_create_widget) simply
    # calls the class callback - so dont have the same issue as for GncPlugin
    # - just need to assign the callbacks

    # a plugin is first loaded into the manager
    # (most plugins loaded in top-level.c)
    # the main window (gnc-main-window) gets the list of plugins from the manager
    # then calls the add to window function of each plugin


    # ah - this is something I think Ive missed - we can name the GType here
    __gtype_name__ = 'GncPluginPython'

    # for equvalency with C code make these class variables
    # as far as I can see variables in python (class or instance)
    # are independent of those variables in the underlying GType GObject

    actions_name = None

    plugin_actions = []

    plugin_toggle_actions = []

    plugin_important_actions = []

    ui_filename = None

    ui_xml_str = None


    def __init__ (self):

        #pdb.set_trace()

        # do we need to init the parent class - GncPlugin
        # do this or use gobject.GObject.__init__(self)
        super(GncPluginPython,self).__init__()
        #gncplugin.Plugin.__init__(self)
        #GncPlugin.Plugin.__init__(self)
        #BaseGncPlugin.__init__(self)

        # we cannot easily get access to the instance private data structure
        # without including the full private data struct

        print >> sys.stderr, "before super access class"

        #priv = self.access_class_data()
        priv = girepo.access_class_data(self)

        print >> sys.stderr, "after super access class"

        # sort of emulate the functions called in gnc_plugin.c
        # this is whats in the class_init function
        # this is auto-called after being setup by the gnc_plugin_get_type function

        # we cannot follow this form of the C code
        # because if class_init is defined in a subclass and we call this parent
        # __init__ function the following call will call the subclass version
        # in python we would have to add a super call to the parent class_init
        # in the subclass class_init
        #self.class_init()

        # gobjects have constructor function
        # again in python these would be called by super calls from subclasses
        #self.constructor(report)


        # we need to save each window add_to_window is called for
        self.saved_windows = {}


    def class_init (self):

        # this is the equivalent for the class init function
        # will this work as a classmethod for gir wrapping
        # following the C code this should initialize this classes parent class data

        print "doing parent class_init"

        #pdb.set_trace()

        # a finalize function is assigned here
        # again this is a function stored in the parent class - in this case the GObject
        # how is this done here

        pass


    @classmethod
    def new (cls):
        pdb.set_trace()

        #plugin_page = g_object_new( GNC_TYPE_PLUGIN_PAGE_REPORT,
        #                        "report-id", reportId, NULL );

        # call like this:
        #newplugin = Cgobject.pygobject_new(plugin_page)

        return newplugin


    # this is extremely scary - we have to re-implement gnc_plugin_add_to_window
    # and gnc_plugin_remove_from_window here because we are assuming the raw C
    # class private data elements are NULL (because we havent set them)
    # so the gnc-plugin.c implementations of these functions will skip the
    # UI updates so we have to do those updates here - which is actually good
    # for doing things in python
    # its important that subclasses of this do not define the C actions_name etc
    # - then the virtual function call they do will call this python function
    # NOTA BENE - the lowest subclass of this class needs to define the do_ functions

    def add_to_window (self, window, window_type):

        print >> sys.stderr, "called super add_to_window"
        #pdb.set_trace()

        # now this is confusing - this can be called multiple times
        # for each gnucash main window (we can have more than one)

        # in C the action groups/merge ids are stored in a per GncMainWindow
        # private data structure - merged_actions_table
        # for the moment store the windows per plugin in the plugin
        # - self.saved_windows

        if hash(window) in self.saved_windows:
            # what to do!!
            print "add called more than once same window!!"
            pdb.set_trace()
            print "add called more than once same window!!"

        if self.actions_name != None:

            # extend the functionality of the main window
            window = gnc_main_window.main_window_extend(window)

            (action_group, merge_id) = window.py_merge_actions(self.actions_name, self.plugin_actions, self.plugin_toggle_actions, self.ui_xml_str, self)

            # do we need to save window object - for safety lets not for the moment
            self.saved_windows[hash(window)] = (action_group, merge_id)

            if self.plugin_important_actions:

                #action_group = gnc_main_window.get_action_group(window, self.actions_name)
                action_group = window.get_action_group(self.actions_name)

                set_important_actions(action_group, self.plugin_important_actions)



    def remove_from_window (self, window, window_type):

        #print >> sys.stderr, "called super remove_from_window"
        #pdb.set_trace()
        #print >> sys.stderr, "called super remove_from_window"


        # extend the functionality of the main window
        window = gnc_main_window.main_window_extend(window)

        if hash(window) in self.saved_windows:

            (action_group, merge_id) = self.saved_windows[hash(window)]

            del self.saved_windows[hash(window)]

            pdb.set_trace()

            if self.actions_name != None:
                window.unmerge_actions(self.actions_name, action_group, merge_id)

        else:

            if self.actions_name != None:
                # what to do!!
                print "remove called and no saved window!!"
                pdb.set_trace()
                print "remove called and no saved window!!"



# re-implement in python these global functions of gnc-plugin.c
# - they are not part of the GncPlugin GType as do not have GncPlugin GType
# as first argument - they just call either gtk or gobject functions

def init_short_names (action_group, toolbar_labels):

    #pdb.set_trace()

    # the label is passed through the gettext function call in C
    # which I think looks for a translation

    for toolbar_label in toolbar_labels:
        action = action_group.get_action(toolbar_label[0])
        action.set_short_label(N_(toolbar_label[1]))


def set_important_actions (action_group, important_actions):

    pdb.set_trace()

    for imp_action in important_actions:
        action = action_group.get_action(imp_action)
        action.is_important = True

    if len(important_actions) > 3:
        raise RuntimeError("Too many important actions in set_important_actions!!")

def update_actions (action_group, action_names, property_name, value):

    #pdb.set_trace()
    if len(action_names) > 0: pdb.set_trace()
    # still not exactly sure how to set the property here

    for action_name in action_names:
        action = action_group.get_action(action_name)
        if action != None:
            #setattr(action, "set_"+
            action.set_property(property_name, value)
        else:
            #g_warning("No such action with name '%s' in action group %s (size %d)",
            #          action_names[i], gtk_action_group_get_name(action_group),
            #          g_list_length(gtk_action_group_list_actions(action_group)));
            print >> sys.stderr, "No such action with name '%s' in action group %s (size %d)"%( \
                      action_name, action_group.get_name(),
                      len(action_group.list_actions()))

if False:

    GObject.type_register(GncPluginPython)

    print >> sys.stderr, GObject.type_query(GncPluginPython)
    typptr = GObject.type_query(GncPluginPython)
    print >> sys.stderr, "gtype",typptr.type_name
    print >> sys.stderr, "gtype",typptr.type
    print >> sys.stderr, "gtype",typptr.class_size
    print >> sys.stderr, "gtype",typptr.instance_size

    #pdb.set_trace()

if True:

    # not sure about how to do subclasses yet
    # we appear to need a __girmetaclass__ attribute in this
    # class - even though GncPluginPython defines one
    # yes this really doesnt make sense - the only __metaclass__
    # definition is in GncPluginPython but that seems to cause the subclass
    # to call the GncPluginMeta except with arguments from the subclass
    # only!!
    # actually dont think the C GncPlugin GType was designed for multiple
    # subclassing - it doesnt make sense - each subclass cannot define
    # the plugin_name - only the lowest subclass definition could be used
    # only one level of subclassing makes sense

    class GncPluginPythonTest(GncPluginPython):

        __metaclass__ = girepo.GncPluginSubClassMeta

        #__girmetaclass__ = GncPlugin.PluginClass
        #__girmetaclass__ = BaseGncPluginClass

        plugin_name = "GncPluginPythonTest"

        def __init__ (self):
            print "python gobject","%x"%hash(self)
            print "python gtype obj klass %s address %x"%(str(self.__class__),hash(gi.GObject.type_class_peek(self)))
            super(GncPluginPythonTest,self).__init__()
            print "python gtype obj klass %s address %x"%(str(self.__class__),hash(gi.GObject.type_class_peek(self)))

    GObject.type_register(GncPluginPythonTest)

    print >> sys.stderr, GObject.type_query(GncPluginPythonTest)
    typptr = GObject.type_query(GncPluginPythonTest)
    print >> sys.stderr, "gtype",typptr.type_name
    print >> sys.stderr, "gtype",typptr.type
    print >> sys.stderr, "gtype",typptr.class_size
    print >> sys.stderr, "gtype",typptr.instance_size

    #pdb.set_trace()

    myplugin = GncPluginPythonTest()

    #pdb.set_trace()

    #print "junk"

