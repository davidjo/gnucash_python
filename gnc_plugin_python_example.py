
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import gnc_plugin_python_example_gi
#    from gnc_plugin_python_example_gi import GncPluginPythonExample
#except ImportError:
#    import gobject
#    import gnc_plugin_python_example_pregi
#    from gnc_plugin_python_example_pregi import GncPluginPythonExample

try:
    from gi.repository import GObject
    import gnc_plugin_python_example_gi
    from gnc_plugin_python_example_gi import GncPluginPythonExample
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

