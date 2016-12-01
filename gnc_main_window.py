
import sys

import traceback
import pdb

#try:
#    import gi
#    from gi.repository import GObject
#    import gnc_main_window_gi
#except ImportError:
#    import gobject
#    import gnc_main_window_gi

#pdb.set_trace()

try:
    import gi
    from gi.repository import GObject
    import gnc_main_window_gi
    from gnc_main_window_gi import main_window_wrap
    libgnc_gnomeutils = gnc_main_window_gi.libgnc_gnomeutils
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()


