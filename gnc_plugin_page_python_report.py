
# finally we need to create a new class
# to run reports in python

import sys

import os

import pdb

import traceback


import gtk

import gobject


#pdb.set_trace()


# great - after all this importing webkit locks gnucash up
# and just importing WebView doesnt help either
#print >> sys.stderr, "Before webview import"
#import webkit
#from webkit import WebView
# OK have pinned this down to the gobject.threads_init()
# this is called in the __init__.py for webkit - and this locks up in Python callback from menu
# the following does not include __init__.py and does not lock up
sys.path.insert(0,"/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages/webkit")
webkit = __import__("webkit")
#print >> sys.stderr, "After webview import"

# try accessing through gnucash type
#import gnchtmlwebkit

import ctypes

try:
    import _sw_app_utils
    from gnucash import *
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


# define a function equivalent to N_ for internationalization
def N_(msg):
    return msg


def close_handler (arg):
    print "close handler called"
    pass



# add a Report object for details of each report
# not sure what to inherit from

# hmm there seems to be a similar report class in scheme
# which stores details of the report

# for the moment lets use combo class
# still need to figure about report templates
# although for python different instances might be how to do it
# - the class is the template and each instance a specific report

# so report is going to be the base class and the different types
# become subclasses??


class Params_Data(object):
    def __init__ (self):
        self.win = None
        self.db = None
        self.options = None
        self.cur_report = None

class OptionsDB(object):
    def __init__ (self,options):
        pass


class Report(object):

    def __init__ (self):
        self.report_name = "python-report"

        self.report_editor_widget = None
        self.report_type = None

    def get_editor (self):
        return self.report_editor_widget

    def get_type (self):
        return self.report_type


    def default_params_editor (self, report, options):

       # somewhere a widget is stored for report editors
       editor = self.get_editor()
       if editor:
           editor.present()
       else:

           default_params_data = Params_Data()

           default_params_data.options = options
           default_params_data.cur_report = report
           default_params_data.db = OptionDB(self.default_params_data.options)

           rpttyp = self.get_report_type()
           tmplt = rpttyp.get_template()
           title = tmplt.get_template_name()

           default_params_data.win = DialogOption.OptionsDialog_New(title)

           default_params_data.win.build_contents(default_params_data.db)
           default_params_data.db.clean()

           default_params_data.win.set_apply_cb(default_params_data.win.apply_cb,default_params_data)
           default_params_data.win.set_help_cb(default_params_data.win.help_cb,default_params_data)
           default_params_data.win.set_close_cb(default_params_data.win.close_cb,default_params_data)

           default_params_data.win.widget()


# hmm - the actual graphics drawer is somehow in html
# - the Report class seems to be something else
# not sure whether should still do this
# for now using separate class to implement drawing
class HtmlView(object):

    def __init__ (self):

        # create raw widget here - no use of gnucash html stuff at all
        self.widget = gtk.ScrolledWindow()
        self.widget.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)

        # this is pywebkit access - fails - locks up the whole gnucash GUI
        self.webview = webkit.WebView()
        self.widget.add(self.webview)

        # use gnucash access to webkit
        #self.html = gnchtmlwebkit.HtmlWebkit()
        # note this creates the basic window widget internally
        # we get the widget via html.get_widget()
        #self.widget = self.html.get_widget()


    def show_url (self):
        # try drawing something here
        #button = gtk.Button(label="My Button")
        #self.widget.add(button)

        summary = "<html><body>You scored <b>192</b> points.</body></html>";

        #pdb.set_trace()

        self.webview.load_string(summary,"text/html", "UTF-8", "gnucash:report")

        #self.html.show_data(summary,len(summary))


# have a hash table for reports - this ensures the
# report objects are not deallocated
# for the moment use a global here
reports = {}

# for the moment save the pages
python_pages = {}


# now create a new plugin for python reports

STOCK_PDF_EXPORT = "gnc-pdf-export"

