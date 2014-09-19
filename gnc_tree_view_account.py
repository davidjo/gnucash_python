
import sys

import traceback
import pdb

#try:
#    from gi.repository import GObject
#    import gnc_tree_view_account_gi
#    new = gnc_tree_view_account_gi.new
#    new_with_root = gnc_tree_view_account_gi.new_with_root
#    set_selected_accounts = gnc_tree_view_account_gi.set_selected_accounts
#    get_selected_accounts = gnc_tree_view_account_gi.get_selected_accounts
#except ImportError:
#    import gobject
#    import gnc_tree_view_account_pregi
#    new = gnc_tree_view_account_pregi.new
#    new_with_root = gnc_tree_view_account_pregi.new_with_root
#    set_selected_accounts = gnc_tree_view_account_pregi.set_selected_accounts
#    get_selected_accounts = gnc_tree_view_account_pregi.get_selected_accounts

try:
    from gi.repository import GObject
    import gnc_tree_view_account_gi
    new = gnc_tree_view_account_gi.new
    new_with_root = gnc_tree_view_account_gi.new_with_root
    set_selected_accounts = gnc_tree_view_account_gi.set_selected_accounts
    get_selected_accounts = gnc_tree_view_account_gi.get_selected_accounts
except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

