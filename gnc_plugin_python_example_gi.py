# finally we need to create a new class
# to run plugins in python

import sys

import os

import json

import pdb

import traceback


import gtk

import gobject

import girepo


#pdb.set_trace()


import ctypes


import gnucash_log
from gnucash_log import ENTER

import girepo

import gi

import gnc_plugin

from gnc_plugin import BaseGncPlugin,BaseGncPluginClass
#from gnc_plugin import GncPluginPythonMixin
from gnc_plugin import GncPluginPython



# define a function equivalent to N_ for internationalization
def N_(msg):
    return msg


# define a simple function to convert the 64 bit hash to 32 bit
def hash32 (inhsh):
    return (inhsh - (inhsh >> 32)) & (2**32 - 1) 


def close_handler (arg):
    gnucash_log.dbglog_err("close handler called")
    pdb.set_trace()
    pass


class GncPluginPythonExample(GncPluginPython):

    __metaclass__ = girepo.GncPluginSubClassMeta

    #__girmetaclass__ = BaseGncPluginClass

    plugin_name = "GncPluginPythonExample"

    # ah - this is something I think Ive missed - we can name the GType here
    __gtype_name__ = 'GncPluginPythonExample'

    # add properties/signals here
    #__gproperties__ =

    # I think these are more consistent if they are class variables
    # unfortunately cant figure out how to have a method of the class
    # in a class variable

    # the analysis is that essentially in gnucash plugins are single
    # instance classes

    def __init__ (self):

        print "python gtype obj klass %s address %x"%(str(self.__class__),hash(gi.GObject.type_class_peek(self)))

        #pdb.set_trace()

        super(GncPluginPythonExample,self).__init__()
        #GncPluginPython.__init__(self)

        print "python gtype obj klass %s address %x"%(str(self.__class__),hash(gi.GObject.type_class_peek(self)))

        #pdb.set_trace()


        # following the C code we set the parent GncPlugin class variables
        # in the subclass

        # dont quite see why these are class variables - this just follows the
        # C code currently

        GncPluginPythonExample.actions_name = "GncPluginPythonExampleActions"


        GncPluginPythonExample.plugin_actions = [ \
               ("exampleAction", None, N_("Example Description..."), None,
                N_("example tooltip"),
                self.cmd_test,
               ),
               ]

        GncPluginPythonExample.plugin_toggle_actions = []

        GncPluginPythonExample.plugin_important_actions = []

        GncPluginPythonExample.ui_filename = None

        GncPluginPythonExample.ui_xml_str = """
<ui>
  <menubar>
    <menu name="Tools" action="ToolsAction">
      <placeholder name="ToolsPlaceholder">
        <menuitem name="example" action="exampleAction"/>
     </placeholder>
    </menu>
  </menubar>
</ui>
"""


        #pdb.set_trace()

        #print >> sys.stderr, "before access class"

        #priv = girepo.access_class_data()

        #print >> sys.stderr, "after access class"

        #GncPluginPythonExample.class_init()

        self.class_init()

        # gobjects have constructor function
        #self.constructor(report)


    # to follow the C code in python this should be a classmethod
    # however this does not appear to work for the codegen wrapped functions
    # - looks like you cannot use cls. as the prefix - complains about
    # missing argument - which Im assuming is the self object - so Im assuming
    # the cls object is not being passed as 1st argument
    #@classmethod
    #def class_init (cls):
    #    pass

    def class_init (self):

        # this is the class init function
        # unfortunately Im not seeing anyway to access the private data from python

        # first call the parent class_init - this is only way to do this
        # if we add the parent class_init call to the parent __init__
        # we will call the subclass class_init at that time
        #super(GncPluginPythonExample,self).class_init()

        # this follows the C code - the GncPlugin class private data is set in the
        # subclass class_init function - not by calling the GncPlugin classes own
        # class_init function!!

        #pdb.set_trace()

        # we need to set some parent items - how to do this??
        # we probably need to set all of these
        #gnc_plugin_class->plugin_name     = GNC_PLUGIN_NAME;

        print >> sys.stderr, "before super set_plugin_name"

        print "junk",self.plugin_name,self.actions_name

        # define special C function in the wrappers to set the class private data
        #pdb.set_trace()
        #self.set_class_init_data(plugin_name=self.plugin_name, actions_name=self.actions_name)

        print >> sys.stderr, "before super set_callbacks"

        # and another special C function in the wrappers to set the callbacks
        # in the class private data
        #self.set_callbacks()

        #print >> sys.stderr, "after set_callbacks"


    ## note that in the C the primary version of these functions are defined in
    ## gnc-plugin.c - and at the end of their code they call the functions saved
    ## in the GncPlugin class private data - if they are defined
    ## in python this gets sort of inverted - we define functions here to call
    ## the parent GncPluginPython class version of these functions - before doing
    ## extra work - and the GncPluginPython version of these functions does not
    ## call functions of the subclass (how could it)

    #def do_add_to_window (self, window, window_type):

    #    print >> sys.stderr, "called add_to_window"
    #    pdb.set_trace()

    #    #super(GncPluginPythonExample,self).add_to_window(window, window_type)

    #def do_remove_from_window (self, window, window_type):

    #    print >> sys.stderr, "called remove_from_window"
    #    pdb.set_trace()
    #    print >> sys.stderr, "called remove_from_window"

    #    #super(GncPluginPythonExample,self).remove_from_window(window, window_type)



    def cmd_test (self, action, data):

        print >> sys.stderr, " entered cmd_test"

        pdb.set_trace()

        print >> sys.stderr, " entered cmd_test"


#pdb.set_trace()

gobject.type_register(GncPluginPythonExample)


