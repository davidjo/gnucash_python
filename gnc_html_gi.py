
# this uses some hackery to work with the C GncHtmlWebkit subclass
# - the advantage of this hackery is that all(?) the other url handling
# is still maintained so eg account names as hyperlinks still open
# the account register as in the C/scheme reports

import os
import sys

import ctypes

import gc

from gi.repository import GObject

from gi.repository import Gtk

from gi.repository import URLType


import pdb
import traceback


def N_(msg):
    return msg


# well great - gnc_build_url is not defined in the include file!!
# - it is in swig bindings though!! (but not python??)


# great - after all this importing webkit locks gnucash up
# and just importing WebView doesnt help either
#print >> sys.stderr, "Before webview import"
#import webkit
#from webkit import WebView
# OK have pinned this down to the gobject.threads_init()
# this is called in the __init__.py for webkit - and this locks up in Python callback from menu
# the following does not include __init__.py and does not lock up
# UPDATE - now calling gobject.threads_init again 
#sys.path.insert(0,"/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages/webkit")
#webkit = __import__("webkit")
#print >> sys.stderr, "After webview import"

# try accessing through gnucash type
# THIS WORKS AND IS THE PREFERRED METHOD FOR THE MOMENT
# - this allows some functionality to work automagically eg account hyper links
# opening up account register
# NOTE that in addition this needs the GncHtml GType defined


from gi.repository import GncHtmlWebkit

import glib_ctypes

#import pygignchelpers

import girepo
from girepo import GObjectField


# OK - I give up - we need to get access to the private instance data
#  - create duplicate ctype definitions here

# lets try re-creating the private data structure (DANGEROUS) and
# accessing the value via ctypes
# - not of real use until sort out field offset issue of gir

GtkWidgetOpaque = ctypes.c_void_p
gchar_p = ctypes.c_char_p
URLTypeOpaque = ctypes.c_char_p
GHashTableOpaque = ctypes.c_void_p
GncHTMLUrltypeCBOpaque = ctypes.c_void_p
GncHTMLLoadCBOpaque = ctypes.c_void_p
GncHTMLFlyoverCBOpaque = ctypes.c_void_p
GncHTMLButtonCBOpaque = ctypes.c_void_p
gpointer = ctypes.c_void_p
gnc_html_history_opaque = ctypes.c_void_p

class GncHtmlPrivate(ctypes.Structure):

    _fields_ = [ \
                ("parent", GtkWidgetOpaque),                      # /* window this html goes into */
                ("container", GtkWidgetOpaque),                   # /* parent of the webkit widget */
                ("current_link", gchar_p),                        # /* link under mouse pointer */

                ("base_type", URLTypeOpaque),                     # /* base of URL (path - filename) */
                ("base_location", gchar_p),

                ("request_info", GHashTableOpaque),           # /* hash uri to GList of GtkHTMLStream * */

                # /* callbacks */
                ("urltype_cb", GncHTMLUrltypeCBOpaque),       # /* is this type OK for this instance? */
                ("load_cb", GncHTMLLoadCBOpaque),
                ("flyover_cb", GncHTMLFlyoverCBOpaque),
                ("button_cb", GncHTMLButtonCBOpaque),

                ("flyover_cb_data", gpointer),
                ("load_cb_data", gpointer),
                ("button_cb_data", gpointer),

		("history", gnc_html_history_opaque),
               ]

WebKitWebViewOpaque = ctypes.c_void_p

class GncHtmlWebKitPrivate(ctypes.Structure):

    _fields_ = [ \
                ("base", GncHtmlPrivate),
                ("web_view", WebKitWebViewOpaque),
                ("html_string", gchar_p),
                #("html_string", ctypes.c_void_p),
               ]


ctypes.pythonapi.PyString_AsString.argtypes = (ctypes.c_void_p,)
ctypes.pythonapi.PyString_AsString.restype = ctypes.c_void_p

