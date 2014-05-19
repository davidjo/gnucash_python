
# finally we need to create a new class
# to run reports in python

import sys

import pdb

import traceback


import gtk

import gobject

import ctypes

try:
    import _sw_app_utils
    #from gnucash import *
    #from _sw_core_utils import gnc_prefs_is_extra_enabled
    #import gtk
    pass
except Exception, errexc:
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

#pdb.set_trace()

import gncpluginpage

import gnc_plugin_page

import gnc_main_window

from pygkeyfile import GKeyFile





libglibnm = ctypes.util.find_library("libglib-2.0")
if libglibnm is None:
    raise RuntimeError("Can't find a libglib-2.0 library to use.")

libglib = ctypes.cdll.LoadLibrary(libglibnm)


libglib.g_log_remove_handler.argtypes = [ctypes.c_char_p, ctypes.c_uint]
libglib.g_log_remove_handler.restype = None



class QofBookOpaque(ctypes.Structure):
    pass



gncpluginpagetype = gobject.type_from_name('GncPluginPage')

gncpluginpagereporttype = gobject.type_from_name('GncPluginPageReport')


# strange  - it is here where the class init function is called

# this lists the properties
print >> sys.stderr, gobject.list_properties(gncpluginpagetype)

# this lists the signal names
print >> sys.stderr, gobject.signal_list_names(gncpluginpagetype)




# OK attempt to create a Python class for gnc_plugin_page

#pdb.set_trace()

tmppluginpage = gobject.new(gobject.type_from_name('GncPluginPage'))


def close_handler (arg):
    print "close handler called"
    pass



# add a Report object for details of each report
# not sure what to inherit from


class Report(object):

    def __init__ (self):
        self.report_name = "python-report"


# hmm - the actual graphics drawer is somehow in html
# - the Report class seems to be something else
# not sure whether should still do this
# for now using separate class to implement drawing
# maybe we use a Widget here??
class ReportView(object):

    def __init__ (self):
        # in html this create a new scrolled window in gnc_html_init
        #priv->container = gtk_scrolled_window_new( NULL, NULL );
        #gtk_scrolled_window_set_policy( GTK_SCROLLED_WINDOW(priv->container),
        #                                GTK_POLICY_AUTOMATIC,
        #                                GTK_POLICY_AUTOMATIC );
        # - lets do this here
        #self.widget = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self.widget = gtk.ScrolledWindow()
        self.widget.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)

    def show_url (self):
        # try drawing something here
        button = gtk.Button(label="My Button")
        self.widget.add(button)


# have a hash table for reports - this ensures the
# report objects are not deallocated
# for the moment use a global here
reports = {}

# for the moment save the pages
python_pages = {}


# now create a new plugin for python reports


