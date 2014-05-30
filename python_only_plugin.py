import sys
import os
import pdb


import gobject


import ctypes

#pdb.set_trace()

try:
    #import _sw_app_utils
    #from gnucash import *
    #from _sw_core_utils import gnc_prefs_is_extra_enabled
    import gtk
    pass
except Exception, errexc:
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

gncmainwindowtype = gobject.type_from_name('GncMainWindow')

# this lists the properties
print >> sys.stderr, gobject.list_properties(gncmainwindowtype)

# this lists the signal names
print >> sys.stderr, gobject.signal_list_names(gncmainwindowtype)

print >> sys.stderr, dir(gncmainwindowtype)


import gnc_main_window


import gnc_plugin_page_python_report


import pythoncallback

# this works with the pythoncallback module
# pass a callback saver object for the moment
class MyCallbacks(object):

    def __init__ (self):
        self.user_data = None
        self.callbacks = {}


class MyPlugin(gobject.GObject):

    def __init__(self):
        self.plugin_class_init()
        self.plugin_init()

    def plugin_class_init (self):
        print >> sys.stderr, "plugin_class_init called"
        # try creating the ui xml file here
        ui_xml = """<ui>
  <menubar>
    <menu name="Reports" action="ReportsAction">
      <placeholder name="OtherReports">
        <menu name="PythonReports" action="PythonReportsAction">
          <placeholder name="PythonReportsholder">
            <menuitem name="Python Reports" action="pythonreportsAction"/>
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

        # yes - we now can add menu items in python only with some help
        # from a gncmainwindow module wrapping GncMainWindow
        # (could not get this to work with ctypes - conversion of the return
        # pointer from gnc_gui_init to a proper pygobject failed)
        # we apparently have to use the main window ui_merge object

        self.main_window = gnc_main_window.gnc_gui_init()
        self.main_ui_merge = self.main_window.get_uimanager()

        self.merge_id = 0

        #accelgroup = self.main_ui_merge.get_accel_group()
        #self.main_window.add_accel_group(accelgroup)


        # Create an ActionGroup
        actiongroup = gtk.ActionGroup('GncPythonMyPluginActions')
        self.actiongroup = actiongroup

        # create callback objects
        #self.reports_cb_obj = MyCallback(self.report_cb)
        #self.reports_cb_obj.callback

        self.save_callbacks = MyCallbacks()

        #actiongroup.add_actions([ 
        pythoncallback.add_actions(self.save_callbacks, actiongroup, [ \
            ("PythonReportsAction", None, "Python Reports...", None, "python reports tooltip", None),
            ("PythonToolsAction", None, "Python Tools...", None, "python tools tooltip", None),
            ("pythonreportsAction", None, "Python reports description...", None, "python reports tooltip", self.reports_cb),
            ("pythongenericAction", None, "Python tools description...", None, "python tools tooltip", self.tools_cb),
                 ], user_data=self.main_window)

        self.main_ui_merge.insert_action_group(actiongroup,0)

        self.merge_id = self.main_ui_merge.add_ui_from_string(ui_xml)

        #self.main_window.manual_merge_actions("myplugin",actiongroup,self.merge_id)

        self.main_ui_merge.ensure_update()

        print "merge_id",self.merge_id

    def plugin_init (self):
        print >> sys.stderr, "plugin_init called"

    # unfortunately looks as though this wont work because of GIL issues
    # - in the python C plugin we lock the callback and plugin_finalize
    # this is crashing when we try a second call

    def plugin_finalize (self):
        print >> sys.stderr, "plugin_finalize called"

    def reports_cb (self, actionobj, user_data=None):
        print >> sys.stderr, "reports_cb",actionobj,user_data

        try:
            #gnc_plugin_page_python_report.GncPluginPagePythonReport.OpenReport(42,window)
            gnc_plugin_page_python_report.OpenReport(42,user_data)
        except Exception, errexc:
            print >> sys.stderr, "error in reports_cb callback",str(errexc)
        print  "junke"

    def tools_cb (self,*args):
        print >> sys.stderr, "tools_cb",args

# gdb call back for report
#0  0x0000000100040898 in gnc_html_report_stream_cb ()
#1  0x00000001001c853e in load_to_stream ()
#2  0x00000001001c8d97 in impl_webkit_show_url ()
#3  0x00000001001c5fb1 in gnc_html_show_url ()
#4  0x000000010003e8d6 in gnc_plugin_page_report_create_widget ()
#5  0x000000010021e981 in gnc_plugin_page_create_widget ()
#6  0x0000000100214220 in gnc_main_window_open_page ()