def fixup_html_string (privfld, docstr):

    #pdb.set_trace()

    # this does the impl_webkit_show_data storage of the html string in the
    # private data of GncHtmlWebkit

    priv_ptr = privfld.get_object_value()

    webkit_private = ctypes.cast( priv_ptr, ctypes.POINTER( GncHtmlWebKitPrivate ) ).contents

    print("python priv addr %x"%ctypes.addressof(webkit_private))

    web_view_ptr = webkit_private.web_view

    # we cannot take addresses of structure members
    #print("python priv webview addr %x"%ctypes.addressof(webkit_private.web_view))

    # given up - make this a c_void_p and cast for string - and just store pointer
    html_string = ""
    if webkit_private.html_string != None:
        html_string = ctypes.cast(webkit_private.html_string, gchar_p).value

    #
    # but we can get the offset
    print("python priv html_string offset %x"%GncHtmlWebKitPrivate.html_string.offset)

    # what to do about unicode??
    new_value_str_ptr = ctypes.pythonapi.PyString_AsString(id(docstr))

    print("python str address %x"%new_value_str_ptr)

    # here Im worried about freeing data - html_string is freed by gnc_html_webkit_dispose
    # and Im not sure if python will be able handle something freed under it
    # one solution is to do as impl_webkit_show_data and use g_strdup
    # via ctypes
    # does ctypes.c_char_p copy the string?
    copy_value_str_ptr = glib_ctypes.libglib.g_strdup(new_value_str_ptr)

    # lets assume for the moment we may have issues
    #webkit_private.html_string = ctypes.c_char_p(docstr)
    webkit_private.html_string = ctypes.cast(copy_value_str_ptr,ctypes.c_char_p)

    #webkit_private.html_string = ctypes.cast(ctypes.c_char_p(docstr), ctypes.c_void_p)

    # finally - this is how we do pointer assignment given plain addresses
    # we must cast to a pointer type - its confusing because the pointed to type is also a generic
    # pointer!!
    #value_ptr = priv_ptr + GncHtmlWebKitPrivate.html_string.offset
    #print("python html_string address %x"%value_ptr)
    #ctypes.cast(value_ptr, ctypes.POINTER(ctypes.c_void_p)).contents.value = new_value_str_ptr


# make a subclass to track the virtual calls

class PythonHtmlWebkit(GncHtmlWebkit.HtmlWebkit):

    def __init__ (self):
        super(PythonHtmlWebkit,self).__init__()

    # apparently for gobject introspection virtual methods (which GI recognises)
    # are overridden  by adding do_ to their name

    # we need to re-implement impl_webkit_show_data and impl_webkit_export_to_file
    # in order to deal with the usage of the C private data html_string
    # this is a pure re-implementation
    # the big issue is now need access to the webkit library for the
    # call to webkit_web_view_load_uri or webkit_web_view_load_html_string
    # in impl_webkit_show_data
    # well thats not going to work either because we need the private variable
    # web_view for the webkit function calls!!

    def do_show_data (self, data, datalen):
        print "do_show_data",data[0:20],str(datalen)
        pdb.set_trace()

        TEMPLATE_REPORT_FILE_NAME = "gnc-report-XXXXXX.html"

    def do_export_to_file (self, filename):
        print "do_export_to_file",filename
        pdb.set_trace()
        print "do_export_to_file",filename


# GncHtml has register handlers which allow a url type
# to be associated with function calls - a subclass definition
# (in this case the subclass is GncHtmlWebkit) of the show_url
# function may use these handlers
# it also has a table for stream handlers - these are used in the
# load to stream function
# this a ctypes implementation to load new python handlers into
# the C functions
# not sure this is going to work - the problem is we have no simple
# way to determine the existing handlers loaded - unless we directly
# access the GHashTables the handlers are stored in
# - and what we want to do is call the existing handler in most cases

def register_url_handler (url_type, handler):

    if url_type.lower() in url_handlers:
        unregister_url_handler(url_type)

    url_handlers[url_type.lower()] = handler

def unregister_url_handler (url_type):

    if url_type.lower() in url_handlers:
        del url_handlers[url_type.lower()]


# hmm - the actual graphics drawer is somehow in html
# - the Report class seems to be something else
# not sure whether should still do this
# for now using separate class to implement drawing