class GncPluginPagePythonReport(type(tmppluginpage)):

    __gproperties__ = {
                       'report-id' : (gobject.TYPE_INT,              # type
                                      'integer report id',           # nick name
                                      'integer report id',           # description
                                      0,                             # min value
                                      2000000,                       # max value
                                      42,                            # default value
                                      gobject.PARAM_READWRITE),      # flags
                      }

    def __init__ (self, report_id):

        # do we need to init the parent class - GncPluginPage
        # do this or use gobject.GObject.__init__(self)
        gncpluginpage.PluginPage.__init__(self)

        cmtstr = """
    DEBUG( "report id = %d", reportId );
    plugin_page = g_object_new( GNC_TYPE_PLUGIN_PAGE_REPORT,
                                "report-id", reportId, NULL );
    DEBUG( "plugin_page: %p", plugin_page );
    DEBUG( "set %d on page %p", reportId, plugin_page );
    return GNC_PLUGIN_PAGE( plugin_page );
        """

        #pdb.set_trace()

        print >> sys.stderr, "before access private"

        priv = self.access_private_data()

        print >> sys.stderr, "after access private"

        # variables from the private data structure
        # do we need any of these
        # ah - some of these need to be gobject properties
        # but we still need the python instance
        self.reportId = 0
        self.component_manager_id = 0
        self.option_change_cb_id = None
        self.name_change_cb_id = None
        self.initial_report = None
        self.edited_reports = None
        self.need_reload = False
        self.reloading = False
        # thats another module we might need - gnc-html
        self.html = None
        self.container = None

        # sort of emulate the functions called in gnc_plugin_page_report.c
        # this is whats in the class_init function
        # this is auto-called after being setup by the gnc_plugin_page_report_get_type function
        self.class_init()

        # gobjects have constructor function
        self.constructor(report_id)



    def class_init(self):

        # this is 

        # Im not seeing anyway to access the private data from python

        #pdb.set_trace()

        # we need to set some parent items - how to do this??
        # we probably need to set all of these
        #gnc_plugin_page_class->plugin_name     = GNC_PLUGIN_PAGE_REPORT_NAME;

        print >> sys.stderr, "before set_plugin_name"

        # stupid boy - this is setting the plugin_name NOT the page_name!!
        #pdb.set_trace()
        self.set_class_init_data(plugin_name="GncPluginPagePythonReport")

        print >> sys.stderr, "after plugin_name"

        #gnc_plugin_page_class->create_widget   = gnc_plugin_page_report_create_widget;
        #gnc_plugin_page_class->destroy_widget  = gnc_plugin_page_report_destroy_widget;
        #gnc_plugin_page_class->save_page       = gnc_plugin_page_report_save_page;
        #gnc_plugin_page_class->recreate_page   = gnc_plugin_page_report_recreate_page;
        #gnc_plugin_page_class->page_name_changed = gnc_plugin_page_report_name_changed;
        #gnc_plugin_page_class->update_edit_menu_actions = gnc_plugin_page_report_update_edit_menu;
        #gnc_plugin_page_class->finish_pending   = gnc_plugin_page_report_finish_pending;

        print >> sys.stderr, "before set_callbacks"

        self.set_callbacks()

        print >> sys.stderr, "after set_callbacks"

        # need to add report-id as a property??

        print "junk"


    def constructor(self, report_Id):

        #
        # this calls the parent constructor
        # (how does this work in the pygobject universe??)
        # then gets the report-id property by scanning the properties passed as an argument
        #report_Id = self.get_property("report-id")

        self.constr_init(report_Id)

    def constr_init (self, report_id):

        #pdb.set_trace()

        # this sets the property in gnc_plugin_page_report
        self.set_property("report-id",report_id)

        # do some setup - for gnc_plugin_page_report lots of guile stuff
        #gnc_plugin_page_report_setup(self)
        self.report_setup()

        # need to set parent variables - are these properties?? yes!!
        # in the guile version 
        self.set_property("page-name", self.initial_report.report_name)
        self.set_property("page-uri", "default:")
        self.set_property("ui-description", "gnc-plugin-page-python-report-ui.xml")
        self.set_property("use-new-window", False)

        # not sure what type to convert this to yet
        curbook = _sw_app_utils.gnc_get_current_book()
        print >> sys.stderr, "curbook_ptr %x"%curbook.__long__()
        curbook_ptr = ctypes.cast( curbook.__long__(), ctypes.POINTER( QofBookOpaque ) )
        #pdb.set_trace()
        print >> sys.stderr, "curbook_ptr %x"%ctypes.addressof(curbook_ptr.contents)
        #pdb.set_trace()
        #self.add_book(ctypes.addressof(curbook_ptr.contents))
        self.add_book(curbook.__long__())
        #pdb.set_trace()

        cmtstr1 = """
    /* Create menu and toolbar information */
    action_group =
        gnc_plugin_page_create_action_group(parent,
                                            "GncPluginPageReportActions");
    gtk_action_group_add_actions( action_group,
                                  report_actions,
                                  num_report_actions,
                                  plugin_page );
    gnc_plugin_update_actions(action_group,
                              initially_insensitive_actions,
                              "sensitive", FALSE);
    gnc_plugin_init_short_names (action_group, toolbar_labels);
        """


    # note we define do_.... functions but call them as set_... or get__...

    def do_get_property (self, property):
        if property.name == 'report-id':
            return self.reportId
        else:
            raise AttributeError, 'unknown property %s' % property.name

    def do_set_property (self, property, value):
        if property.name == 'report-id':
            self.reportId = value
        else:
            raise AttributeError, 'unknown property %s' % property.name


    def report_setup(self):

        self.cur_report = None
        self.initial_report = None
        self.edited_reports = []
        self.name_change_cb_id = None

        report_id = self.get_property('report-id')

        # need to do something like this
        #if report_id in self.report_dict:

        self.initial_report = Report()


    def create_widget (self):

        # think we need to trap errors here before returning to C

        self.container = None

        try:

           self.container = gtk.Frame()
           self.container.set_shadow_type(gtk.SHADOW_NONE)

           # this calls gnc_html_get_widget in report system
           # whats the equivalent here?
           # will use variables with approx name in C until figure this further

           self.html = ReportView()

           self.container.add(self.html.widget)

           # is this available in app-utils
           # apparently not
           # otherwise need to do a ctypes call
           #pdb.set_trace()
           close_callback_type = ctypes.CFUNCTYPE(None,ctypes.c_void_p)

           self.component_manager_id = gnc_plugin_page.libgnc_apputils.gnc_register_gui_component("window-report", None, close_callback_type(close_handler), hash(self))

           #session = _sw_app_utils.gnc_get_current_session()
           session = gnc_plugin_page.libgnc_apputils.gnc_get_current_session()

           #_sw_app_utils.gnc_gui_component_set_session(self.component_manager_id, session)
           gnc_plugin_page.libgnc_apputils.gnc_gui_component_set_session(self.component_manager_id, session)

           # need this??
           #gnc_html_set_urltype_cb(priv->html, gnc_plugin_page_report_check_urltype);
           #gnc_html_set_load_cb(priv->html, gnc_plugin_page_report_load_cb, report);


           # this seems to be the major drawing bit
           # im going to sort of assume that this is what draws in the above created window
           #gnc_window_set_progressbar_window( GNC_WINDOW(page->window) );
           #gnc_html_show_url(priv->html, type, url_location, url_label, 0);
           #g_free(url_location);
           #gnc_window_set_progressbar_window( NULL );

           self.html.show_url()


           #g_signal_connect(priv->container, "expose_event",
           #                 G_CALLBACK(gnc_plugin_page_report_expose_event_cb), report);

           self.container.connect("expose_event", self.expose_event_cb)

           #gtk_widget_show_all( GTK_WIDGET(priv->container) );

           self.container.show_all()

           print "finished create_widget"

        except Exception, errexc:
           traceback.print_exc()
           pdb.set_trace()

        return self.container


    def destroy_widget (self):
        global python_pages
        print >> sys.stderr, "destroy_widget"
        try:

           gnc_plugin_page.libgnc_apputils.gnc_unregister_gui_component(self.component_manager_id)
           self.component_manager_id = 0
           del python_pages[self.reportId]

        except Exception, errexc:
           traceback.print_exc()
           pdb.set_trace()

    def save_page (self, arg1):
        print >> sys.stderr, "save_page"
        pdb.set_trace()

    @classmethod
    # this ought to be a class method but still not sorted this
    def recreate_page (cls, arg1, arg2, arg3):
        print >> sys.stderr, "recreate_page"
        pdb.set_trace()

    def window_changed (self, *args):
        print >> sys.stderr, "window_changed",len(args)
        pdb.set_trace()

    def page_name_changed (self, *args):
        print >> sys.stderr, "page_name_changed",len(args)
        #pdb.set_trace()

    def update_edit_menu_actions (self, arg1):
        print >> sys.stderr, "update_edit_menu_actions"
        pdb.set_trace()

    def finish_pending (self):
        print >> sys.stderr, "finish_pending"
        return not self.reloading


    def expose_event_cb (self, *args):
        print >> sys.stderr, "expose_event_cb callback"

        str1 = """
    priv = GNC_PLUGIN_PAGE_REPORT_GET_PRIVATE(page);
    ENTER( "report_draw" );
    if (!priv->need_reload)
    {
        LEAVE( "no reload needed" );
        return;
    }
    priv->need_reload = FALSE;
    gnc_window_set_progressbar_window( GNC_WINDOW(GNC_PLUGIN_PAGE(page)->window) );
    gnc_html_reload(priv->html);
    gnc_window_set_progressbar_window( NULL );
    LEAVE( "reload forced" );
        """

        if not self.need_reload:
            return



    # try as module method
    #@classmethod

