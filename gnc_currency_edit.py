
# special currency widget

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import GObject

from gi.repository import Gtk

from datetime import datetime

import pdb


import sw_app_utils

import gnucash


#import gnc_utils
from gnc_utils import GncCBWEMixin


def N_(msg):
    return msg

# so this looks like needs some fixing
# is seems to be using the ComboBox directly in gtk 3
# no - it appears it always used ComboBox
# so I must have changed it - because it was simpler I think
# anyway in gtk 3 it appears Gtk.ComboBoxEntry has gone
# yes its confirmed Gtk.ComboBoxEntry is gone in Gtk 3
# - but looking at GtkComboBox dont see difference in python
# implementation - we still have the model object

# why did I do this?
# it appears because I decided to implement everything in dialog_options
# in python or maybe it didnt work????

#class GncCurrencyEdit(Gtk.ComboBox):
class GncCurrencyEdit(GncCBWEMixin,Gtk.ComboBox):

    # ah - this is something I think Ive missed - we can name the GType here
    __gtype_name__ = 'GncCurrencyEdit'

    mnemonic = GObject.Property(type=str,                                                  # type
                                default="USD",                                             # default value
                                nick=N_("Active currency's mnemonic"),                     # nick
                                blurb=N_("Active currency's mnemonic"),                    # description
                                flags=GObject.ParamFlags.READWRITE)                        # flags
                                #minimum=-1,                                                # min value
                                #maximum=GLib.MAXINT32)                                     # max value


    cmtstr = """
    __gsignals__ = {
                   'format_changed' : (GObject.SignalFlags.RUN_FIRST, None, (int,))
                   }
    """


    def __init__ (self):

        store = Gtk.ListStore(GObject.TYPE_STRING)

        super(GncCurrencyEdit,self).__init__(model=store,has_entry=True)

        # need to implement this!!
        # Set the style context for this widget so it can be easily manipulated with css
        # this method appears to be outdated - the path method seems to be new version
        #self.set_style_context("GncCurrencyEdit")
        self.get_path().iter_set_object_name(0,"GncCurrencyEdit")

        # why are these in the C init and the above in the C new??
        # as they are in the C init they will be done at the g_object_new call
        # which is equivalently here in python
        self.connect("notify::mnemonic",self.mnemonic_changed)

        self.connect("changed",self.active_changed)


        # weird - I appear to need BOTH of these
        # without set_entry_text_column get a crash
        # without set_text_column no display of column!!
        # set_text_column does not exist in Gtk 3
        self.set_entry_text_column(0)
        #self.set_text_column(0)

        # this is where it is in 
        self.require_list_item()

        self.fill_currencies()

        store.set_sort_column_id(0,Gtk.SortType.ASCENDING)


    def add_item (self, commodity):
        model = self.get_model()
        prtstr = commodity.get_printname()
        #print("currency added",prtstr)
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
            raise AttributeError('unknown property %s' % property.name)
    def do_set_property (self, property, value):
        if property.name == 'mnemonic':
            self.mnemonic = value
        else:
            raise AttributeError('unknown property %s' % property.name)

    def get_currency (self):

        #pdb.set_trace()

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
        self.set_by_string(printname)


    def clear_display (self):

        # is this ever used??
        # - seems to have a bug

        model = self.get_model()

        entry = self.get_child()

        self.handler_block_by_func(self.active_changed)

        self.set_model(None)
        self.set_text("")
        self.set_active(-1)
        self.set_model(model)

        # this doesnt look right - surely should be unblock
        self.handler_block_by_func(self.active_changed)


    def active_changed (self, *args):
        print("active_changed currency",args)
        widget = args[0]

        currency = self.get_currency()
        mnemonic = currency.get_mnemonic()

        self.handler_block_by_func(self.active_changed)
        self.set_property("mnemonic",mnemonic)
        self.handler_unblock_by_func(self.active_changed)


    def mnemonic_changed (self, *args):
        print("mnemonic_changed",args)
        widget = args[0]

        currency = sw_app_utils.get_current_commodities().lookup('CURRENCY', self.get_property('mnemonic'))

        if currency == None:
            #DEBUG("gce %p, default currency mnemonic %s",
            #      self, gnc_commodity_get_mnemonic(currency));
            currency = sw_app_utils.locale_default_currency()

        self.handler_block_by_func(self.mnemonic_changed)
        self.set_currency(currency)
        self.handler_unblock_by_func(self.mnemonic_changed)


#GncCurrencyEdit.set_by_string = gnc_utils.set_by_string
#GncCurrencyEdit.add_completion = gnc_utils.add_completion
#GncCurrencyEdit.require_list_item = gnc_utils.require_list_item
#GncCurrencyEdit.focus_out_cb = gnc_utils.focus_out_cb
#GncCurrencyEdit.changed_cb = gnc_utils.changed_cb
#GncCurrencyEdit.match_selected_cb = gnc_utils.match_selected_cb

