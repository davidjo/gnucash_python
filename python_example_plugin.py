import sys
import os
import pdb


import ctypes

#pdb.set_trace()

import gnc_main_window

import gnc_plugin_page_report

import gnc_plugin_page_python_report


try:
    #import _sw_app_utils
    #from gnucash import *
    #from _sw_core_utils import gnc_prefs_is_extra_enabled
    #from gi.repository import Gtk
    pass
except Exception, errexc:
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

print >> sys.stderr, "before pythonplugin"

import pythonplugin

print >> sys.stderr, "after pythonplugin"


import gnc_plugin_page_report



class MyPlugin(object):

    def __init__(self):
        pass

    def plugin_class_init (self):
        print >> sys.stderr, "plugin_class_init called"
        # try creating the ui xml file here
        ui_xml = \
"""
<ui>
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
    <menu name="Tools" action="ToolsAction">
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
        fdes = open("/Users/djosg/.gnucash/ui/python-example-plugin.xml",'w')
        fdes.write(ui_xml)
        fdes.close()
        # not sure about life time if make it local
        # making it a self attribute means stays around as long as instance does
        # - we really need it to stay around as long as module is loaded
        # be careful - passing None here means must check for Py_None in the extension!!
        mylist = [ \
            ("PythonReportsAction", None, "Python Reports...", None, "python reports tooltip", None),
            ("PythonToolsAction", None, "Python Tools...", None, "python tools tooltip", None),
            ("pythonreportsAction", None, "Python reports description...", None, "python reports tooltip", None),
            ("pythongenericAction", None, "Python tools description...", None, "python tools tooltip", None),
                 ]
        self.myactions = { \
                         'actions_name' : "gnc-plugin-python-generic-actions",
                         'actions' : mylist,
                         'ui_filename' : "/Users/djosg/.gnucash/ui/gnc-plugin-python-generic-ui-tmp.xml",
                         }
        return self.myactions

    def plugin_init (self):
        print >> sys.stderr, "plugin_init called"

    def plugin_finalize (self):
        print >> sys.stderr, "plugin_finalize called"

    def plugin_action_callback (self,actionobj,dataobj):
        print >> sys.stderr, "plugin_action_callback called",actionobj
        print >> sys.stderr, "plugin_action_callback called",actionobj.get_name()
        # this gets access to the underlying C pointer
        #ctypes.pythonapi.PyCObject_AsVoidPtr.restype = ctypes.c_long
        #ctypes.pythonapi.PyCObject_AsVoidPtr.argtypes = [ctypes.py_object]
        #dataadr = ctypes.pythonapi.PyCObject_AsVoidPtr(dataobj)
        # this does what is needed - except this calls the guile report system
        # so creates a failed report page
        #windowdata_ptr = ctypes.cast(dataobj, ctypes.POINTER(gnc_main_window.GncMainWindowActionData))
        #window = ctypes.addressof(windowdata_ptr.contents.window.contents)
        #gnc_plugin_page_report.GncPluginPageReport.OpenReport(42,window)
        #pdb.set_trace()
        window = dataobj['window']
        if actionobj.get_name() == 'pythonreportsAction':
            try:
                #gnc_plugin_page_python_report.GncPluginPagePythonReport.OpenReport(42,window)
                gnc_plugin_page_python_report.OpenReport(42,window)
            except Exception, errexc:
                print >> sys.stderr, "error in plugin_action callback",str(errexc)
            print  "junke"

# gdb call back for report
#0  0x0000000100040898 in gnc_html_report_stream_cb ()
#1  0x00000001001c853e in load_to_stream ()
#2  0x00000001001c8d97 in impl_webkit_show_url ()
#3  0x00000001001c5fb1 in gnc_html_show_url ()
#4  0x000000010003e8d6 in gnc_plugin_page_report_create_widget ()
#5  0x000000010021e981 in gnc_plugin_page_create_widget ()
#6  0x0000000100214220 in gnc_main_window_open_page ()