class HtmlView(object):

    def __init__ (self,use_pywebkit=False,use_gncwebkit=True):

        # story so far
        # the python webkit displays blank for the jqplot
        # - normal html is displayed, javascript text display works
        # but jqplot fails to display
        # using the gnucash webkit GObject everything works - jqplot is displayed!!
        # (the show data function writes the html to a temporary file before
        # displaying using webkit show_uri - is this the issue??)
        # cant see immediately what the difference - only difference I can see
        # so far is gnucash sets a default encoding and font  

        self.use_pywebkit = use_pywebkit
        self.use_gncwebkit = use_gncwebkit

        if self.use_pywebkit:
            # create raw widget here - no use of gnucash html stuff at all
            self.widget = Gtk.ScrolledWindow()
            self.widget.set_policy(Gtk.POLICY_AUTOMATIC,Gtk.POLICY_AUTOMATIC)

            # this is pywebkit access - fails - locks up the whole gnucash GUI
            # unless just access the underlying webkit bindings
            self.webview = webkit.WebView()
            self.widget.add(self.webview)

        if self.use_gncwebkit:
            # use gnucash access to webkit via gi wrapper
            self.html = GncHtmlWebkit.HtmlWebkit()
            print >> sys.stderr, GObject.signal_list_names(GncHtmlWebkit.HtmlWebkit)
            #pdb.set_trace()
            #self.html = PythonHtmlWebkit()
            # so this is annoying - the gir bindings are generating
            # the wrong offset for the priv field (but not for the parent field)
            # probably some inconsistency in the Gtk.Bin gir definition
            # (which GncHtml is a subclass of)
            # yes - Gtk.Bin is a subclass of Gtk.Container which has bit fields
            # at end of instance structure and apparently introspection cant handle
            # bit fields - so all offsets after Gtk.Container are wrong!!
            # added a hack to GObjectField to handle this if know offset
            #prnt = GObjectField.Setup(self.html,"parent_instance")
            self.privfld = GObjectField.Setup(self.html,"priv",offset_adjust_hack=-16,check_adjust_hack=144)
            # note this creates the base scrolled window widget internally
            # we get the widget (a scrolled window) via html.get_widget()
            self.widget = self.html.get_widget()
            print "webkit widget",type(self.widget)
            print "webkit widget",self.widget
            print "webkit widget",self.widget.get_child()


    # so the story so far is as follows
    # the problem with impl_webkit_show_url is where to inject the python report
    # - this function is driven by handlers
    # - the problem is if we replace handlers with python handlers ALL reports will
    # go through python - even though it may just fall through to the C function
    # note there is also the issue that elements of the report may need to call out
    # to the original report handlers - sort of ignoring this at the moment
    # for the moment we have re-implemented the show_url function (which we partially do below)
    # the original show_url eventually leads to a call to impl_webkit_show_data to
    # actually display the rendered html string - which we can use except that
    # it does a direct call to impl_webkit_export_to_file which relies on setting
    # the html string into the private C variable html_string
    # unfortunately re-implementing impl_webkit_show_data also needs access to the
    # the other C private variable web_view so Im stuck either way
    # pygignchelpers creates a special function in C to set the html_string variable
    # and then call impl_webkit_show_data and we see a report
    # we also now have an introspection/ctypes way to set this value ie without
    # compiling a module
    # (note we still have no way to fire up a python report via those url handlers
    #  or even detect if we have a python report)
    # one advantage of hi-jacking the C version is that call outs from the report seem
    # to be handled by the base impl_webkit_show_url functions 

    # so for the moment we have a minimal impl_webkit_show_url re-implementation
    # - this is only called from create_widget so we know we have a report url
    # (for a python report) and we dont bother trying to implement all the other
    # url handling - we just need to inject the eventual html string into the
    # impl_webkit_show_data C function 

    def show_url (self,url_type,url_location,url_label,report_cb=None):
        # try drawing something here
        #button = Gtk.Button(label="My Button")
        #self.widget.add(button)

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

        #pdb.set_trace()

        # in impl_webkit_show_url the load_cb is called AFTER loading the page
        # why did I put it before??
        # in scheme something to do with loading updated options and creating new version
        # of a report based on those updated options

        self.load_cb(url_type,url_location,url_label)

        # the C impl_webkit_show_url does a lot with urls - getting a specific
        # handler for different types of url and calling that to handle the url
        # it also does something about creating a history or urls accessed
        # (which Im not sure how is used at the moment)
        # looks like eventually load_to_stream is called to actually display
        # any generated data - if the url would generate display data

        # more closely following the C code
        self.load_to_stream(url_type,url_location,url_label,report_cb=report_cb)

        # why is this here??
        # the self.container.show_all() in create_widget should show this widget
        self.widget.show_all()

    def reload (self):
        pdb.set_trace()
        #gc.collect()
        # something with history
        # for the moment use the saved instance mapped to a function call via lambda
        # is this ever called??
        # no - the reload virtual function is set to impl_webkit_reload which will
        # get called - and as impl_webkit_reload is based on the gnc_history_html 
        # which if history exists (which we dont have for python reports)
        # impl_webkit_reload just re-calls gnc_html_show_url ie impl_webkit_show_url
        # which wont handle python reports
        self.show_url(None,None,None,report_cb=lambda : self.report_backup)


    def load_to_stream (self, url_type, url_location, url_label, report_cb=None):
        #pdb.set_trace()

        # here we pass in report_cb the function to generate the html display
        # data

        # we ignore all the stream handlers code in this routine
        # we assume this is only passed a url_type of report

        if report_cb:

            # this code is partially implementing the report stream handler
            # as defined in gnc_html_report_stream_cb in window-report.c
            # which seems to be the primary callout to scheme to run the report

            report = report_cb()
            # im going to stuff this in a variable for reload temporarily
            self.report_backup = report

            baddocstr = "<html><body><h3>%s</h3>\n            <p>%s</p></body></html>"%( \
                                 N_("Report error"),
                                 N_("An error occurred while running the report."))

            try:
                # try an implementation closer to the C/scheme
                docstr = report.run()
            except Exception, errexc:
                traceback.print_exc()
                docstr = baddocstr
            else:
                if docstr == None:
                    docstr = baddocstr 

            self.load_string(docstr)

        else:

            summary = "<html><body>The report is <b>not</b> defined in show_url.</body></html>";

            # in the C code the progress bar is reset here
            # this would be our equivalent
            #gnc_report_utilities.report_finished()

            self.load_string(summary)


    def load_string (self, docstr):
        #pdb.set_trace()
        # junky function to map the calls
        if self.use_pywebkit:
            self.webview.load_string(docstr,"text/html", "UTF-8", "gnucash:report")
        if self.use_gncwebkit:

            # major hack until sort out impl_webkit_show_url
            # this calls impl_webkit_show_data but prior to this storing docstr
            # in private gnc_html variable html_string - which is required
            # for the impl_webkit_export_to_file call in impl_webkit_show_data
            # for the moment use our tricky helper function to accomplish this
            #pdb.set_trace()
            print "hash self.html","%x"%hash(self.html)
            #pygignchelpers.show_data(self.html,docstr,len(docstr))

            # hacked up introspection/ctypes way to set html_string variable
            fixup_html_string(self.privfld,docstr)
            # this calls the impl_webkit_show_data GncHtmlWebkit function
            # NOTA BENE - impl_webkit_show_data seems to copy the generated report
            # string to a file via the impl_webkit_export_to_file call
            # AND THEN RESETS the uri to a file uri
            # the html string is displayed by a call to webkit_web_view_load_uri
            # which almost immediately does the webkit_navigation_requested_cb
            # callback which basically ignores file uris!!
            # note that its webkit_navigation_requested_cb which responds to links
            # etc in report pages
            self.html.show_data(docstr,len(docstr))

            # so looks as though what we need to do is re-implement impl_webkit_show_data
            # in python because it does a direct call to impl_webkit_export_to_file rather
            # than through the virtual function and then we re-implement impl_webkit_export_to_file
            # to use the python saved document string rather than inaccessible C private data
            # structure
            # not so fast - no point until we figure out the priv pointer offset issue
            # calling the show data function here does indeed end up calling the do_show_data function
            # of the PythonHtmlWebkit subclass
            #pdb.set_trace()
            #self.html.show_data(docstr,len(docstr))
            #print "junk"


    def set_load_cb (self, load_cb, load_cb_data=None):
        #pdb.set_trace()
        self.load_cb = load_cb
        self.load_cb_data = load_cb_data


