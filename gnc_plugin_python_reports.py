# finally we need to create a new class
# to run plugins in python

import sys

import os

import json

import pdb

import traceback


import gtk

import gobject


#pdb.set_trace()


import ctypes


import sw_app_utils


import gnucash_log
from gnucash_log import ENTER

import gnc_plugin

from gnc_plugin import GncPluginPython

import gnc_main_window

import gnc_plugin_page_python_report

import python_menu_extensions

from python_menu_extensions import GncMenuItem, GncActionEntry

import report_objects



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



class GncPluginPythonReports(GncPluginPython):

    # ah - this is something I think Ive missed - we can name the GType here
    __gtype_name__ = 'GncPluginPythonReports'

    # add properties/signals here
    #__gproperties__ =

    # I think these are more consistent if they are class variables
    # unfortunately cant figure out how to have a method of the class
    # in a class variable

    # the analysis is that essentially in gnucash plugins are single
    # instance classes

    def __init__ (self):

        #pdb.set_trace()

        super(GncPluginPythonReports,self).__init__()
        #GncPluginPython.__init__(self)

        self.class_init()

        # gobjects have constructor function
        #self.constructor(report)


        # load the report classes and create instances
        # first import the report definitions
        report_objects.load_python_reports()

        # now setup the menus
        self.load_python_reports_menu()



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

        # this follows the C code - the GncPlugin class private data is set in the
        # subclass class_init function - not by calling the GncPlugin classes own
        # class_init function!!

        #pdb.set_trace()

        # following the C code we set the parent GncPlugin class variables
        # in the subclass

        # dont quite see why these are class variables - this just follows the
        # C code currently

        GncPluginPythonReports.plugin_name = "GncPluginPythonReports"

        GncPluginPythonReports.actions_name = "GncPluginPythonReportsActions"


        GncPluginPythonReports.plugin_actions = [ \
            ("PythonReportsAction", None, "Python Reports...", None, "python reports tooltip", None),
            ("pythongenericAction", None, "Python reports description...", None, "python reports tooltip", self.reports_cb),
            #("exampleAction", None, N_("example description..."), None,
            # N_("example tooltip"),
            # self.cmd_test,
            #),
            ]

        GncPluginPythonReports.plugin_toggle_actions = []

        GncPluginPythonReports.plugin_important_actions = []

        GncPluginPythonReports.ui_filename = None

        GncPluginPythonReports.ui_xml_str = """<ui>
  <menubar>
    <menu name="Reports" action="ReportsAction">
      <placeholder name="OtherReports">
        <menu name="PythonReports" action="PythonReportsAction">
          <placeholder name="PythonReportsholder">
          </placeholder>
        </menu>
     </placeholder>
    </menu>
  </menubar>
</ui>
"""
        #fdes = open("/Users/djosg/.gnucash/ui/python-example-plugin.xml",'w')
        #fdes.write(ui_xml)
        #fdes.close()


        # first call the parent class_init - this is only way to do this
        # if we add the parent class_init call to the parent __init__
        # we will call the subclass class_init at that time
        # watch positioning!! - do after class variable defines for safety
        super(GncPluginPythonReports,self).class_init()


        #pdb.set_trace()

        print >> sys.stderr, "before access class"

        priv = self.access_class_data()

        print >> sys.stderr, "after access class"


        # we need to set some parent items - how to do this??
        # we probably need to set all of these
        #gnc_plugin_class->plugin_name     = GNC_PLUGIN_NAME;

        print >> sys.stderr, "before super set_plugin_name"

        print "junk",self.plugin_name,self.actions_name

        # define special C function in the wrappers to set the class private data
        # it appears to be confirmed the following works
        # but prefixing with cls. does not - get needs an argument error
        #cls.set_class_init_data(plugin_name=cls.plugin_name, actions_name=cls.actions_name)
        #pdb.set_trace()
        self.set_class_init_data(plugin_name=self.plugin_name, actions_name=self.actions_name)

        print >> sys.stderr, "before super set_callbacks"

        # and another special C function in the wrappers to set the callbacks
        # in the class private data
        self.set_callbacks()

        #print >> sys.stderr, "after set_callbacks"


    def plugin_init (self):
        gnucash_log.dbglog_err("python only plugin_init called")

    # unfortunately looks as though this wont work because of GIL issues
    # - in the python C plugin we lock the callback and plugin_finalize
    # this is crashing when we try a second call

    def plugin_finalize (self):
        gnucash_log.dbglog_err("python only plugin_finalize called")


    # note that in the C the primary version of these functions are defined in
    # gnc-plugin.c - and at the end of their code they call the functions saved
    # in the GncPlugin class private data - if they are defined
    # in python this gets sort of inverted - we define functions here to call
    # the parent GncPluginPython class version of these functions - before doing
    # extra work - and the GncPluginPython version of these functions does not
    # call functions of the subclass (how could it)

    def add_to_window (self, window, window_type):

        #pdb.set_trace()

        print >> sys.stderr, "called add_to_window"

        super(GncPluginPythonReports,self).add_to_window(window, window_type)

        # need to map the window somehow to a window object
        window = gnc_main_window.main_window_wrap(window)

        self.menu_extensions.add_to_window(window, window_type)


    def remove_from_window (self, window, window_type):

        #pdb.set_trace()

        # need to map the window somehow to a window object
        save_window = window
        window = gnc_main_window.main_window_wrap(window)

        self.menu_extensions.remove_from_window(window, window_type)

        #print >> sys.stderr, "called remove_from_window"
        #pdb.set_trace()
        #print >> sys.stderr, "called remove_from_window"

        super(GncPluginPythonReports,self).remove_from_window(save_window, window_type)



    def add_menuitems (self, name, rpt):
        # create the data needed for gtk.ActionGroup.add_actions
        title = N_("Report")+": "+N_(name)

        menuitm = GncMenuItem()
        ae = GncActionEntry()

        ae.name = rpt.report_guid
        if rpt.menu_name:
            ae.label = rpt.menu_name
        elif rpt.name:
            ae.label = rpt.name
        else:
            ae.label = name
        if rpt.menu_tip:
            ae.tooltip = rpt.menu_tip
        else:
            ae.tooltip = N_("Display the %s report"%name)
        ae.stock_id = None
        ae.accelerator = None
        ae.callback = self.reports_cb
        menuitm.ae = ae
        if rpt.menu_path:
            #menuitm.path = "ui/menubar/Reports/StandardReports/"+rpt.menu_path
            menuitm.path = "ui/menubar/Reports/OtherReports/PythonReports/PythonReportsholder/"
        else:
            menuitm.path = "ui/menubar/Reports/OtherReports/PythonReports/PythonReportsholder/"
        menuitm.name = ae.label
        menuitm.action = ae.name
        menuitm.type = gtk.UI_MANAGER_MENUITEM
        return menuitm


    def load_python_reports_menu (self):
        # this is effectively the replacement for gnc:add-report-template-menu-items
        # in report-gnome.scm

        #pdb.set_trace()

        menu_list = []
        for rpt in sorted(report_objects.python_reports_by_name.keys()):
            menu_list.append(self.add_menuitems(rpt,report_objects.python_reports_by_name[rpt]))

        group_name = self.actions_name+'MenuItems'

        # now need to update menu
        self.menu_extensions = python_menu_extensions.PythonMenuAdditions(group_name, menu_list)


    def reports_cb (self, actionobj, user_data=None):
        gnucash_log.dbglog_err("report_cb",actionobj,user_data)
        gnucash_log.dbglog_err("report_cb",actionobj.get_name())
        #(lambda (window)
        #  (let ((report (gnc:make-report
        #        (gnc:report-template-report-guid template))))
        #    (gnc-main-window-open-report report window)))))
        window = user_data

        # junk test
        trybook = sw_app_utils.get_current_book()

        try:
            # so we need either the report instance, guid or key name here
            # in scheme/C implementation what is passed here is an integer representing the scheme
            # report object - which is an "instance" of a report template
            # so finally understood the scheme process - the report is instantiated here
            # by the gnc:make-report - which returns the report id rather than an instance pointer
            # so question is do we maintain passing the id integer or go with passing the instance
            # pointer
            report_guid = actionobj.get_name()
            report_type = report_objects.python_reports_by_guid[report_guid]
            report = report_objects.Report(report_type=report_type)
            #gnc_plugin_page_python_report.GncPluginPagePythonReport.OpenReport(report,window)
            gnc_plugin_page_python_report.OpenReport(report,window)
            #gc.collect()
            gnucash_log.dbglog("call back done")
        except Exception, errexc:
            traceback.print_exc()
            print >> sys.stderr, "error in reports_cb callback",str(errexc)


# gdb call back for report
#0  0x0000000100040898 in gnc_html_report_stream_cb ()
#1  0x00000001001c853e in load_to_stream ()
#2  0x00000001001c8d97 in impl_webkit_show_url ()
#3  0x00000001001c5fb1 in gnc_html_show_url ()
#4  0x000000010003e8d6 in gnc_plugin_page_report_create_widget ()
#5  0x000000010021e981 in gnc_plugin_page_create_widget ()
#6  0x0000000100214220 in gnc_main_window_open_page ()


gobject.type_register(GncPluginPythonReports)


