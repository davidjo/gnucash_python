
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import gnc_currency_edit_gi
#    GncCurrencyEdit = gnc_currency_edit_gi.GncCurrencyEdit
#except ImportError:
#    import gobject
#    import gnc_currency_edit_pregi
#    GncCurrencyEdit = gnc_currency_edit_pregi.GncCurrencyEdit

try:
    from gi.repository import GObject
    import gnc_currency_edit_gi
    GncCurrencyEdit = gnc_currency_edit_gi.GncCurrencyEdit
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

