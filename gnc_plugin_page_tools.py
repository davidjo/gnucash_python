
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import gnc_plugin_python_tools_gi
#    GncPluginPythonTools = gnc_plugin_python_tools_gi.GncPluginPythonTools
#except ImportError:
#    import gobject
#    import gnc_plugin_python_tools_pregi
#    GncPluginPythonTools = gnc_plugin_python_tools_pregi.GncPluginPythonTools

try:
    from gi.repository import GObject
    import gnc_plugin_python_tools_gi
    GncPluginPythonTools = gnc_plugin_python_tools_gi.GncPluginPythonTools
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