type_2_proto = { \
                 URLType.TYPE_FILE : "file",
                 URLType.TYPE_JUMP : "",
                 URLType.TYPE_HTTP : "http",
                 URLType.TYPE_FTP : "ftp",
                 URLType.TYPE_SECURE : "https",
                 URLType.TYPE_REGISTER : "gnc-register",
                 URLType.TYPE_ACCTTREE : "gnc-acct-tree",
                 URLType.TYPE_REPORT : "gnc-report",
                 URLType.TYPE_OPTIONS : "gnc-options",
                 URLType.TYPE_SCHEME : "gnc-scm",
                 URLType.TYPE_HELP : "gnc-help",
                 URLType.TYPE_XMLDATA : "gnc-xml",
                 URLType.TYPE_PRICE : "gnc-price",
                 URLType.TYPE_BUDGET : "gnc-budget",
                 URLType.TYPE_OTHER : "",
                }

proto_2_type = {}


def build_url (type, location, label):

    #type_name = gnc_html_type_to_proto_hash(type)

    type_name = "file"

    if label:

        urlstr = "%s%s%s#%s"%(type_name,':' if type_name != "" else '', location if location != "" else "", label if label != "" else "")

    else:

        urlstr = "%s%s%s"%(type_name,':' if type_name != "" else '', location if location != "" else "")

    return urlstr

