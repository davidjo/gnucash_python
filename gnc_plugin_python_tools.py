
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import gnc_plugin_python_tools_gi
#    from gnc_plugin_python_tools_gi import GncPluginPythonTools
#except ImportError:
#    import gobject
#    import gnc_plugin_python_tools_pregi
#    from gnc_plugin_python_tools_pregi import GncPluginPythonTools

try:
    from gi.repository import GObject
    import gnc_plugin_python_tools_gi
    from gnc_plugin_python_tools_gi import GncPluginPythonTools
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