def OpenReport (report_id, window):
    global python_pages
    # following the C the gnc_plugin_page_report_new has the report_id as argument
    # which is passed to the constructor as a property
    try:

        # Im  not sure whether should hang onto the myreport object
        # in gnucash it looks like gnc_main_window_open_page will save the
        # page pointer somewhere - and removed in gnc_main_window_close_page
        # yes - the page is saved in the installed_pages list by gnc_main_window_connect
        # called at end of gnc_main_window_open_page

        # check if already created the report
        # not sure if crashes Im seeing are due to object deletion or something
        # with creating same report twice
        if report_id in python_pages:
            print >> sys.stderr, "report already created",report_id
            return

        myreport = GncPluginPagePythonReport(report_id)

        # junkily stash the pointer in global to ensure not
        # deallocated 
        python_pages[report_id] = myreport

        windowp = hash(window)
        #windowp = ctypes.cast(windowp,ctypes.POINTER(gnc_main_window.GncMainWindowOpaque))
        #windowp = ctypes.cast(windowp,ctypes.c_void_p)
        myreportp = hash(myreport)
        #myreportp = ctypes.cast(myreportp,ctypes.POINTER(gnc_plugin_page.GncPluginPageOpaque))
        #myreportp = ctypes.cast(myreportp,ctypes.c_void_p)
        #pdb.set_trace()
        #print >> sys.stderr, "0x%x"%ctypes.addressof(windowp)
        #print >> sys.stderr, "0x%x"%ctypes.addressof(myreportp)
        print >> sys.stderr, "0x%x"%windowp
        print >> sys.stderr, "0x%x"%myreportp

        gnc_main_window.libgnc_gnomeutils.gnc_main_window_open_page(windowp,myreportp)

        #pdb.set_trace()
        print "junk1"

    except Exception, errexc:
        print >> sys.stderr, "OpenReport error:",str(errexc)
        pdb.set_trace()

#pdb.set_trace()

gobject.type_register(GncPluginPagePythonReport)

#tmpexampl = gobject.new(GncPluginPagePythonReport)
