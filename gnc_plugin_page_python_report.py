
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import gnc_plugin_page_python_report_gi
#    OpenReport = gnc_plugin_page_python_report_gi.OpenReport
#except ImportError:
#    import gobject
#    import gnc_plugin_page_python_report_pregi
#    OpenReport = gnc_plugin_page_python_report_pregi.OpenReport

try:
    from gi.repository import GObject
    import gnc_plugin_page_python_report_gi
    OpenReport = gnc_plugin_page_python_report_gi.OpenReport
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

