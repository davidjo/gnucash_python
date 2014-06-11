
# what the hell is going on here
# this is creating a new general select dialog
# but the dialog is defined in dialog-commodity.c

import gobject

from gnc_general_select import GncGeneralSelect

import dialog_commodity
from dialog_commodity import DialogCommodity


# not clear what to do here
# is GncCommodityEdit a subclass of GncGeneralSelect
# no - we need to be a subclass of GncGeneralSelect

class GncCommodityEdit(GncGeneralSelect):

    def __init__ (self):
        super(GncCommodityEdit,self).__init__(GncGeneralSelect.GNC_GENERAL_SELECT_TYPE_SELECT,
                                                 self.get_string, self.new_select, None)

    def get_string (self, ptr):
        # in C this involves a type conversion
        return ptr.get_printname()

    def new_select (self, mode_ptr, comm, toplevel):
        # lots of type conversions
        mode = mode_ptr if mode_ptr != None else DialogCommodity.DIAG_COMM_ALL
        newobj = dialog_commodity.gnc_ui_select_commodity_modal(comm, toplevel, mode)
        return newobj

