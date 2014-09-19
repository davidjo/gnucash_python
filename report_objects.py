
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import report_objects_gi
#except ImportError:
#    import gobject
#    import report_objects_pregi

try:
    from gi.repository import GObject
    import report_objects_gi
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

