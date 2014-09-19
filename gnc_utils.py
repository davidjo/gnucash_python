
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import gnc_utils_gi
#    GncCBWEMixin = gnc_utils_gi.GncCBWEMixin
#except ImportError:
#    import gobject
#    import gnc_utils_pregi
#    GncCBWEMixin = gnc_utils_pregi.GncCBWEMixin

try:
    from gi.repository import GObject
    import gnc_utils_gi
    GncCBWEMixin = gnc_utils_gi.GncCBWEMixin
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

