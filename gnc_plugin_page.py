import sys
import os
import pdb

print >> sys.stderr, "trying plugin page"

try:
    #import _sw_app_utils
    #from gnucash import *
    #from _sw_core_utils import gnc_prefs_is_extra_enabled
    #import gtk
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


    # for equvalency with C code make these class variables

    plugin_name = None

    tab_icon = None

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

        print >> sys.stderr, "before super access private"

        priv = self.access_private_data()

        print >> sys.stderr, "after super access private"

        # instance private data handle here
        # these are properties
        self.action_group = None
        self.ui_merge = None
        self.ui_description = None
        self.use_new_window = None
        self.page_name = None
        self.page_color = None
        self.uri = None
        self.statusbar_text = None

        self.merge_id = None
        self.books = []
        self.page_long_name = None

        # the actual code in the C init function
        self.page_name = None
        self.page_color = None
        self.uri = None
        self.window = None
        self.summarybar = None


    def class_init (self):

        # this is the equivalent for the class init function
        # this does not work as a classmethod - we need an instance pointer
        # to use the codegen wrapped functions
        # unfortunately Im not seeing anyway to access the private data from python
        # following the C code this should initialize this classes parent class data

        # note in python we call this using a super call from a subclass

        self.tab_icon = None
        self.plugin_name = None

        # ah - if GObjects being used properly the GObjects will have the
        # properties and signals - we do not need to define them here


    # gnucash does weird things - a base class functionality often
    # simpy calls virtual functions from function pointers stored in the
    # class data
    # in python this can be ignored - we just have dummy definitions here
    # and implement the virtual functions in the subclass
    # - only if there is other code do we need functions in the base class
    # - and we just do this non-virtual function code

    # (a lot of the gnucash code can be ignored because python handles the garbage
    # collection/reference counting automagically)

    # def create_widget (self)

    # def destroy_widget (self)


    def show_summarybar (self, visible):

        if self.summarybar == None:
            return

        # check using correct gtk functions here!!
        if visible:
            self.summarybar.show()
        else:
            self.summarybar.hide()


    # def save_page (self, key_file, group_name):

    # this is an instance creation method so is special
    # @classmethod
    # def recreate_page (window, page_type, key_file, page_group):


    # not clear where to define this function - defined in gnc-plugin.c in C
    # but has no connection to the GncPlugin GObject
    # change the filename to an xml string - loaded externally
    # in python the ui_merge is assumed to be a pygtk gtk.UIManager object
    # all arguments should be non-null

    #def add_actions (ui_merge, action_group, filename):
    @staticmethod
    def add_actions (ui_merge, action_group, ui_xml_str):

        ui_merge.insert_action_group(action_group, 0)

        #merge_id = ui_merge.add_ui_from_file(filename)

        merge_id = ui_merge.add_ui_from_string(ui_xml_str)

        if merge_id:
            ui_merge.ensure_update()

        return merge_id


    def merge_actions (self, ui_merge):

        self.ui_merge = ui_merge

        self.merge_id = self.add_actions(self.ui_merge, self.action_group, self.ui_description)


    def unmerge_actions (self, ui_merge):

        self.ui_merge.remove_ui(self.merge_id)

        self.ui_merge.remove_action_group(self.action_group)

        self.ui_merge = None

        self.merge_id = 0


    def get_action (self, name):

        return self.action_group.get_action(name)

    def get_plugin_name (self):

        return self.plugin_name



    def do_get_property (self, property):
        if property.name == 'page-name':
            return self.page_name
        elit property.name == 'page-color':
            return self.page_color
        elit property.name == 'uri':
            return self.uri
        elit property.name == 'statusbar-text':
            return self.statusbar_text
        elit property.name == 'ui-description':
            return self.ui_description
        elit property.name == 'ui-merge':
            return self.ui_merge
        elit property.name == 'action-group':
            return self.action_group
        else:
            raise AttributeError, 'unknown property %s' % property.name

    def do_set_property (self, property, value):
        if property.name == 'page-name':
            self.page_name = value
        elit property.name == 'page-color':
            self.page_color = value
        elit property.name == 'uri':
            self.uri = value
        elit property.name == 'statusbar-text':
            self.statusbar_text = value
        elit property.name == 'ui-description':
            self.ui_description = value
        elit property.name == 'ui-merge':
            self.ui_merge = value
        elit property.name == 'action-group':
            self.action_group = value
        else:
            raise AttributeError, 'unknown property %s' % property.name



    # im not sure how we handle signals yet
    # all these functions do is to emit a signal??

    # def inserted (self):
    #     self.emit("inserted",0)

    # def removed (self):
    #     self.emit("removed",0)

    # def selected (self):
    #     self.emit("selected",0)

    # def unselected (self):
    #     self.emit("unselected",0)


    def add_book (self, book):

        self.books.append(book)


    def has_book (self, book):

        for tmp_book in self.books:
            if tmp_book == book:
                return True

        return False

    def has_books (self):

        return self.books != None and len(self.books) != 0

    def get_window (self);

        return self.window


    # all the properties seem to have get/set functions defined for them
    # why??

    def get_page_name (self):

        return self.page_name

    def set_page_name (self,name):

         self.page_name = name

         if self.page_name_changed:
             self.page_name_changed(name)


    def get_page_long_name (self):

        return self.page_long_name


    def set_page_long_name (self, name):

         self.page_long_name = name


    def get_ui_description (self):

       return self.ui_description

    def set_ui_description (self, ui_filename):

        self.ui_description = ui_filename

    def get_ui_merge (self):

        return self.ui_merge


    def create_action_group (self, group_name):

        group = gtk.ActionGroup(group_name)
        group.set_translation_domain("gnucash")

        self.action_group = group


    def get_action_group (self):

        return self.action_group
