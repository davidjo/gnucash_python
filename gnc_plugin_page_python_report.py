# finally we need to create a new class
# to run reports in python

import sys

import os

import json

import pdb

import traceback


import gtk

import gobject


#pdb.set_trace()


import ctypes

try:
    # import my fixup module for the raw _sw_app_utils
    import sw_app_utils
    from gnucash import *
    #from _sw_core_utils import gnc_prefs_is_extra_enabled
    #import gtk
    pass
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

#pdb.set_trace()

import gncpluginpage
from gncpluginpage import PluginPage

import gnc_plugin_page

import gnc_main_window

from pygkeyfile import GKeyFile


import report_objects
from report_objects import Report

from gnc_html import HtmlView

from gnucash_log import ENTER


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
#print >> sys.stderr, gobject.list_properties(gncpluginpagetype)

# this lists the signal names
#print >> sys.stderr, gobject.signal_list_names(gncpluginpagetype)




# OK attempt to create a Python class for gnc_plugin_page

#pdb.set_trace()

tmppluginpage = gobject.new(gobject.type_from_name('GncPluginPage'))


# define a function equivalent to N_ for internationalization
def N_(msg):
    return msg


# define a simple function to convert the 64 bit hash to 32 bit
def hash32 (inhsh):
    return (inhsh - (inhsh >> 32)) & (2**32 - 1) 


def close_handler (arg):
    print >> sys.stderr, "close handler called"
    pdb.set_trace()
    pass


# for the moment save the pages
python_pages = {}


# now create a new plugin for python reports

STOCK_PDF_EXPORT = "gnc-pdf-export"

# this sort of worked prior to wrap of gncpluginpage using codegen
#class GncPluginPagePythonReport(type(tmppluginpage)):