class GncPluginPagePythonReport(type(tmppluginpage)):


    # ah - this is something I think Ive missed - we can name the GType here
    __gtype_name__ = 'GncPluginPagePythonReport'

    # OK Im now thinking gobject warning messages were happening previously but just did not get the message

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

        #pdb.set_trace()

        # do we need to init the parent class - GncPluginPage
        # do this or use gobject.GObject.__init__(self)
        gncpluginpage.PluginPage.__init__(self)

        #pdb.set_trace()

        self.report_actions = [ \
           ("PythonFilePrintAction", gtk.STOCK_PRINT, N_("_Print Report..."), "<control>p",
            N_("Print the current report"),
            self.print_cb,
           ),
           ("PythonFilePrintPDFAction", STOCK_PDF_EXPORT, N_("Export as P_DF..."), None,
            N_("Export the current report as a PDF document"),
            self.exportpdf_cb,
           ),
           ("PythonEditCutAction", gtk.STOCK_CUT, N_("Cu_t"), None,
            N_("Cut the current selection and copy it to clipboard"),
            None
           ),
           ("PythonEditCopyAction", gtk.STOCK_COPY, N_("_Copy"), None,
            N_("Copy the current selection to clipboard"),
            self.copy_cb,
           ),
           ("PythonEditPasteAction", gtk.STOCK_PASTE, N_("_Paste"), None,
            N_("Paste the clipboard content at the cursor position"),
            None
           ),
           ("PythonViewRefreshAction", gtk.STOCK_REFRESH, N_("_Refresh"), "<control>r",
            N_("Refresh this window"),
            self.reload_cb,
           ),
           ("PythonReportSaveAction", gtk.STOCK_SAVE, N_("Save _Report Configuration"), "<control><alt>s",
            N_("Update the current report's saved configuration. "
            "The report will be saved in the file ~/.gnucash/saved-reports-2.4. "),
            self.save_cb,
           ),
           ("PythonReportSaveAsAction", gtk.STOCK_SAVE_AS, N_("Save Report Configuration As..."), "<control><alt><shift>s",
            N_("Add the current report's configuration to the `Saved Report Configurations' menu. "
            "The report will be saved in the file ~/.gnucash/saved-reports-2.4. "),
            self.save_as_cb,
           ),
           ("PythonReportExportAction", gtk.STOCK_CONVERT, N_("Export _Report"), None,
            N_("Export HTML-formatted report to file"),
            self.export_cb,
           ),
           ("PythonReportOptionsAction", gtk.STOCK_PROPERTIES, N_("_Report Options"), None,
            N_("Edit report options"),
            self.options_cb,
           ),
           ("PythonReportBackAction", gtk.STOCK_GO_BACK, N_("Back"), None,
            N_("Move back one step in the history"),
            self.back_cb,
           ),
           ("PythonReportForwAction", gtk.STOCK_GO_FORWARD, N_("Forward"), None,
            N_("Move forward one step in the history"),
            self.forw_cb,
           ),
           ("PythonReportReloadAction", gtk.STOCK_REFRESH, N_("Reload"), None,
            N_("Reload the current page"),
            self.reload_cb,
           ),
           ("PythonReportStopAction", gtk.STOCK_STOP, N_("Stop"), None,
            N_("Cancel outstanding HTML requests"),
            self.stop_cb,
           ),
           ]

        # note these action names must exist in above list!!
        self.toolbar_labels = [ \
           ("PythonFilePrintAction",      N_("Print")),
           ("PythonReportExportAction",   N_("Export")),
           ("PythonReportOptionsAction",  N_("Options")),
           ]

        self.initially_insensitive_actions = []

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

        ui_desc_path = os.path.join(os.environ['HOME'],'.gnucash','ui',"gnc-plugin-page-python-report-ui.xml")

        if not os.path.exists(ui_desc_path):
            print >> sys.stderr, "path does not exist", ui_desc_path
            pdb.set_trace()

        # need to set parent variables - are these properties?? yes!!
        # in the guile version 
        self.set_property("page-name", self.initial_report.report_name)
        self.set_property("page-uri", "default:")
        self.set_property("ui-description", ui_desc_path)
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

        # Create menu and toolbar information

        # do we need to keep this around??
        self.action_group = self.create_action_group("GncPluginPageReportActions")

        self.action_group.add_actions(self.report_actions,user_data=self)

        gncpluginpage.update_actions(self.action_group, self.initially_insensitive_actions, "sensitive", False)

        gncpluginpage.init_short_names (self.action_group, self.toolbar_labels)

        print "actions added"


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

           self.html = HtmlView()

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

           #pdb.set_trace()

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

    def save_page (self, keyfile, group):
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

    # args are (GtkAction *action, GncPluginPageReport *rep

    def forw_cb (self, action, rep):
        print "forw_cb called"
    def back_cb (self, action, rep):
        print "back_cb called"
    def reload_cb (self, action, rep):
        print "reload_cb called"
    def stop_cb (self, action, rep):
        print "stop_cb called"
    def save_cb (self, action, rep):
        print "save_cb called"
    def save_as_cb (self, action, rep):
        print "save_as_cb called"
    def export_cb (self, action, rep):
        print "export_cb called"
    def options_cb (self, action, rep):
        print "options_cb called"
        result = gnc_report_window_default_params_editor
        if result == None:
            #gnc_warning_dialog(GTK_WIDGET(gnc_ui_get_toplevel()), "%s",
            #                   _("There are no options for this report."));
            pass
        else:
            #gnc_plugin_page_report_add_edited_report(priv, priv->cur_report);
            pass
    def print_cb (self, action, rep):
        print "print_cb called"
    def exportpdf_cb (self, action, rep):
        print "exportpdf_cb called"
    def copy_cb (self, action, rep):
        print "copy_cb called"


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
