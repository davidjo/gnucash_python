

import sys

import pdb


# trivial switcher module


# the issue is that the ctypes version works beautifully
# and the introspection version reliably crashes
# my current guess is that the py-gobject wrapping of the
# swig account objects is releasing the underlying account gobject
# when the py-gobject wrapper is freed
# introspection issue resolved as difference between transfer full
# and transfer none - the account objects are stored in the tree view
# and should not be transfer full when returned as selections but
# transfer none - its the tree view thats holding the account objects
# - then using introspection works

if False:

    import gnc_tree_view_account_ctypes

    from gnc_tree_view_account_ctypes import *

    # keep current code as is in dialog_options

    def do_get_selected_accounts (widget):

        return widget.do_get_selected_accounts()

    def do_set_selected_accounts (widget, account_list, show_last):

        widget.do_set_selected_accounts(account_list, show_last)


elif True:

    import gnc_tree_view_account_gi

    from gnc_tree_view_account_gi import new_with_root

    from gnc_tree_view_account_gi import new

    from gnc_tree_view_account_gi import GncTreeViewAccountPython

    # keep current code as is in dialog_options

    def do_get_selected_accounts (widget):

        return widget.do_get_selected_accounts()

    def do_set_selected_accounts (widget, account_list, show_last):

        widget.do_set_selected_accounts(account_list, show_last)
