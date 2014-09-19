
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import gnc_date_edit_python_gi
#    GncDateEdit = gnc_date_edit_python_gi.GncDateEdit
#except ImportError:
#    import gobject
#    import gnc_date_edit_python_pregi
#    GncDateEdit = gnc_date_edit_python_pregi.GncDateEdit

try:
    from gi.repository import GObject
    import gnc_date_edit_python_gi
    GncDateEdit = gnc_date_edit_python_gi.GncDateEdit
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

