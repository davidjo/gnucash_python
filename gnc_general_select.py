
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import  gnc_general_select_gi
#    GncGeneralSelect = gnc_general_select_gi.GncGeneralSelect
#except ImportError:
#    import gobject
#    import gnc_general_select_pregi
#    GncGeneralSelect = gnc_general_select_pregi.GncGeneralSelect

try:
    from gi.repository import GObject
    import  gnc_general_select_gi
    GncGeneralSelect = gnc_general_select_gi.GncGeneralSelect
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

