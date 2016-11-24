
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import gnc_plugin_python_reports_gi
#    from gnc_plugin_python_reports_gi import GncPluginPythonReports
#except ImportError:
#    import gobject
#    import gnc_plugin_python_reports_pregi
#    from gnc_plugin_python_reports_pregi import GncPluginPythonReports

try:
    from gi.repository import GObject
    import gnc_plugin_python_reports_gi
    from gnc_plugin_python_reports_gi import GncPluginPythonReports
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

