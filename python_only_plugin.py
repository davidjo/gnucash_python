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

# can we access a function in a python module via ctypes?
# - no because it needs to be a dylib not an so

#libcallback = ctypes.CDLL("/Users/djosg/.gnucash/python/pythoncallback.so")


#libcallback.gnc_python_callback.argtypes = [ ctypes.c_void_p, ctypes.c_void_p ]
#libcallback.gnc_python_callback.restype = None

#python_callbacktype = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)



import gnc_main_window


import gnc_plugin_page_python_report

import gnc_menu_extension


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

        # create callback object
        self.save_callbacks = MyCallbacks()

        # now try and fix

        # I dont quite understand this - using the gtk calls leads to a crash on a second
        # click of the menu
        # pythoncallback wraps the callbacks in GIL protection and things seem to work
        # - but I thought GIL protection was being done for gobjects - and as far as I can
        # see the callbacks are done through pyg_closure_marshal which does pyglib_gil_state_ensure etc
        # however the problem only happens if the reports page is actually displayed
        #newcb = python_callbacktype(self.reports_cb)
        # well I give up have no real idea why pythoncallback method is needed but it seems to work
        #actiongroup.add_actions([ 
        pythoncallback.add_actions(self.save_callbacks, actiongroup, [ \
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

        print "merge_id",self.merge_id

        # load the report classes and create instances
        self.load_python_reports()

    def plugin_init (self):
        print >> sys.stderr, "python only plugin_init called"

    def load_python_reports (self):
        # ok im wrong - we can instantiate here as long as do
        # very little in the __init__ - in particular no GUI
        from hello_world import HelloWorld 
        self.python_reports = {}
        self.python_reports['HelloWorld'] = HelloWorld()

        menu_list = []
        for rpt in self.python_reports:
            menu_list.append(self.add_menuitems(self.python_reports[rpt]))

        # now need to update menu
        # we cannot use the gnc-menu-extensions and gnc-plugin-menu-additions
        # as they are tied to scheme - because gnc-plugin-menu-additions gets its
        # list from gnc-menu-extensions which is totally tied to scheme
        self.menu_extensions = gnc_menu_extension.MyMenuAdditions(self.main_window)
        self.menu_extensions.add_to_window(menu_list)

    def add_menuitems (self, rpt):
        # create the data needed for gtk.ActionGroup.add_actions
        menuitm = GncMenuItem()
        ae = GncActionEntry()
        ae.name = rpt.report_guid
        ae.label = rpt.menu_name
        ae.tooltip = rpt.menu_tip
        ae.stock_id = None
        ae.accelerator = None
        ae.callback = self.reports_cb
        menuitm.ae = ae
        menuitm.path = "ui/menubar/Reports/OtherReports/PythonReports/PythonReportsholder/"
        menuitm.name = ae.label
        menuitm.action = ae.name
        menuitm.type = gtk.UI_MANAGER_MENUITEM
        return menuitm

    # unfortunately looks as though this wont work because of GIL issues
    # - in the python C plugin we lock the callback and plugin_finalize
    # this is crashing when we try a second call

    def plugin_finalize (self):
        print >> sys.stderr, "python only plugin_finalize called"

    def reports_cb (self, actionobj, user_data=None):
        print >> sys.stderr, "reports_cb",actionobj,user_data
        #pdb.set_trace()
        window = user_data

        try:
            #gnc_plugin_page_python_report.GncPluginPagePythonReport.OpenReport(42,window)
            gnc_plugin_page_python_report.OpenReport(42,window)
            print "call back done"
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

