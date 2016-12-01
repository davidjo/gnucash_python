# finally we need to create a new class
# to run reports in python

import sys

import os

import json

import pdb

import traceback


from gi.repository import GObject

from gi.repository import Gtk

from gi.repository import GLib


from gi.repository import URLType

from gi.repository import GncHtml

import girepo

#pdb.set_trace()

import ctypes

try:
    # import my fixup module for the raw _sw_app_utils
    import sw_app_utils
    from gnucash import *
    #from _sw_core_utils import gnc_prefs_is_extra_enabled
    #from gi.repository import Gtk
    pass
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

#pdb.set_trace()

# imported pygkeyfile here but not used??
# now is GLib.KeyFile
#from gi.repository import GLib


import gnc_main_window

import gnc_plugin

import gnc_html_ctypes

import report_objects
from report_objects import Report

from dialog_options import GncOptionDB

from gnc_html import HtmlView


import gnucash_log
from gnucash_log import ENTER


libglibnm = ctypes.util.find_library("libglib-2.0")
if libglibnm is None:
    raise RuntimeError("Can't find a libglib-2.0 library to use.")

libglib = ctypes.cdll.LoadLibrary(libglibnm)


libglib.g_log_remove_handler.argtypes = [ctypes.c_char_p, ctypes.c_uint]
libglib.g_log_remove_handler.restype = None



class QofBookOpaque(ctypes.Structure):
    pass

class ActionToolbarLabels(ctypes.Structure):
    _fields_ = [ ("action_name", ctypes.c_char_p),      # The name of the action.
                 ("label", ctypes.c_char_p),            # The alternate toolbar label to use 
               ]



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


# for the moment save the pages
python_pages = {}


# now create a new plugin for python reports

STOCK_PDF_EXPORT = "gnc-pdf-export"


if True:

    from gnc_plugin_page_gi import GncPluginPagePython
    #pdb.set_trace()

    #import pygihelpers

    #import pygigtkhelpers

    #from gnc_plugin_gi import GncPlugin

else:

    import gnome_utils
    from gnome_utils import GncPluginPage

    # can we do this??
    PluginPage = GncPluginPage


# We create a subclass of GncPluginPage via the python version
# note that gnucash creates a C subclass of GncPluginPage for GncPluginPageReport
# here we are doing this in python - therefore we re-implement in python
# methods/variables of GncPluginPageReport - fortunately GncPluginPageReport does not actually
# add new class variables
# so the python is paralleling the C code

