import sys
import os
import pdb

print >> sys.stderr, "trying plugin page"

try:
    #import _sw_app_utils
    #from gnucash import *
    #from _sw_core_utils import gnc_prefs_is_extra_enabled
    import gtk
    pass
except Exception, errexc:
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

print >> sys.stderr, "trying plugin page"

from ctypes import *

import gobject


from ctypes.util import find_library



gchar = c_char
gint = c_int
gboolean = gint
gcharp = POINTER(gchar)
GQuark = c_uint32
gsize = c_uint32
GType = gsize

GCallback = c_void_p


from pygkeyfile import GKeyFile


if True:

    # use codegen wrap

    import gncpluginpage
    from gncpluginpage import PluginPage

    BaseGncPluginPage = PluginPage

elif False:

    # use SWIG wrap
    # THIS NEEDS MUCH WORK!!

    import gnome_utils
    from gnome_utils import GncPluginPage

    BaseGncPluginPage = GncPluginPage


else:

    # use pygobject and ctypes access to gnc_plugin

    # attempt access to the gnc-plugin-page plugin

    # amazing this just worked!!
    # we now have the GncPluginPage as a type in python
    # the problem is there seems to be no python access to the extra functions
    # of the gnc-plugin-page class

    # so GncPluginPage has no SCM stuff
    # but the question is still how to use such types in python
    # so far I think we can get the type but all functions associated with it
    # are not in the type object and also dont know how to get to the private data
    # in python

    # it appears the basic GObject address is given by the hash of the python object

    # looks as though the only way to use subclassed GObject entities
    # is to create a python class which calls the functions via eg ctypes
    # or swig or an extension module

    # NOTA BENE - a GncPluginPage is NOT a subclass of GncPlugin!!


    gncpluginpagetype = gobject.type_from_name('GncPluginPage')


    # this lists the properties
    print >> sys.stderr, gobject.list_properties(gncpluginpagetype)

    # this lists the signal names
    print >> sys.stderr, gobject.signal_list_names(gncpluginpagetype)


    # can we create a new page
    #pdb.set_trace()

    #newpage = gobject.new(gncpluginpagetype)

    # at the time didnt seem possible to use the gncpluginpage directly


#pdb.set_trace()

# for the moment save the pluginpages??
#python_pluginpages = {}


class GncPluginPagePython(BaseGncPluginPage):

    # OK attempt to create a Python class for gnc_plugin_page

    # for GncPluginPage the class structure contains callbacks
    # but the primary function definition (eg gnc_plugin_page_create_widget) simply
    # calls the class callback - so dont have the same issue as for GncPlugin
    # - just need to assign the callbacks

    # ah - this is something I think Ive missed - we can name the GType here
    __gtype_name__ = 'GcnPluginPagePython'


    # these are the C class variables - we can access these using the special wrapper
    # function set_class_init_data
    # note these seem to be designed to be set by subclasses
    #plugin_name = None
    #tab_icon = None

    # we can ignore proper GObject signals - these are handled properly as GObjects

    #void (* inserted) (GncPluginPage *plugin_page);
    #void (* removed) (GncPluginPage *plugin_page);
    #void (* selected) (GncPluginPage *plugin_page);
    #void (* unselected) (GncPluginPage *plugin_page);

    # callbacks are added using special functions added in the codegen wrappers

    # these are the virtual functions defined
    # these simply need to be implemented in subclasses in python
    # the gnc_plugin_page functions simply call the virtual function
    #gnc_plugin_page_class->create_widget   = gnc_plugin_page_report_create_widget;
    #gnc_plugin_page_class->destroy_widget  = gnc_plugin_page_report_destroy_widget;
    #gnc_plugin_page_class->save_page       = gnc_plugin_page_report_save_page;
    #gnc_plugin_page_class->recreate_page   = gnc_plugin_page_report_recreate_page;
    #gnc_plugin_page_class->page_name_changed = gnc_plugin_page_report_name_changed;
    #gnc_plugin_page_class->update_edit_menu_actions = gnc_plugin_page_report_update_edit_menu;
    #gnc_plugin_page_class->finish_pending   = gnc_plugin_page_report_finish_pending;


    def __init__ (self):

        #pdb.set_trace()

        # do we need to init the parent class - GncPluginPage
        # do this or use gobject.GObject.__init__(self)
        #super(GncPluginPagePython,self).__init__()
        gncpluginpage.PluginPage.__init__(self)

        print >> sys.stderr, "before super access class"

        priv = self.access_class_data()

        print >> sys.stderr, "after super access class"


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
        # these very difficult to access without having to copy the private C structure
        # to the wrapping code
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


    # we MUST ensure the codegen functions are called here
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
        super(GncPluginPagePython,self).add_book(book.instance.__long__())

    def has_book (self, book):
        pdb.set_trace()
        retval = super(GncPluginPagePython,self).has_book(book.instance.__long__())
        return retval

    def has_books (self):
        pdb.set_trace()
        books = super(GncPluginPagePython,self).has_books()
        return self.books != None and len(self.books) != 0

