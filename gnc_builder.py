
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import gnc_builder_gi
#    GncBuilder = gnc_builder_gi.GncBuilder
#except ImportError:
#    import gobject
#    import gnc_builder_pregi
#    GncBuilder = gnc_builder_pregi.GncBuilder

try:
    from gi.repository import GObject
    import gnc_builder_gi
    GncBuilder = gnc_builder_gi.GncBuilder
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