class GncPluginPagePythonReport(PluginPage):

    # ah - this is something I think Ive missed - we can name the GType here
    __gtype_name__ = 'GncPluginPagePythonReport'

    # OK Im now thinking gobject warning messages were happening previously but just did not get the message

    __gproperties__ = {
                       'report-id' : (gobject.TYPE_INT,                       # type
                                      N_('The numeric ID of the report.'),    # nick name
                                      N_('The numeric ID of the report.'),    # description
                                      -1,                                     # min value
                                      gobject.G_MAXINT,                       # max value
                                      -1,                                     # default value
                                      gobject.PARAM_READWRITE),               # flags
                                      #gobject.PARAM_CONSTRUCT_ONLY | gobject.PARAM_READWRITE),      # flags
                                      # cant figure out how to use gobject.PARAM_CONSTRUCT_ONLY
                                      # not clear what the "constructor" is in python - __init__ ??
                                      # but using in constr_init is definitely not
                      }


    def __init__ (self, report):

        # do we need to init the parent class - GncPluginPage
        # do this or use gobject.GObject.__init__(self)
        gncpluginpage.PluginPage.__init__(self)

        # again we are passing the instance pointer in python rather than integer report id
        # - but the report instance contains the report id
        report_id = report.id
        print "init report_id",report_id

        # this property is set on the g_object_new statement
        self.set_property("report-id",report_id)

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
        self.constructor(report)



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

        print "junk2"


    def constructor (self, report):
        #pdb.set_trace()
        # why this??
        report_Id = -42;
        #
        # this calls the parent constructor
        # (how does this work in the pygobject universe??)
        # then gets the report-id property by scanning the properties passed as an argument
        report_Id = self.get_property("report-id")
        print "constructor report-id",report_Id

        # scheme passes the report_Id - in python we will pass the report instance
        self.constr_init(report)

    def constr_init (self, report):

        # again we are passing the instance pointer in python rather than integer report id
        # - but the report instance contains the report id
        report_id = report.id
        print "constr_init report-id","%x"%report_id
        #pdb.set_trace()

        # this sets the property in gnc_plugin_page_report
        # well thats what I thought it did
        # I dont get this - the C code sets this into the private variable reportId
        # I thought is where the property report-id is stored
        # so we store it, access it just to re-store it???
        self.set_property("report-id",report_id)
        print "constr_init get report-id","%x"%self.get_property("report-id")

        # do some setup - for gnc_plugin_page_report lots of scheme stuff
        #gnc_plugin_page_report_setup(self)
        self.report_setup(report)

        ui_desc_path = os.path.join(os.environ['HOME'],'.gnucash','ui',"gnc-plugin-page-python-report-ui.xml")

        if not os.path.exists(ui_desc_path):
            print >> sys.stderr, "path does not exist", ui_desc_path
            pdb.set_trace()

        # need to set parent variables - are these properties?? yes!!
        # in the scheme version 
        self.set_property("page-name", self.initial_report.report_type.name)
        self.set_property("page-uri", "default:")
        self.set_property("ui-description", ui_desc_path)
        self.set_property("use-new-window", False)

        # with wrapping module this now returns a gnucash python bindings Book instance
        curbook = sw_app_utils.get_current_book()
        #pdb.set_trace()
        # really need to make this function accept a Book instance
        self.add_book(curbook.instance.__long__())

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


    def report_setup(self, report):

        #pdb.set_trace()

        self.cur_report = None
        self.initial_report = None
	self.edited_reports = []
        self.name_change_cb_id = None

        report_id = self.get_property('report-id')
        print "report_setup",report_id

        # need to do something like this to follow scheme
        # currently do not need this - in python we pass the report instance
        #if report_id in Report.report_ids:
        #    report = Report.report_ids[report_id]

        self.initial_report = report

        # in scheme cur_report is another pointer to the report instance
        self.cur_report = self.initial_report

    def create_widget (self):

        # think we need to trap errors here before returning to C

        self.container = None

        try:

           # the does the creation of the html object (equivalent gnc_html_factory_create_html)
           # ignored calls about gnc_html_history
           # whats the equivalent here?
           # will use variables with approx name in C until figure this further

           self.html = HtmlView()

           self.container = gtk.Frame()
           self.container.set_shadow_type(gtk.SHADOW_NONE)

           # this is the gnc_html_get_widget call in report system
           self.container.add(self.html.widget)

           # is this available in app-utils
           # apparently not
           # otherwise need to do a ctypes call
           #pdb.set_trace()
           close_callback_type = ctypes.CFUNCTYPE(None,ctypes.c_void_p)

           self.component_manager_id = gnc_plugin_page.libgnc_apputils.gnc_register_gui_component("window-report", None, close_callback_type(close_handler), hash(self))
           # debugging - doesnt appear to have any effect
           #self.component_manager_id = gnc_plugin_page.libgnc_apputils.gnc_register_gui_component("window-report", None, None, None)

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

           # we dont need report - this is self
           # apparently we can add arguments here which will be added to end
           # of arguments for expose_event_cb
           self.container.connect("expose_event", self.expose_event_cb)

           #gtk_widget_show_all( GTK_WIDGET(priv->container) );

           self.container.show_all()

           #pdb.set_trace()

           print "finished create_widget"

        except Exception, errexc:
           traceback.print_exc()
           pdb.set_trace()

        return self.container


    def destroy_widget (self):


       # traceback for normal page - the close button calls destroy widget
       #0  0x0000000103e0be87 in gnc_unregister_gui_component ()
       #1  0x000000010003e434 in gnc_plugin_page_report_destroy_widget ()
       #2  0x0000000100213cd7 in gnc_main_window_close_page ()
       #3  0x0000000104f4ada6 in _g_closure_invoke_va ()
       #4  0x0000000104f6143e in g_signal_emit_valist ()
       #5  0x0000000104f625d4 in g_signal_emit ()
       #6  0x0000000104318615 in gtk_real_button_released ()

        global python_pages
        print >> sys.stderr, "destroy_widget"
        try:

           gnc_plugin_page.libgnc_apputils.gnc_unregister_gui_component(self.component_manager_id)
           self.component_manager_id = 0
           del python_pages[self.reportId]

        except Exception, errexc:
           traceback.print_exc()
           pdb.set_trace()

    def save_page (self, key_file, group_name):
        print >> sys.stderr, "save_page"
        # this is a biggy - the scheme version outputs the data needed to regenerate the report
        # - it appears to be saved under .gnucash/books in the .gcm for the book
        # - where scheme options are saved - which I think is a GKeyFile entity
        # maybe in python we can pickle the object 
        # ah - we just need to ensure save_page and recreate_page coordinate
        #pdb.set_trace()
        #ENTER("page %p, key_file %p, group_name %s"%(self, key_file, group_name))
        # so the basic page type and page name are stored by default
        # I think this saves various option blocks
        #itmcnt = 1
        #key_file.set_value(group_name, "PythonOptions%d"%itmcnt, self.cur_report.gen_save_text)
        # this saves the main report
        # for the moment we definitely need the guid
        # almost works but not quite as the value is a python object
        # for the moment create new dict with value as module and class name string
        #pdb.set_trace()
        pyitms = {}
        for key,val in report_objects.python_reports_by_guid.iteritems():
            pyitms[key] = "%s.%s"%(val.__class__.__module__,val.__class__.__name__)
        key_file.set_value(group_name, "PythonOptions", repr(pyitms))
        #key_file.set_value(group_name, "PythonOptions", json.dumps(report_objects.python_reports_by_guid))

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


    def expose_event_cb (self, widget, event):
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

    # args are GtkAction *action, GncPluginPageReport *rep
    # in our case rep is currently this class ie GncPluginPagePythonReport

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
        # not sure what class partitioning should be here yet
        # we have instance of this class for each report
        # ah - but we need separate instance for each variation of this report with
        # different options
        result = self.cur_report.edit_options()
        if result == None:
            #gnc_warning_dialog(GTK_WIDGET(gnc_ui_get_toplevel()), "%s",
            #                   _("There are no options for this report."));
            #parent = gnc_gui_get_toplevel()
            parent = None
            gtk.MessageDialog(parent,gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_WARNING,gtk.BUTTONS_CLOSE,N_("There are no options for this report."))
        else:
            self.add_edited_report(self.cur_report)
            pass
    def print_cb (self, action, rep):
        print "print_cb called"
    def exportpdf_cb (self, action, rep):
        print "exportpdf_cb called"
    def copy_cb (self, action, rep):
        print "copy_cb called"


    def add_edited_report (self, cur_report):
        self.edited_reports.append(cur_report)


    @classmethod
    def recreate_page (cls, window, key_file, page_group):
        print >> sys.stderr, "recreate_page",window, key_file, page_group
        # amazing - this is working - it being called if report was open on gnucash
        # close
        # now need to figure how to regenerate the report
        # call trace
        #0  0x000000010003dc58 in gnc_plugin_page_report_recreate_page ()
        #1  0x000000010021d33b in gnc_plugin_page_recreate_page ()
        #2  0x0000000100219aaf in gnc_main_window_restore_all_windows ()
        #3  0x00000001000a85b7 in gnc_restore_all_state ()
        #pdb.set_trace()
        #key_file.get_value(page_group,'PageType')
        #'GncPluginPagePythonReport'
        #key_file.get_value(page_group,'PageName')
        #'Hello, World'
        # I think somehow in scheme the saved strings are evaluated and that creates
        # the new report instance and defines the scheme integer report id
        # oh boy thats how to hack gnucash - the .gcm file contains the scheme code to generate
        # a new report by calls either to gnc:restore-report-by-guid-with-custom-template 
        # or normally gnc:restore-report-by-guid which is evaluated in the scheme version of
        # this function
        pyopts = key_file.get_value(page_group,'PythonOptions')
        print "recreate_page",pyopts
        # hmm - will this only have one key??
        pydict = eval(pyopts)
        report_guid = pydict.keys()[0]
        if report_guid in report_objects.python_reports_by_guid:
            new_report = Report(report_type=report_objects.python_reports_by_guid[report_guid])
            new_page = GncPluginPagePythonReport.OpenNewReport(new_report,window)
        else:
            # if we need to import the module
            #newmod = __import__(modnam, globals(), locals(), [subclsnam], -1)
            pass

        return new_page

    @classmethod
    def OpenNewReport (cls, report, window):
        global python_pages
        print >> sys.stderr, "OpenNewReport",window
        # we are currently passing the report instance rather than the integer report id
        # as scheme does - note that the report id is defined by report.id
        report_id = report.id
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

            myreportpage = GncPluginPagePythonReport(report)

            # junkily stash the pointer in global to ensure not
            # deallocated 
            python_pages[report_id] = myreportpage

            windowp = hash(window)
            #windowp = ctypes.cast(windowp,ctypes.POINTER(gnc_main_window.GncMainWindowOpaque))
            #windowp = ctypes.cast(windowp,ctypes.c_void_p)
            myreportp = hash(myreportpage)
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
            traceback.print_exc()
            print >> sys.stderr, "OpenReport error:",str(errexc)
            pdb.set_trace()

        return myreportpage


def OpenReport (report, window):
    GncPluginPagePythonReport.OpenNewReport(report, window)

#pdb.set_trace()

gobject.type_register(GncPluginPagePythonReport)

#tmpexampl = gobject.new(GncPluginPagePythonReport)


# right - what we need to do is split out the recreate_page
# as this needs to exist outside of an instance
# and not really figured out how to do this as a class method
# also we need to specially set the class gnc callback for this

# and now setup the callback - passing in the appropriate GType name
# note this sets into the GncPluginPage class structure of the GncPluginPagePythonReport GType
# - not the GncPluginPage class structure of the GncPluginPage GType
# only one class structure of a GType exists for all instances
# these callbacks are set into the parent class structure of GncPluginPagePythonReport
# and are the same for all instances of GncPluginPagePythonReport

gncpluginpage.set_recreate_callback("GncPluginPagePythonReport")


