
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import gnc_html_gi
#    HtmlView = gnc_html_gi.HtmlView
#except ImportError:
#    import gobject
#    import gnc_html_pregi
#    HtmlView = gnc_html_pregi.HtmlView

try:
    from gi.repository import GObject
    import gnc_html_gi
    HtmlView = gnc_html_gi.HtmlView
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

