import sys
import os
import pdb

print("trying plugin page", file=sys.stderr)

try:
    #import _sw_app_utils
    #from gnucash import *
    #from _sw_core_utils import gnc_prefs_is_extra_enabled
    #from gi.repository import Gtk
    pass
except Exception as errexc:
    print("Failed to import!!", file=sys.stderr)
    pdb.set_trace()

print("trying plugin page", file=sys.stderr)

from ctypes import *

from gi.repository import GObject

import girepo


from pygobjectcapi import PyGObjectCAPI
#from pygobjectcapi_gi import PyGObjectCAPI


Cgobject = PyGObjectCAPI()

from ctypes.util import find_library



gchar = c_char
gint = c_int
gboolean = gint
gcharp = POINTER(gchar)
GQuark = c_uint32
gsize = c_uint32
GType = gsize

GCallback = c_void_p


#from gi.repository import GLib.KeyFile


# now create a new pluginpage in python


try:
    from gi.repository import GObject
    from gi.repository import GncPluginPage
except Exception as errexc:
    traceback.print_exc()
    print("Failed to import!!", file=sys.stderr)
    pdb.set_trace()


#pdb.set_trace()

BaseGncPluginPage = GncPluginPage.PluginPage
BaseGncPluginPageClass = GncPluginPage.PluginPageClass


#pdb.set_trace()

# for the moment save the pluginpages??
#python_pluginpages = {}


class GncPluginPagePython(BaseGncPluginPage, metaclass=girepo.GncPluginPageMeta):

    __girmetaclass__ = GncPluginPage.PluginPageClass

    # OK attempt to create a Python class for gnc_plugin_page

    # this class must NOT define a valid plugin_name - that is the function of its subclasses
    # - we need to define the class variable name here so we get access to
    # the C GncPluginPage.PluginPageClass structure - this is the function of the GncPluginPageMeta class
    # - to provide access to the C class structure
    # (we need to add the __girmetaclass__ class variable to define the gir class definition to use)
    # note these seem to be designed to be set by subclasses
    # (NOTE tab_icon does not seem to be used any more)
    plugin_name = None
    tab_icon = None

    # for GncPluginPage the class structure contains callbacks
    # but the primary function definition (eg gnc_plugin_page_create_widget) simply
    # calls the class callback - so dont have the same issue as for GncPlugin
    # - just need to assign the callbacks

    # ah - this is something I think Ive missed - we can name the GType here
    __gtype_name__ = 'GcnPluginPagePython'


    # we can ignore proper GObject signals - these are handled properly as GObjects

    #void (* inserted) (GncPluginPage *plugin_page);
    #void (* removed) (GncPluginPage *plugin_page);
    #void (* selected) (GncPluginPage *plugin_page);
    #void (* unselected) (GncPluginPage *plugin_page);

    # these are the virtual functions defined
    # these simply need to be implemented in subclasses in python
    # by prepending do_ to the following names
    #create_widget
    #destroy_widget
    #save_page
    #recreate_page
    #window_changed
    #page_name_changed
    #update_edit_menu_actions
    #finish_pending


    def __init__ (self):

        #pdb.set_trace()

        # do we need to init the parent class - GncPluginPage
        # do this or use GObject.GObject.__init__(self)
        super(GncPluginPagePython,self).__init__()

        print("before super access class", file=sys.stderr)

        priv = girepo.access_class_data(self)

        print("after super access class", file=sys.stderr)


        # NOTA BENE these are python only versions of these variables
        # if access is needed the base C variable we must use the direct
        # codegen function calls to set the variable

        # this lists the variables in use but we should try to ensure use
        # the C variables - in case a GncPluginPage function is called elsewhere
        # in the C code - in which will check the C variable
        # these only here for documentation
        # note that variables defined as properties are available by
        # using get_property/set_property

        # instance public data
        #self.window = None
        #self.notebook_page = None
        #self.summarybar = None

        # instance private data handle here
        # these are properties so can access using set_property/get_property
        #self.ui_description = None
        #self.use_new_window = None
        #self.page_name = None
        #self.page_color = None
        #self.uri = None
        #self.statusbar_text = None

        #self.ui_merge = None
        #self.action_group = None

        # non-property private variables
        # I dont think we need to worry about these as these are all set by
        # GncPluginPage function calls
        #self.merge_id = None
        #self.books = []
        #self.page_long_name = None

        # the actual code in the C init function
        #self.page_name = None
        #self.page_color = None
        #self.uri = None

        #self.window = None
        #self.summarybar = None


    def class_init (self):

        # this is the equivalent for the class init function
        # this does not work as a classmethod - we need an instance pointer
        # to use the codegen wrapped functions
        # unfortunately Im not seeing anyway to access the private data from python
        # following the C code this should initialize this classes parent class data

        # note in python we call this using a super call from a subclass

        #self.tab_icon = None
        #self.plugin_name = None

        # ah - if GObjects being used properly the GObjects will have the
        # properties and signals - we do not need to define them here

        pass


    # gnucash does weird things - a base class functionality often
    # simpy calls virtual functions from function pointers stored in the
    # class data
    # in python this can be ignored - we just have dummy definitions here
    # and implement the virtual functions in the subclass
    # - only if there is other code do we need functions in the base class
    # - and we just do this non-virtual function code

    # (a lot of the gnucash code can be ignored because python handles the garbage
    # collection/reference counting automagically)


    # we need to be very careful what we re-implement here - check very
    # carefully if we need to ensure that the codegen function is called
    # - because the C function updates private variables and if some function
    # involving those private variable(s) is called somewhere else in gnucash
    # we need to ensure the codegen functions are used here
    # a good example if the books private variable


    # def create_widget (self)
    #     # we could call the base C function with a super call here I think
    #     super(GncPluginPagePython,self).create_widget(...)

    # def destroy_widget (self)


    # not sure we need to implement this - the summarybar is part of instance data
    # - still not sure if can access via GObject though

    # def show_summarybar (self, visible):

    # def save_page (self, key_file, group_name):

    # this is an instance creation method so is special
    # @classmethod
    # def recreate_page (window, page_type, key_file, page_group):


    # we MUST ensure the C functions are called here
    # to ensure the C private variable books is updated
    # primarily because the gnc_plugin_page_has_book function is called by
    # gnc_main_window_open_page to create the page
    # we can either just not define these functions here
    # or maybe we can call the super class functions

    # yes - we have confirmed the following works
    # - useful as can now map the book class here rather than in the subclass
    # - we pass around the SWIG wrapped book object in general

    def add_book (self, book):
        #pdb.set_trace()
        # we need to convert from the SWIG gnucash book obj to the GObject type here
        book_ptr = book.instance.__int__()
        bookobj = Cgobject.to_object(book_ptr)
        super(GncPluginPagePython,self).add_book(bookobj)

    def has_book (self, book):
        pdb.set_trace()
        book_ptr = book.instance.__int__()
        bookobj = Cgobject.to_object(book_ptr)
        retval = super(GncPluginPagePython,self).has_book(bookobj)
        return retval

    def has_books (self):
        pdb.set_trace()
        books = super(GncPluginPagePython,self).has_books()
        return self.books != None and len(self.books) != 0

