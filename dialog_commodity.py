
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import dialog_commodity_gi
#    DialogCommodity = dialog_commodity_gi.DialogCommodity
#except ImportError:
#    import gobject
#    import dialog_commodity_pregi
#    DialogCommodity = dialog_commodity_pregi.DialogCommodity

try:
    from gi.repository import GObject
    import dialog_commodity_gi
    DialogCommodity = dialog_commodity_gi.DialogCommodity
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