class GncPluginPagePythonReport(GncPluginPagePython):

    __metaclass__ = girepo.GncPluginPageSubClassMeta

    #__girmetaclass__ = BasePluginPageClass


    plugin_name = "GncPluginPagePythonReport"

    tab_icon = None


    # ah - this is something I think Ive missed - we can name the GType here
    __gtype_name__ = 'GncPluginPagePythonReport'

    # OK Im now thinking gobject warning messages were happening previously but just did not get the message

    __gproperties__ = {
                       'report-id' : (int,                                    # type
                                      N_('The numeric ID of the report.'),    # nick name
                                      N_('The numeric ID of the report.'),    # description
                                      -1,                                     # min value
                                      GLib.MAXINT32,                          # max value
                                      -1,                                     # default value
                                      GObject.ParamFlags.READWRITE),          # flags
                                      #GObject.ParamFlags.CONSTRUCT_ONLY | GObject.ParamFlags.READWRITE),      # flags
                                      # cant figure out how to use GObject.ParamFlags.CONSTRUCT_ONLY
                                      # not clear what the "constructor" is in python - __init__ ??
                                      # but using in constr_init is definitely not
                      }


    def __init__ (self, report):

        # do we need to init the parent class - GncPluginPage
        # do this or use GObject.__init__(self)
        #GncPluginPage.PluginPage.__init__(self)
        super(GncPluginPagePythonReport,self).__init__()

        # again we are passing the instance pointer in python rather than integer report id
        # - but the report instance contains the report id
        report_id = report.id
        #print "init report_id",report_id
        gnucash_log.dbglog("init report_id",report_id)

        # this property is set on the g_object_new statement
        self.set_property("report-id",report_id)

        #pdb.set_trace()

        self.report_actions = [ \
           ("PythonFilePrintAction", Gtk.STOCK_PRINT, N_("_Print Report..."), "<control>p",
            N_("Print the current report"),
            self.print_cb,
           ),
           ("PythonFilePrintPDFAction", STOCK_PDF_EXPORT, N_("Export as P_DF..."), None,
            N_("Export the current report as a PDF document"),
            self.exportpdf_cb,
           ),
           ("PythonEditCutAction", Gtk.STOCK_CUT, N_("Cu_t"), None,
            N_("Cut the current selection and copy it to clipboard"),
            None
           ),
           ("PythonEditCopyAction", Gtk.STOCK_COPY, N_("_Copy"), None,
            N_("Copy the current selection to clipboard"),
            self.copy_cb,
           ),
           ("PythonEditPasteAction", Gtk.STOCK_PASTE, N_("_Paste"), None,
            N_("Paste the clipboard content at the cursor position"),
            None
           ),
           ("PythonViewRefreshAction", Gtk.STOCK_REFRESH, N_("_Refresh"), "<control>r",
            N_("Refresh this window"),
            self.reload_cb,
           ),
           ("PythonReportSaveAction", Gtk.STOCK_SAVE, N_("Save _Report Configuration"), "<control><alt>s",
            N_("Update the current report's saved configuration. "
            "The report will be saved in the file ~/.gnucash/saved-reports-2.4. "),
            self.save_cb,
           ),
           ("PythonReportSaveAsAction", Gtk.STOCK_SAVE_AS, N_("Save Report Configuration As..."), "<control><alt><shift>s",
            N_("Add the current report's configuration to the `Saved Report Configurations' menu. "
            "The report will be saved in the file ~/.gnucash/saved-reports-2.4. "),
            self.save_as_cb,
           ),
           ("PythonReportExportAction", Gtk.STOCK_CONVERT, N_("Export _Report"), None,
            N_("Export HTML-formatted report to file"),
            self.export_cb,
           ),
           ("PythonReportOptionsAction", Gtk.STOCK_PROPERTIES, N_("_Report Options"), None,
            N_("Edit report options"),
            self.options_cb,
           ),
           ("PythonReportBackAction", Gtk.STOCK_GO_BACK, N_("Back"), None,
            N_("Move back one step in the history"),
            self.back_cb,
           ),
           ("PythonReportForwAction", Gtk.STOCK_GO_FORWARD, N_("Forward"), None,
            N_("Move forward one step in the history"),
            self.forw_cb,
           ),
           ("PythonReportReloadAction", Gtk.STOCK_REFRESH, N_("Reload"), None,
            N_("Reload the current page"),
            self.reload_cb,
           ),
           ("PythonReportStopAction", Gtk.STOCK_STOP, N_("Stop"), None,
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

        #print >> sys.stderr, "before access private"

        #priv = girepo.access_private_data()

        #print >> sys.stderr, "after access private"

        # variables from the private data structure
        # do we need any of these
        # ah - some of these need to be gobject properties
        # but we still need the python instance
        self.reportId = 0
        self.component_manager_id = 0

        self.cur_report = None
        self.cur_odb = None
        self.option_change_cb_id = None

        self.initial_report = None
        self.initial_odb = None
        self.name_change_cb_id = None


        self.edited_reports = None

        self.need_reload = False

        self.reloading = False

        # thats another module we might need - gnc-html
        self.html = None
        self.container = None

        # these are not initialized in C
        # these seem to be new copies of the options database for a report
        # Im very confused by their usage
        self.initial_odb = None
        self.cur_odb = None

        # sort of emulate the functions called in gnc_plugin_page_report.c
        # this is whats in the class_init function
        # this is auto-called after being setup by the gnc_plugin_page_report_get_type function
        #self.class_init()

        # gobjects have constructor function
        self.constructor(report)

        #pdb.set_trace()



    def class_init(self):

        # this is the class init function
        # unfortunately Im not seeing anyway to access the private data from python

        # with gobject introspection access to virtual methods is available
        # so we prepend do_ to the following function names

        #pdb.set_trace()

        #gnc_plugin_page_class->create_widget   = gnc_plugin_page_report_create_widget;
        #gnc_plugin_page_class->destroy_widget  = gnc_plugin_page_report_destroy_widget;
        #gnc_plugin_page_class->save_page       = gnc_plugin_page_report_save_page;
        #gnc_plugin_page_class->recreate_page   = gnc_plugin_page_report_recreate_page;
        #gnc_plugin_page_class->page_name_changed = gnc_plugin_page_report_name_changed;
        #gnc_plugin_page_class->update_edit_menu_actions = gnc_plugin_page_report_update_edit_menu;
        #gnc_plugin_page_class->finish_pending   = gnc_plugin_page_report_finish_pending;

        # need to add report-id as a property??

        pass


    def constructor (self, report):
        #pdb.set_trace()
        # why this??
        #report_Id = -42;
        #
        # I dont understand the following C mess - this calls a parent constructor
        # (how does this work in the pygobject universe??)
        # then gets the report-id property by scanning the properties passed as an argument

        #0  0x000000010003ee71 in gnc_plugin_page_report_constructor ()
        #1  0x0000000104f5935a in g_object_new_internal ()
        #2  0x0000000104f59b32 in g_object_new_valist ()
        #3  0x0000000104f5a18a in g_object_new ()
        #4  0x000000010003bffa in gnc_plugin_page_report_new ()
        #5  0x000000010003c14b in gnc_main_window_open_report ()

        #
        # this calls the parent constructor
        # (how does this work in the pygobject universe??)
        # then gets the report-id property by scanning the properties passed as an argument
        #report_Id = self.get_property("report-id")

        # yes - here I think in C the reportId is passed - in python we are passing the report object
        # so ignore the above
        report_Id = report.id

        # the report.id is a sequential count of number of reports run in the current gnucash run
        #print "constructor report-id",report_Id

        # scheme passes the report_Id - in python we will pass the report instance
        self.constr_init(report)


    def constr_init (self, report):

        # again we are passing the instance pointer in python rather than integer report id
        # - but the report instance contains the report id
        report_id = report.id
        #print "constr_init report-id","%x"%report_id
        #pdb.set_trace()

        # this sets the property in gnc_plugin_page_report
        # well thats what I thought it did
        # I dont get this - the C code sets this into the private variable reportId
        # I thought is where the property report-id is stored
        # so we store it, access it just to re-store it???
        self.set_property("report-id",report_id)
        #print "constr_init get report-id","%x"%self.get_property("report-id")

        # do some setup - for gnc_plugin_page_report lots of scheme stuff
        #gnc_plugin_page_report_setup(self)
        self.report_setup(report)

        # need to figure out how to get preferences
        #use_new = gnc_prefs_get_bool(GNC_PREFS_GROUP_GENERAL_REPORT, GNC_PREF_USE_NEW)
        use_new = False

        # decided to construct full path here - in real gnucash only the filename is stored
        ui_desc_path = os.path.join(os.environ['HOME'],'.gnucash','ui',"gnc-plugin-page-python-report-ui.xml")

        if not os.path.exists(ui_desc_path):
            print >> sys.stderr, "path does not exist", ui_desc_path
            pdb.set_trace()

        # need to set parent variables - are these properties?? yes!!
        # in the scheme version 
        self.set_property("page-name", self.initial_report.report_type.name)
        self.set_property("page-uri", "default:")
        self.set_property("ui-description", ui_desc_path)
        self.set_property("use-new-window", use_new)

        # with wrapping module this now returns a gnucash python bindings Book instance
        curbook = sw_app_utils.get_current_book()
        self.add_book(curbook)

        # Create menu and toolbar information

        # do we need to keep this around??
        self.action_group = self.create_action_group("GncPluginPageReportActions")

        self.action_group.add_actions(self.report_actions,user_data=self)

        #pdb.set_trace()

        # these actions defined in gnc-plugin.c are not part of the GncPlugin GType
        # - now re-implemented in python as simply call various Gtk functions

        #GncPlugin.Plugin.update_actions(self.action_group, self.initially_insensitive_actions, "sensitive", False)

        gnc_plugin.update_actions(self.action_group, self.initially_insensitive_actions, "sensitive", False)

        #GncPlugin.Plugin.init_short_names(self.action_group, self.set_toolbar_labels(self.toolbar_labels))

        gnc_plugin.init_short_names(self.action_group, self.toolbar_labels)

        print "actions added"
        gnucash_log.dbglog("actions added")


    def set_toolbar_labels (self, toolbar_labels):
        # this attempts to convert the python tuple list
        # to the action_toolbar struct
        # IT DOES NOT WORK - because cannot assign pointers to structs
        pdb.set_trace()
        actlbllst = []
        for indx,actlbl in enumerate(self.toolbar_labels):
            actlbltmp = GncPlugin.action_toolbar_labels()
            actlbltmp.action_name = actlbl[0]
            actlbltmp.label = actlbl[1]
            actlbllst.append(actlbltmp)
        return actlbllst


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


    def get_cur_report (self):
        # junky little routine to access self.cur_report till figure out
        # overall calling pattern
        return self.cur_report

    def report_setup(self, report):

        #pdb.set_trace()

        self.cur_report = None
        self.initial_report = None
	self.edited_reports = []
        self.name_change_cb_id = None

        report_id = self.get_property('report-id')
        print "report_setup",report_id
        gnucash_log.dbglog("report_setup",report_id)

        # need to do something like this to follow scheme
        # currently do not need this - in python we pass the report instance
        #if report_id in Report.report_ids:
        #    report = Report.report_ids[report_id]

        self.initial_report = report

        #// all reports need [to be] saved immediately after they're created.
        #PINFO("set needs save");
        #report.set_needs_save(True)


    def load_cb (self, url_type, url_location, url_label):

        #pdb.set_trace()
        print "load_cb",str(url_type),url_location,url_label

        # we need to implement this - this is important for
        # getting the report to change on option changes

        #ENTER( "load_cb: type=[%s], location=[%s], label=[%s]",
        #       type ? type : "(null)", location ? location : "(null)",
        #       label ? label : "(null)" );

        #if url_type == 'report' and url_location[0:3] == 'id=':
        #    report_id = int(url_location[3:])
        #    #DEBUG( "parsed id=%d", report_id );
        #elif url_type == 'options' and url_location[0:10] == 'report-id=':
        #    report_id = int(url_location[10:])
        #    if report_id in Report.report_ids:
        #        inst_report = Report.report_ids[report_id]
        #        self.add_edited_report(inst_report)
        #    return
        #else:
        #    #LEAVE( " unknown URL type [%s] location [%s]", type, location )
        #    return

        # so first dont understand how this can be true
        # - report_setup sets initial_report
        # so I dont see how this is ever done
        # in C/scheme because we have passed report id we look it up here
        # and then do this - but this is impossible in python where
        # we pass the actual instance
        if self.initial_report == None:
            #if report_id in Report.report_ids:
            #    inst_report = Report.report_ids[report_id]
            #self.initial_report = inst_report
            self.initial_report.set_needs_save(True)
            self.initial_odb = GncOoptionDB(self.initial_report.options)
            self.name_change_cb_id = self.initial_odb.register_change_callback(self.refresh,"General", "Report name")

        # in scheme cur_report is another pointer to the report instance
        if self.cur_report != None and self.cur_odb != None:
            # unregister some callbacks
            self.cur_odb.unregister_change_callback(self.option_change_cb_id)
            self.cur_odb = None

        # but this is important
        # we need to the GncOptionDB here because if dont change options
        # we do not have options from the default_params_editor
        # as suspected when click on options icon we call default_params_editor and get
        # a new option database
        # after updating options using default_params_editor when get back into
        # this routine to actually display report we get another new option database
        # so looks like we need to ensure GncOptionDB will be garbage collected all the time
        # still not sorted why need so many copies
        self.cur_report = self.initial_report
        self.cur_odb = GncOptionDB(self.initial_report.options)

        # this is very important for reloading report on option change
        self.option_change_cb_id = self.cur_odb.register_change_callback(self.option_change_cb)

        # some history stuff not got into yet

    # apparently for gobject introspection virtual methods (which GI recognises)
    # are overridden  by adding do_ to their name

    def do_create_widget (self):

        #pdb.set_trace()
        print "do_create_widget"

        # calling stack showing report page html create stack
        #0  0x00000001001c6327 in gnc_html_init ()
        #1  0x0000000104f6aa13 in g_type_create_instance ()
        #2  0x0000000104f53bb8 in g_object_new_internal ()
        #3  0x0000000104f54fad in g_object_newv ()
        #4  0x0000000104f551ac in g_object_new ()
        #5  0x00000001001c743a in gnc_html_webkit_new ()
        #6  0x000000010003e6af in gnc_plugin_page_report_create_widget ()
        #7  0x000000010021e981 in gnc_plugin_page_create_widget ()
        #8  0x0000000100214220 in gnc_main_window_open_page ()
        #9  0x0000000100038cce in _wrap_gnc_main_window_open_report ()


        # call stack showing how we get to report renderer function
        # gnc_run_report calls the scheme gnc:report-run function
        # which eventually calls the renderer via
        # gnc:report-render-html (in report.scm)
        #0  0x00000001001a5bd4 in gnc_run_report ()
        #1  0x00000001001a5cf3 in gnc_run_report_id_string ()
        #2  0x00000001000408a3 in gnc_html_report_stream_cb ()
        #3  0x00000001001c853e in load_to_stream ()
        #4  0x00000001001c8d97 in impl_webkit_show_url ()
        #5  0x00000001001c5fb1 in gnc_html_show_url ()
        #6  0x000000010003e8d6 in gnc_plugin_page_report_create_widget ()

        # think we need to trap errors here before returning to C

        self.container = None

        try:

           # this code is emulating the gnc_plugin_page_report_create_widget function

           # this does the creation of the html object (equivalent gnc_html_factory_create_html)
           # note that gnc_html_factory_create_html simply calls gnc_html_webkit_new
           # - so we get the webkit GncHtml subclass not the GncHtml class
           # also note that we get a new instance of GncHtmlWebkit(GncHtml) for each new report page
           # ignored calls about gnc_html_history
           # whats the equivalent here?
           # will use variables with approx name in C until figure this further

           self.html = HtmlView()

           self.container = Gtk.Frame()
           # for some reason Gtk.ShadowType.NONE is not defined - even though it should be!!
           # plus Gtk.ShadowType knows its an enum and knows the values!!
           #self.container.set_shadow_type(Gtk.ShadowType.NONE)
           self.container.set_shadow_type(0)

           # this is the gnc_html_get_widget call in report system
           self.container.add(self.html.widget)

           # is this available in app-utils
           # apparently not
           # otherwise need to do a ctypes call
           close_callback_type = ctypes.CFUNCTYPE(None,ctypes.c_void_p)

           self.component_manager_id = sw_app_utils.libgnc_apputils.gnc_register_gui_component("window-report", None, close_callback_type(close_handler), hash(self))
           # debugging - doesnt appear to have any effect
           #self.component_manager_id = sw_app_utils.libgnc_apputils.gnc_register_gui_component("window-report", None, None, None)

           #session = _sw_app_utils.gnc_get_current_session()
           session = sw_app_utils.libgnc_apputils.gnc_get_current_session()

           #_sw_app_utils.gnc_gui_component_set_session(self.component_manager_id, session)
           sw_app_utils.libgnc_apputils.gnc_gui_component_set_session(self.component_manager_id, session)

           # need this??
           #gnc_html_set_urltype_cb(priv->html, gnc_plugin_page_report_check_urltype);

           # so far need this as this sets up for re-running report on option changes
           #gnc_html_set_load_cb(priv->html, gnc_plugin_page_report_load_cb, report);
           self.html.set_load_cb(self.load_cb)


           # this seems to be how the report is passed to the html processor
           # gnc_html_parse_url seems to generate a url_location and url_label
           # which are then passed to the gnc_html_show_url function
           # what all this mess seems to be doing is creating a url from components (gnc_build_url)
           # which is parsed back to components (gnc_html_parse_url)
           # - for the moment seems this essentially just copies id_name to url_location
           #DEBUG( "id=%d", priv->reportId )
           id_name = "id=%d"%self.reportId

           #pdb.set_trace()

           # great - build_url is defined in gnc_html.c but not in gnc_html.h
           # ctypes here we come!!

           child_name = gnc_html_ctypes.build_url( URLType.TYPE_REPORT, id_name, None )

           (url_type, url_location, url_label) = self.html.html.parse_url(child_name)

           #pdb.set_trace()


           # this seems to be the major drawing bit
           # im going to sort of assume that this is what draws in the above created window
           #gnc_window_set_progressbar_window( GNC_WINDOW(page->window) );
           #gnc_html_show_url(priv->html, type, url_location, url_label, 0);
           #g_free(url_location);
           #gnc_window_set_progressbar_window( NULL );

           # this is complicated now
           # if we follow the C/scheme self.cur_report is only defined
           # after the load_cb callback is called so cant pass report here
           # essentially here C/scheme passes the report Id then looks it
           # up in load_cb

           self.html.show_url(url_type,url_location,url_label,report_cb=self.get_cur_report)


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
           gnucash_log.dbglog("finished create_widget")

        except Exception, errexc:
           traceback.print_exc()
           pdb.set_trace()

        return self.container


    def do_destroy_widget (self):


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
        gnucash_log.dbglog_err("destroy_widget")
        try:

           sw_app_utils.libgnc_apputils.gnc_unregister_gui_component(self.component_manager_id)
           self.component_manager_id = 0
           del python_pages[self.reportId]

        except Exception, errexc:
           traceback.print_exc()
           pdb.set_trace()

    def do_save_page (self, key_file, group_name):
        print >> sys.stderr, "save_page"
        gnucash_log.dbglog_err("save_page")
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

    # this is checked if exists before calling
    # currently only defined for register pages
    #def do_window_changed (self, *args):
    #    print >> sys.stderr, "window_changed",len(args)
    #    gnucash_log.dbglog_err("window_changed",len(args))
    #    pdb.set_trace()

    def do_page_name_changed (self, *args):
        print >> sys.stderr, "page_name_changed",len(args)
        gnucash_log.dbglog_err("page_name_changed",len(args))
        #pdb.set_trace()

    def do_update_edit_menu_actions (self, arg1):
        print >> sys.stderr, "update_edit_menu_actions"
        gnucash_log.dbglog_err("update_edit_menu_actions")
        pdb.set_trace()

    def do_finish_pending (self):
        print >> sys.stderr, "finish_pending"
        gnucash_log.dbglog_err("finish_pending")
        return not self.reloading


    def option_change_cb (self):
        print >> sys.stderr, "option_change_cb callback"
        gnucash_log.dbglog_err("option_change_cb callback")
        if self.cur_report == None:
            return
        old_name = self.get_page_name()
        new_name = self.cur_odb.lookup_string_option('General','Report name',None)
        if new_name != old_name:
            # some name updating code
            # dont have good place - this is defined in gnc-main-window.c but its
            # 1st arg is a GncPluginPage so it should be in that class
            #main_window_update_page_name(pluginpage, new_name_escaped)
            pdb.set_trace()
            pass
        self.cur_report.set_dirty(True)
        self.need_reload = True
        self.html.reload()

    def history_destroy_cb (self, data):
        print >> sys.stderr, "history_destroy_cb callback"
        gnucash_log.dbglog_err("history_destroy_cb callback")

    def expose_event_cb (self, widget, event):
        print >> sys.stderr, "expose_event_cb callback"
        gnucash_log.dbglog_err("expose_event_cb callback")

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


    def gnc_get_export_type_choice (self, export_types):

        pass


    def gnc_get_export_filename (self, choice):

        if choice == None:
            file_type = N_("HTML")
        else:
            file_type = choice

        title = N_("Save %s To File"%file_type)

        # GNC_PREFS_GROUP_REPORT = "dialogs.report"
        default_dir = sw_app_utils.get_default_directory("dialogs.report")

        file_dialog = gnc_file.GncFileDialog()

        filepath = file_dialog.gnc_file_dialog(title, None, default_dir, file_dialog.GNC_FILE_DIALOG_EXPORT)

        if filepath.find('.') < 0:
            filepath = filepath + '.' + file_type.lower()

        if filepath == None or filepath == "":
            return None

        default_dir = os.path.dirname(filepath)
        # GNC_PREFS_GROUP_REPORT = "dialogs.report"
        sw_app_utils.set_default_directory("dialogs.report", default_dir)

        if os.path.exists(filepath):

            try:
                os.stat(filepath)
                errstr = None
            except OSError, osex:
                errstr = osex.strerror

            if errstr != None:

                fmt = N_("You cannot save to that filename.\n\n%s")
                errmsg = fmt%(filepath,errstr)

                gnome_utils_ctypes.gnc_error_dialog(None, errmsg)

                return None

            if not os.path.isfile(filepath):

                errmsg = N_("You cannot save to that filename.")

                gnome_utils_ctypes.gnc_error_dialog(None, errmsg)

                return None

            errmsg = N_("The file %s already exists. Are you sure you want to overwrite it?")

            if not gnome_utils_ctypes.gnc_verify_dialog(None, False, errmsg):
                return None

        return filepath


    # args are GtkAction *action, GncPluginPageReport *rep
    # in our case rep is currently this class ie GncPluginPagePythonReport

    def forw_cb (self, action, rep):
        print "forw_cb called"
        gnucash_log.dbglog("forw_cb called")
    def back_cb (self, action, rep):
        print "back_cb called"
        gnucash_log.dbglog("back_cb called")
    def reload_cb (self, action, rep):
        print "reload_cb called"
        gnucash_log.dbglog("reload_cb called")
    def stop_cb (self, action, rep):
        print "stop_cb called"
        gnucash_log.dbglog("stop_cb called")
    def save_cb (self, action, rep):
        print "save_cb called"
        gnucash_log.dbglog("save_cb called")
    def save_as_cb (self, action, rep):
        print "save_as_cb called"
        gnucash_log.dbglog("save_as_cb called")
    def export_cb (self, action, rep):
        print "export_cb called"
        gnucash_log.dbglog("export_cb called")
        # this appears to allow for a definition in the report template
        # not fully implementing this
        export_types = None
        export_proc = None
        if hasattr(self.cur_report,"export_types"):
            export_types = self.cur_report.export_types
        if hasattr(self.cur_report,"export_thunk"):
            export_proc = self.cur_report.export_thunk
        if type(export_types) == list and callable(export_proc):
            #choice = self.gnc_get_export_type_choice(export_types)
            if choice == None:
                return
        else:
            choice = None

        filepath = self.gnc_get_export_filename(choice)

        if filepath == None or filepath == "":
            return

        if choice != None:
            # I dont think I need self.cur_report - self will be cur_report
            # export_proc called??
            result = export_proc(self.cur_report, choice, filepath)
        else:
            result = self.html.export_to_file(filepath)
            print "export_to_file",result

        if not result:

            fmt = N_("Could not open the file %s. The error is %s")
            strerr = os.strerror(errno)
            errmsg = fmt%(filepath,strerr)
            gnome_utils_ctypes.gnc_error_dialog(None, errmsg)

        return
    def options_cb (self, action, rep):
        print "options_cb called"
        gnucash_log.dbglog("options_cb called")
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
            Gtk.MessageDialog(parent,Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.WARNING,Gtk.ButtonsType.CLOSE,N_("There are no options for this report."))
        else:
            self.add_edited_report(self.cur_report)
            pass
    def print_cb (self, action, rep):
        print "print_cb called"
        gnucash_log.dbglog("print_cb called")
    def exportpdf_cb (self, action, rep):
        print "exportpdf_cb called"
        gnucash_log.dbglog("exportpdf_cb called")
    def copy_cb (self, action, rep):
        print "copy_cb called"
        gnucash_log.dbglog("copy_cb called")


    def add_edited_report (self, cur_report):
        self.edited_reports.append(cur_report)


    @classmethod
    def recreate_page (cls, window, key_file, page_group):
        print >> sys.stderr, "recreate_page",window, key_file, page_group
        gnucash_log.dbglog_err("recreate_page",window, key_file, page_group)
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
        gnucash_log.dbglog("recreate_page",pyopts)
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
        gnucash_log.dbglog_err("OpenNewReport",window)
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
                gnucash_log.dbglog_err("report already created",report_id)
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
            #print >> sys.stderr, "OpenNewReport","0x%x"%ctypes.addressof(windowp)
            #print >> sys.stderr, "OpenNewReport","0x%x"%ctypes.addressof(myreportp)
            print >> sys.stderr, "OpenNewReport","0x%x"%windowp
            print >> sys.stderr, "OpenNewReport","0x%x"%myreportp
            gnucash_log.dbglog_err("0x%x"%windowp)
            gnucash_log.dbglog_err("0x%x"%myreportp)

            #pdb.set_trace()

            gnc_main_window.libgnc_gnomeutils.gnc_main_window_open_page(windowp,myreportp)

            #pdb.set_trace()

        except Exception, errexc:
            traceback.print_exc()
            print >> sys.stderr, "OpenReport error:",str(errexc)
            pdb.set_trace()

        return myreportpage


def OpenReport (report, window):
    GncPluginPagePythonReport.OpenNewReport(report, window)

#pdb.set_trace()

GObject.type_register(GncPluginPagePythonReport)

#tmpexampl = GObject.new(GncPluginPagePythonReport)


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

# must be done here as need to be after type registration

#GncPluginPage.set_recreate_callback("GncPluginPagePythonReport")


