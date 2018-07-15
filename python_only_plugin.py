
# this is the original attempt at adding python extensions
# to the menus
# only left for testing purposes

import sys
import os
import pdb
import traceback
import gc


from gi.repository import GObject


import ctypes


# junky internationalization function
def N_(msg):
    return msg


#  junk test
import sw_app_utils


#pdb.set_trace()

try:
    #import _sw_app_utils
    #from gnucash import *
    #from _sw_core_utils import gnc_prefs_is_extra_enabled
    # we need to fake an argv
    # apparently sys.argv does not exist in side sub-interpreters
    # this fakes it for all subsequent usages I believe
    sys.argv = []
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
    pass
except Exception as errexc:
    traceback.print_exc()
    print("Failed to import!!", file=sys.stderr)
    pdb.set_trace()


gncmainwindowtype = GObject.type_from_name('GncMainWindow')


# this lists the properties
#print(GObject.list_properties(gncmainwindowtype), file=sys.stderr)

# this lists the signal names
#print(GObject.signal_list_names(gncmainwindowtype), file=sys.stderr)

#print(dir(gncmainwindowtype), file=sys.stderr)

# can we access a function in a python module via ctypes?
# - no because it needs to be a dylib not an so

#libcallback = ctypes.CDLL("/Users/djosg/.gnucash/python/pythoncallback.so")


#libcallback.gnc_python_callback.argtypes = [ ctypes.c_void_p, ctypes.c_void_p ]
#libcallback.gnc_python_callback.restype = None

#python_callbacktype = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)




import gnc_main_window

import gnc_plugin_page_python_report

import gnc_menu_extension


import report_objects


class GncMenuItem(object):
    def __init__ (self,path=None,ae=None,action=None,type=None):
        self.path = path
        self.ae = ae
        self.action = action
        self.type = type

class GncActionEntry(object):
    def __init__ (self,name=None,stock_id=None,label=None,accelerator=None,tooltip=None,callback=None):
        self.name = name
        self.stock_id = stock_id
        self.label = label
        self.accelerator = accelerator
        self.tooltip = tooltip
        self.callback = callback

    def as_tuple (self):
        return (self.name,self.stock_id,self.label,self.accelerator,self.tooltip,self.callback)



#import pythoncallback

# this works with the pythoncallback module
# NOTA BENE - pythoncallback module NOT used at the moment
# pass a callback saver object for the moment
class MyCallbacks(object):

    def __init__ (self):
        self.user_data = None
        self.callbacks = {}


