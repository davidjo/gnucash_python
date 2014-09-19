
import sys

import gc

import gtk

import pdb
import traceback


def N_(msg):
    return msg


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
# NOTE that this needs the gnchtml module in additions to define the GncHtml GType
import gnchtmlwebkit


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
            self.widget = gtk.ScrolledWindow()
            self.widget.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)

            # this is pywebkit access - fails - locks up the whole gnucash GUI
            # unless just access the underlying webkit bindings
            self.webview = webkit.WebView()
            self.widget.add(self.webview)

        if self.use_gncwebkit:
            # use gnucash access to webkit via codegen wrapper
            self.html = gnchtmlwebkit.HtmlWebkit()
            # note this creates the base scrolled window widget internally
            # we get the widget (a scrolled window) via html.get_widget()
            self.widget = self.html.get_widget()
            #print "webkit widget",type(self.widget)
            #print "webkit widget",self.widget


    def show_url (self,url_type,url_location,url_label,report_cb=None):
        # try drawing something here
        #button = gtk.Button(label="My Button")
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

        self.load_cb(url_type,url_location,url_label)

        if report_cb:

            report = report_cb()
            # im going to stuff this in a variable for reload temporarily
            self.report_backup = report

            baddocstr = "<html><body><h3>%s</h3>\n            <p>%s</p></body></html>"%( \
                                 N_("Report error"),
                                 N_("An error occurred while running the report."))

            try:
                # try an implementation closer to the C/schem
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

            self.load_string(summary)


        self.widget.show_all()

    def load_string (self, docstr):
        # junky function to map the calls
        if self.use_pywebkit:
            self.webview.load_string(docstr,"text/html", "UTF-8", "gnucash:report")
        if self.use_gncwebkit:
            self.html.show_data(docstr,len(docstr))

    def set_load_cb (self, load_cb, load_cb_data=None):
        self.load_cb = load_cb
        self.load_cb_data = load_cb_data

    def reload (self):
        #pdb.set_trace()
        #gc.collect()
        # something with history
        # for the moment use the saved instance mapped to a function call via lambda
        self.show_url(None,None,None,report_cb=lambda : self.report_backup)


def build_url (type, location, label):

    #type_name = gnc_html_type_to_proto_hash(type)

    type_name = "file"

    if label:

        urlstr = "%s%s%s#%s"%(type_name,':' if type_name != "" else '', location if location != "" else "", label if label != "" else "")

    else:

        urlstr = "%s%s%s"%(type_name,':' if type_name != "" else '', location if location != "" else "")

    return urlstr
