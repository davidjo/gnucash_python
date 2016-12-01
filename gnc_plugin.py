
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import gnc_plugin_gi
#    from gnc_plugin_gi import GncPluginPython
#except ImportError:
#    import gobject
#    import gnc_plugin_pregi
#    from gnc_plugin_pregi import GncPluginPython

try:
    from gi.repository import GObject
    import gnc_plugin_gi
    from gnc_plugin_gi import BaseGncPlugin,BaseGncPluginClass
    from gnc_plugin_gi import GncPluginPython
    from gnc_plugin_gi import init_short_names
    from gnc_plugin_gi import set_important_actions
    from gnc_plugin_gi import update_actions
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

from gnc_plugin_gi import GncPluginPythonTest