class MyPlugin(GObject.GObject):

    def __init__(self):
        self.plugin_class_init()
        self.plugin_init()

    def plugin_class_init (self):
        print("plugin_class_init called", file=sys.stderr)
        # try creating the ui xml file here
        ui_xml = """<ui>
  <menubar>
    <menu name="Reports" action="ReportsAction">
      <placeholder name="OtherReports">
        <menu name="PythonReports" action="PythonReportsAction">
          <placeholder name="PythonReportsholder">
          </placeholder>
        </menu>
     </placeholder>
    </menu>
    <menu name="Tools" action="ToolsAction" >
      <placeholder name="ToolsPlaceholder">
        <menu name="PythonTools" action="PythonToolsAction">
          <placeholder name="PythonToolsholder">
            <menuitem name="Python Tools" action="pythongenericAction"/>
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

        # yes - we now can add menu items in python
        # we simply need the main window object wrapped either using
        # a gncmainwindow module or ctypes and pygobject_new from gobject module
        # (ctypes works now got right argument and return types)
        # currently using ctypes version
        # we apparently have to use the main window ui_merge object

        self.main_window = gnc_main_window.gnc_gui_init()
        self.main_ui_merge = self.main_window.get_uimanager()

        pdb.set_trace()

        self.merge_id = 0

        #accelgroup = self.main_ui_merge.get_accel_group()
        #self.main_window.add_accel_group(accelgroup)


        # Create an ActionGroup
        actiongroup = Gtk.ActionGroup('GncPythonMyPluginActions')
        self.actiongroup = actiongroup

        # create callback object
        #self.save_callbacks = MyCallbacks()

        # ok this whole issue may have been because of my stupidity with GIL Ensure
        #newcb = python_callbacktype(self.reports_cb)
        #pythoncallback.add_actions(self.save_callbacks, actiongroup, [ \
        actiongroup.add_actions([ 
            ("PythonReportsAction", None, "Python Reports...", None, "python reports tooltip", None),
            ("PythonToolsAction", None, "Python Tools...", None, "python tools tooltip", None),
            ("pythongenericAction", None, "Python tools description...", None, "python tools tooltip", self.tools_cb),
                 ], user_data=self.main_window)

            #("pythonreportsAction", None, "Python reports description...", None, "python reports tooltip", self.reports_cb),
            #("pythongenericAction", None, "Python tools description...", None, "python tools tooltip", self.tools_cb),
            #     ], user_data=self.main_window)

        self.main_ui_merge.insert_action_group(actiongroup,0)

        self.merge_id = self.main_ui_merge.add_ui_from_string(ui_xml)

        self.main_ui_merge.ensure_update()

        print("merge_id",self.merge_id)

        # load the report classes and create instances
        # first import the report definitions
        report_objects.load_python_reports()

        # now setup the menus
        self.load_python_reports_menu()

    def plugin_init (self):
        print("python only plugin_init called", file=sys.stderr)


    def load_python_reports_menu (self):
        # this is effectively the replacement for gnc:add-report-template-menu-items
        # in report-gnome.scm

        menu_list = []
        for rpt in report_objects.python_reports_by_name:
            menu_list.append(self.add_menuitems(rpt,report_objects.python_reports_by_name[rpt]))

        # now need to update menu
        # we cannot use the gnc-menu-extensions and gnc-plugin-menu-additions
        # as they are tied to scheme - because gnc-plugin-menu-additions gets its
        # list from gnc-menu-extensions which is totally tied to scheme
        self.menu_extensions = gnc_menu_extension.MyMenuAdditions(self.main_window)
        self.menu_extensions.add_to_window(menu_list)

    def add_menuitems (self, name, rpt):
        # create the data needed for Gtk.ActionGroup.add_actions
        title = N_("Report")+": "+N_(name)
        menuitm = GncMenuItem()
        ae = GncActionEntry()
        ae.name = rpt.report_guid
        if rpt.menu_name:
            ae.label = rpt.menu_name
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
        menuitm.type = Gtk.UIManagerItemType.MENUITEM
        return menuitm

    def reports_cb (self, actionobj, user_data=None):
        print("report_cb",actionobj,user_data, file=sys.stderr)
        print("report_cb",actionobj.get_name(), file=sys.stderr)
        #(lambda (window)
        #  (let ((report (gnc:make-report
        #        (gnc:report-template-report-guid template))))
        #    (gnc-main-window-open-report report window)))))
        print("report_cb",user_data, file=sys.stderr)
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
            print("call back done")
        except Exception as errexc:
            traceback.print_exc()
            print("error in reports_cb callback",str(errexc), file=sys.stderr)

    # unfortunately looks as though this wont work because of GIL issues
    # - in the python C plugin we lock the callback and plugin_finalize
    # this is crashing when we try a second call

    def plugin_finalize (self):
        print("python only plugin_finalize called", file=sys.stderr)

    def old_reports_cb (self, actionobj, user_data=None):
        print("reports_cb",actionobj,user_data, file=sys.stderr)
        #pdb.set_trace()
        window = user_data

        try:
            #gnc_plugin_page_python_report.GncPluginPagePythonReport.OpenReport(42,window)
            gnc_plugin_page_python_report.OpenReport(42,window)
            print("call back done")
        except Exception as errexc:
            traceback.print_exc()
            print("error in reports_cb callback",str(errexc), file=sys.stderr)

    def tools_cb (self,*args):
        print("tools_cb",args, file=sys.stderr)

# gdb call back for report
#0  0x0000000100040898 in gnc_html_report_stream_cb ()
#1  0x00000001001c853e in load_to_stream ()
#2  0x00000001001c8d97 in impl_webkit_show_url ()
#3  0x00000001001c5fb1 in gnc_html_show_url ()
#4  0x000000010003e8d6 in gnc_plugin_page_report_create_widget ()
#5  0x000000010021e981 in gnc_plugin_page_create_widget ()
#6  0x0000000100214220 in gnc_main_window_open_page ()

