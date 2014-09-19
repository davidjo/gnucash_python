
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import dialog_options_gi
#    GncOptionDB = dialog_options_gi.GncOptionDB
#    DialogOption = dialog_options_gi.DialogOption
#except ImportError:
#    import gobject
#    import dialog_options_pregi
#    GncOptionDB = dialog_options_pregi.GncOptionDB
#    DialogOption = dialog_options_pregi.DialogOption

try:
    from gi.repository import GObject
    import dialog_options_gi
    GncOptionDB = dialog_options_gi.GncOptionDB
    DialogOption = dialog_options_gi.DialogOption
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

