
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import python_only_plugin_gi
#    MyPlugin = python_only_plugin_gi.MyPlugin
#except ImportError:
#    import gobject
#    import python_only_plugin_pregi
#    MyPlugin = python_only_plugin_pregi.MyPlugin

try:
    from gi.repository import GObject
    import python_only_plugin_gi
    MyPlugin = python_only_plugin_gi.MyPlugin
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

