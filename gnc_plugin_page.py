
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import gnc_plugin_page_gi
#    from gnc_plugin_page_gi import GncPluginPagePython
#except ImportError:
#    import gobject
#    import gnc_plugin_page_pregi
#    from gnc_plugin_page_pregi import GncPluginPagePython

try:
    from gi.repository import GObject
    import gnc_plugin_page_gi
    from gnc_plugin_page_gi import BaseGncPluginPage,BaseGncPluginPageClass
    from gnc_plugin_page_gi import GncPluginPagePython
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()


