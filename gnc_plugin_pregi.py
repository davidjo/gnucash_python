
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

import pdb


import gnc_main_window


# now create a new plugin in python


if True:

    # use codegen wrap

    import gncplugin
    from gncplugin import Plugin

    BaseGncPlugin = Plugin

elif False:

    # use SWIG wrap
    # THIS NEEDS MUCH WORK!!

    import gnome_utils
    from gnome_utils import GncPlugin

    BaseGncPlugin = GncPlugin

else:

    # use pygobject and ctypes access to gnc_plugin

    # see if can wrap into GncPlugin so can get stored in plugin manager
    # well we cant  - the issue is plugins store data in a private
    # structure which we dont have easy access to
    # so cannot use basic GObject - have no way to set the callback class variables

    # OK lets see if we can just use the GType directly
    # we may be able to if register type before usage
    # by calling the get_type function
    # great - this does work!!

    # well it does but still not figured out how to access
    # the private data of the GType - in particular when
    # it contains data we need access to

    import gobject

    gncplugintype = gobject.type_from_name('GncPlugin')

    # strange  - it is here where the class init function is called

    # this lists the properties
    #print >> sys.stderr, gobject.list_properties(gncplugintype)

    # this lists the signal names
    #print >> sys.stderr, gobject.signal_list_names(gncplugintype)


    # OK attempt to create a Python class for gnc_plugin

    # create a dummy instance in order to get correct type
    # and this will call gnc_plugin_init
    # if gnc_plugin_class_init has not been called it will be called
    # before gnc_plugin_init here

    #pdb.set_trace()

    #tmpgncplugintype = gobject.type_from_name('GncPlugin')
    tmpgncplugin = gobject.new(gobject.type_from_name('GncPlugin'))

    BadGncPlugin = gobject.type_from_name('GncPlugin')

    #print "GObject types"

    #print gobject.type_children(gobject.type_from_name('GncPlugin'))
    #print gobject.type_children(gobject.type_from_name('QofBook'))
    #print gobject.type_parent(gobject.type_from_name('GncPlugin'))
    #for gtyp in gobject.type_children(gobject.type_from_name('GObject')):
    #    print gtyp

    # this lists the properties
    # this is where gnc_date_edit_class_init is called
    # presumably will be called when need the the actual class instantiated
    print >> sys.stderr, gobject.list_properties(BadGncPlugin)

    # this lists the signal names
    print >> sys.stderr, gobject.signal_list_names(BadGncPlugin)

    print >> sys.stderr, dir(BadGncPlugin)


    BaseGncPlugin = type(tmpgncplugin)


#pdb.set_trace()


# for the moment save the plugins
python_plugins = {}


class GncPluginPython(BaseGncPlugin):

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
    __gtype_name__ = 'GcnPluginPython'


    # for equvalency with C code make these class variables
    # as far as I can see variables in python (class or instance)
    # are independent of those variables in the underlying GType GObject
    # still cant see anyway to access such variables except by some
    # helper functions in the wrapper
    # (except for SWIG which wraps both structures (instance and class)
    # and creates accessor functions for all structure items)

    plugin_name = None

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
        #super(GncPluginPython,self).__init__()
        gncplugin.Plugin.__init__(self)

        # we cannot easily get access to the instance private data structure
        # without including the full private data struct

        print >> sys.stderr, "before super access class"

        priv = self.access_class_data()

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
        # this does not work as a classmethod - we need an instance pointer
        # to use the codegen wrapped functions
        # unfortunately Im not seeing anyway to access the private data from python
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
    # its important that subclasses of this do not define the C actions_name
    # using the wrapper function set_class_init_data to prevent calls to the
    # C function from attempting to perform ui merge actions
    # - then the virtual function call they do will call this python function now
    # after set_callbacks

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

            # need to map the window somehow to a window object
            window = gnc_main_window.main_window_wrap(window)

            (action_group, merge_id) = window.merge_actions(self.actions_name, self.plugin_actions, self.plugin_toggle_actions, self.ui_xml_str, self)

            # do we need to save window object - for safety lets not for the moment
            self.saved_windows[hash(window)] = (action_group, merge_id)

            if self.plugin_important_actions:

                action_group = gnc_main_window.get_action_group(window, self.actions_name)

                set_important_actions(action_group, self.plugin_important_actions)



    def remove_from_window (self, window, window_type):

        #print >> sys.stderr, "called super remove_from_window"
        #pdb.set_trace()
        #print >> sys.stderr, "called super remove_from_window"

        # need to map the window somehow to a window object
        window = gnc_main_window.main_window_wrap(window)

        if hash(window) in self.saved_windows:

            (action_group, merge_id) = self.saved_windows[hash(window)]

            del self.saved_windows[hash(window)]

            # need to map the window somehow to a window object
            window = gnc_main_window.main_window_wrap(window)

            if self.actions_name != None:
                window.unmerge_actions(self.actions_name, action_group, merge_id)

        else:

            if self.actions_name != None:
                # what to do!!
                print "remove called and no saved window!!"
                pdb.set_trace()
                print "remove called and no saved window!!"


def set_important_actions (action_group, important_actions):

    # although this function is defined in the gnc-plugin.c file
    # it actually has nothing to do with the GncPlugin class
    # (the C first argument is the action_group)
    # make a module function

    print >> sys.stderr, "called set_important_actions"
    pdb.set_trace()
    print >> sys.stderr, "called set_important_actions"

    for imp_action in important_actions:
         action = action_group.get_action(imp_action)
         action.is_important = True
