
# special currency widget

import gobject

import gtk

from datetime import datetime

import pdb


import sw_app_utils

import gnucash


import qof_ctypes

import gnc_utils


def N_(msg):
    return msg


class GncCurrencyEdit(gtk.ComboBoxEntry):

    # ah - this is something I think Ive missed - we can name the GType here
    __gtype_name__ = 'GncCurrencyEdit'

    # OK Im now thinking gobject warning messages were happening previously but just did not get the message

    # so why does the gnc_currency_edit_new say mnemonic is the only property
    # but we have model and has-entry on the g_object_new which are also properties??

    __gproperties__ = {
                       'mnemonic' : (gobject.TYPE_STRING,                     # type
                                      N_("Active currency's mnemonic"),       # nick name
                                      N_("Active currency's mnemonic"),       # description
                                      "USD",                                  # default value
                                      gobject.PARAM_READWRITE),               # flags
                      }

    cmtstr = """
    __gsignal__ = {
                   'format_changed' : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (int,))
                  }
    """


    def __init__ (self):

        store = gtk.ListStore(gobject.TYPE_STRING)

        super(GncCurrencyEdit,self).__init__(model=store)

        # why are these in the C init and the above in the C new??
        # as they are in the C init they will be done at the g_object_new call
        # which is equivalently here in python
        self.connect("notify::mnemonic",self.mnemonic_changed)

        self.connect("changed",self.active_changed)


        self.set_entry_text_column(0)

        # this is where it is in 
        gnc_utils.gnc_cbwe_require_list_item(self)

        self.fill_currencies()

        store.set_sort_column_id(0,gtk.SORT_ASCENDING)


    def add_item (self, commodity):
        model = self.get_model()
        prtstr = commodity.get_printname()
        model.append((prtstr,))

    def fill_currencies (self):
        commod_tbl = sw_app_utils.get_current_commodities()
        currencies = commod_tbl.get_commodities('CURRENCY')
        for curr in currencies:
            self.add_item(curr)

    def do_get_property (self, property):
        if property.name == 'mnemonic':
            return self.mnemonic
        else:
            raise AttributeError, 'unknown property %s' % property.name
    def do_set_property (self, property, value):
        if property.name == 'mnemonic':
            self.mnemonic = value
        else:
            raise AttributeError, 'unknown property %s' % property.name

    def get_currency (self):

        iter = self.get_active_iter()
        if iter != None:
            model = self.get_model()
            value = model.get_value(iter,0)
            #fullname = value.get_string()
            fullname = value
            mnemonic = fullname
            indx = mnemonic.find(' ')
            if indx >= 0:
                mnemonic = mnemonic[0:indx]
            commodity = sw_app_utils.get_current_commodities().lookup('CURRENCY', mnemonic)
        else:
            #g_warning("Combo box returned 'inactive'. Using locale default currency.")
            commodity = sw_app_utils.locale_default_currency()
        return commodity

    def set_currency (self, currency):

        printname = currency.get_printname()
        gnc_utils.gnc_cbwe_set_by_string(self,printname)

    def active_changed (self, *args):
        print "active_changed currency",args
        widget = args[0]
        pdb.set_trace()

        currency = self.get_currency()
        mnemonic = currency.get_mnemonic()

        self.handler_block_by_func(self.active_changed)
        self.set_property("mnemonic",mnemonic)
        self.handler_unblock_by_func(self.active_changed)


    def mnemonic_changed (self, *args):
        print "mnemonic_changed",args
        widget = args[0]

        currency = sw_app_utils.get_current_commodities().lookup('CURRENCY', self.get_property('mnemonic'))

        if currency == None:
            #DEBUG("gce %p, default currency mnemonic %s",
            #      self, gnc_commodity_get_mnemonic(currency));
            currency = sw_app_utils.locale_default_currency()

        self.handler_block_by_func(self.mnemonic_changed)
        self.set_currency(currency)
        self.handler_unblock_by_func(self.mnemonic_changed)


