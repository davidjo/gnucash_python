
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import gnc_menu_extension_gi
#    MyMenuAdditions = gnc_menu_extension_gi.MyMenuAdditions
#except ImportError:
#    import gobject
#    import gnc_menu_extension_pregi
#    MyMenuAdditions = gnc_menu_extension_pregi.MyMenuAdditions

try:
    from gi.repository import GObject
    import gnc_menu_extension_gi
    MyMenuAdditions = gnc_menu_extension_gi.MyMenuAdditions
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

