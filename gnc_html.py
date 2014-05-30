
import sys

import gtk

import pdb

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
        # unless just access the underlying webkit bindings
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


