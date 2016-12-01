

import sys

from gi.repository import GObject

from gi.repository import Gtk

import re


import pdb

# how to do internationalization in python
#import gettext
#gettext.bindtextdomain('myapplication', '/path/to/my/language/directory')
#gettext.textdomain('myapplication')
#_ = gettext.gettext
# dummy function for internationalization
def N_(msg):
    return msg

import datetime


import gnucash

from gnucash import GncNumeric

from gnucash import GNC_HOW_RND_ROUND_HALF_UP


from sw_app_utils import GncPrintAmountInfo

from sw_app_utils import PrintAmount

from sw_app_utils import FiCalc


from tool_objects import ToolTemplate

from gnc_builder import GncBuilder

from gnc_amount_edit import GNCAmountEditPython


class GNCCommodityAmountEdit(GNCAmountEditPython):

    def __init__ (self, min_places=0, max_places=0, fraction=1):
        super(GNCCommodityAmountEdit,self).__init__(min_places,max_places,fraction)


class FinCalcDialog(object):

    class FinCalcValues(object):
        PAYMENT_PERIODS  = 0
        INTEREST_RATE    = 1
        PRESENT_VALUE    = 2
        PERIODIC_PAYMENT = 3
        FUTURE_VALUE     = 4

        NUM_FIN_CALC_VALUES = 5


    class FinancialInfo(object):

        def __init__ (self):
            frac_digits = 4
            self.fi_calc = FiCalc()
            self.fi_calc.fi_info.npp = 12
            self.fi_calc.fi_info.ir = 8.5
            self.fi_calc.fi_info.pv = 15000.0
            self.fi_calc.fi_info.pmt = -400.0
            self.fi_calc.fi_info.CF = 12
            self.fi_calc.fi_info.PF = 12
            self.fi_calc.fi_info.bep = False
            self.fi_calc.fi_info.disc = True
            self.fi_calc.fi_info.prec = frac_digits

    periods = [ \
               1, # /* annual */
               2, # /* semi-annual */
               3, # /* tri-annual */
               4, # /* quarterly */
               6, # /* bi-monthly */
               12, # /* monthly */
               24, # /* semi-monthly */
               26, # /* bi-weekly */
               52, # /* weekly */
               360, # /* daily (360) */
               365, # /* daily (365) */
              ]


    def __init__ (self):

        self.amounts = {}

        #self.window = Gtk.Window(Gtk.WINDOW_TOPLEVEL)
        #self.window.set_position(Gtk.WIN_POS_CENTER)
        #self.window.set_default_size(800,600)
        #self.window.set_border_width(0)

        #self.window.connect('destroy-event', self.destroy_cb)
        #self.window.connect('delete-event', self.delete_cb)

        #button = Gtk.Button(label="My Button")
        #self.window.add(button)
        #self.window.show_all()

        # I think all the following is done in the run function

        # this I think detects if the dialog is already open
        #if (gnc_forall_gui_components (DIALOG_FINCALC_CM_CLASS,
        #                               show_handler, NULL))
        #    return;

        builder = GncBuilder()
        builder.add_from_file("dialog-fincalc.glade", "liststore1")
        builder.add_from_file("dialog-fincalc.glade", "liststore2")
        builder.add_from_file("dialog-fincalc.glade", "Financial Calculator Dialog")

        # junkily we need to list all signals here
        # the gnucash code somehow figures all signals
        self.builder_handlers = { \
                                'fincalc_response_cb' : self.response_cb,
                                'fincalc_amount_clear_clicked_cb' : self.amount_clear_clicked_cb,
                                'fincalc_calc_clicked_cb' : self.calc_clicked_cb,
                                'fincalc_compounding_radio_toggled' : self.compounding_radio_toggled,
                                'fincalc_update_calc_button_cb' : self.update_calc_button_cb,
                                }

        #builder.connect_signals(self)
        builder.connect_signals(self.builder_handlers)

        self.dialog = builder.get_object("Financial Calculator Dialog")

        # this registers the dialog so the initial count check works
        #gnc_register_gui_component (DIALOG_FINCALC_CM_CLASS,
        #                            NULL, close_handler, fcd);

        self.dialog.connect('destroy', self.destroy_cb)


        hbox = builder.get_object("payment_periods_hbox")

        # this is a subclassed Gtk.Entry - just use pure Gtk.Entry for now
        # are we going to map the actual GncAmountEdit or just use a pure python
        # subclass??
        #edit = gnc_amount_edit_new()
        edit = GNCAmountEditPython(0,0,1)
        edit.show()

        self.amounts[FinCalcDialog.FinCalcValues.PAYMENT_PERIODS] = edit

        hbox.pack_end(edit,expand=False,fill=False,padding=0)

        edit.connect("changed", self.update_calc_button_cb)

        button = builder.get_object("payment_periods_clear_button")
        button.set_data("edit",edit)


        hbox = builder.get_object("interest_rate_hbox")

        edit = GNCAmountEditPython(2,5,100000)
        edit.show()

        self.amounts[FinCalcDialog.FinCalcValues.INTEREST_RATE] = edit

        hbox.pack_end(edit,expand=False,fill=False,padding=0)

        edit.connect("changed", self.update_calc_button_cb)

        button = builder.get_object("interest_rate_clear_button")
        button.set_data("edit",edit)


        hbox = builder.get_object("present_value_hbox")

        edit = GNCCommodityAmountEdit()
        edit.show()

        self.amounts[FinCalcDialog.FinCalcValues.PRESENT_VALUE] = edit

        hbox.pack_end(edit,expand=False,fill=False,padding=0)

        edit.connect("changed", self.update_calc_button_cb)

        button = builder.get_object("present_value_clear_button")
        button.set_data("edit",edit)


        hbox = builder.get_object("periodic_payment_hbox")

        edit = GNCAmountEditPython()
        edit.show()

        self.amounts[FinCalcDialog.FinCalcValues.PERIODIC_PAYMENT] = edit

        hbox.pack_end(edit,expand=False,fill=False,padding=0)

        edit.connect("changed", self.update_calc_button_cb)

        button = builder.get_object("periodic_payment_clear_button")
        button.set_data("edit",edit)


        hbox = builder.get_object("future_value_hbox")

        edit = GNCAmountEditPython()
        edit.show()

        self.amounts[FinCalcDialog.FinCalcValues.FUTURE_VALUE] = edit

        hbox.pack_end(edit,expand=False,fill=False,padding=0)

        edit.connect("changed", self.update_calc_button_cb)

        button = builder.get_object("future_value_clear_button")
        button.set_data("edit",edit)

        self.calc_button = builder.get_object("calc_button")


        combo = builder.get_object("compounding_combo")
        combo.show()

        self.compounding_combo = combo

        combo.connect("changed", self.update_calc_button_cb)


        combo = builder.get_object("payment_combo")
        combo.show()

        self.payment_combo = combo

        combo.connect("changed", self.update_calc_button_cb)


        button = builder.get_object("period_payment_radio")
        combo.show()

        self.end_of_period_radio = button


        button = builder.get_object("discrete_compounding_radio")
        combo.show()

        self.discrete_compounding_radio = button


        self.payment_total_label = builder.get_object("payment_total_label")


        button = builder.get_object("schedule_button")
        button.hide()


    def destroy_cb (self, actionobj, userdata=None):
        print >> sys.stderr, "destroy_cb",actionobj,userdata
        self.dialog.destroy()

    def delete_cb (self, actionobj, userdata=None):
        print >> sys.stderr, "delete_cb",actionobj,userdata
        self.dialog.destroy()

    def response_cb (self, actionobj, response=None):
        print >> sys.stderr, "response_cb",actionobj,response
        if response == Gtk.ResponseType.OK or \
           response == Gtk.ResponseType.CLOSE:
            #gnc_save_window_size(GNC_PREFS_GROUP, self.dialog)
            pass
        #gnc_close_gui_component_by_data (DIALOG_FINCALC_CM_CLASS, fcd)
        self.dialog.destroy()

    def amount_clear_clicked_cb (self, actionobj, userdata=None):
        print >> sys.stderr, "amount_clear_clicked_cb",actionobj,userdata
        edit = actionobj.get_data("edit")
        if edit != None:
            edit.set_text("")

    def calc_clicked_cb (self, actionobj, userdata=None):
        print >> sys.stderr, "calc_clicked_cb",actionobj,userdata

        for i in xrange(FinCalcDialog.FinCalcValues.NUM_FIN_CALC_VALUES):
            text = self.amounts[i].get_text()
            if text != None and text != "":
                continue
            print >> sys.stderr, "click check",i,text
            self.calc_value(i)


    def compounding_radio_toggled (self, actionobj, userdata=None):
        print >> sys.stderr, "compounding_radio_toggled",actionobj,userdata

    def update_calc_button_cb (self, actionobj, userdata=None):
        print >> sys.stderr, "update_calc_button_cb",actionobj,userdata

        for i in xrange(FinCalcDialog.FinCalcValues.NUM_FIN_CALC_VALUES):
            text = self.amounts[i].get_text()
            if text == None or text == "":
                self.calc_button.set_sensitive(True)
                return

        self.calc_button.set_sensitive(False)


    def can_calc_value (self, value):

        for i in xrange(FinCalcDialog.FinCalcValues.NUM_FIN_CALC_VALUES):
            if i != value:
                text = self.amounts[i].get_text()
                if text == None or text == "":
                    return (N_("This program can only calculate one value at a time. " + \
                               "You must enter values for all but one quantity."),
                            i)

                if not self.amounts[i].evaluate():
                    return (N_("GnuCash cannot determine the value in one of the fields. " + \
                               "You must enter a valid expression."),
                            i)

        if value == FinCalcDialog.FinCalcValues.PAYMENT_PERIODS or \
           value == FinCalcDialog.FinCalcValues.PRESENT_VALUE or \
           value == FinCalcDialog.FinCalcValues.PERIODIC_PAYMENT or \
           value == FinCalcDialog.FinCalcValues.FUTURE_VALUE:
            nvalue = self.amounts[FinCalcDialog.FinCalcValues.INTEREST_RATE].get_amount()
            if nvalue.zero_p():
                return (N_("The interest rate cannot be zero."), FinCalcDialog.FinCalcValues.INTEREST_RATE)

        if value == FinCalcDialog.FinCalcValues.INTEREST_RATE or \
           value == FinCalcDialog.FinCalcValues.PRESENT_VALUE or \
           value == FinCalcDialog.FinCalcValues.PERIODIC_PAYMENT or \
           value == FinCalcDialog.FinCalcValues.FUTURE_VALUE:
            nvalue = self.amounts[FinCalcDialog.FinCalcValues.PAYMENT_PERIODS].get_amount()
            if nvalue.zero_p():
                return (N_("The number of payments cannot be zero."), FinCalcDialog.FinCalcValues.PAYMENT_PERIODS)
            if nvalue.negative_p():
                return (N_("The number of payments cannot be negative."), FinCalcDialog.FinCalcValues.PAYMENT_PERIODS)

        return (None, -1)


    def calc_value (self, value):

        (string, error_item) = self.can_calc_value(value)

        if string != None:
            # should do gtk error dialog
            print >> sys.stderr, value, error_item, string
            if error_item == 0:
                entry = self.amounts[0]
            else:
                entry = self.amounts[error_item]
            entry.grab_focus()
            return

        self.financial_info.print_finfo()

        self.gui_to_fi()

        self.financial_info.print_finfo()

        if value == FinCalcDialog.FinCalcValues.PAYMENT_PERIODS:
            #self.financial_info.fi_info.npp = self.financial_info.num_payments()
            self.financial_info.num_payments()
            print "num_payments",self.financial_info.fi_info.npp
        elif value == FinCalcDialog.FinCalcValues.INTEREST_RATE:
            #self.financial_info.fi_info.ir = self.financial_info.interest()
            self.financial_info.interest()
            print "interest",self.financial_info.fi_info.ir
        elif value == FinCalcDialog.FinCalcValues.PRESENT_VALUE:
            #self.financial_info.fi_info.pv = self.financial_info.present_value()
            self.financial_info.present_value()
            print "present_value",self.financial_info.fi_info.pv
        elif value == FinCalcDialog.FinCalcValues.PERIODIC_PAYMENT:
            #self.financial_info.fi_info.pmt = self.financial_info.payment()
            self.financial_info.payment()
            print "payment",self.financial_info.fi_info.pmt
        elif value == FinCalcDialog.FinCalcValues.FUTURE_VALUE:
            #self.financial_info.fi_info.fv = self.financial_info.future_value()
            self.financial_info.future_value()
            print "future_value",self.financial_info.fi_info.fv
        else:
            #PERR("Unknown financial variable")
            pass
            return

        self.financial_info.print_finfo()

        self.fi_to_gui()

        self.calc_button.set_sensitive(False)


    def init_fi (self):

        frac_digits = 4
        self.financial_info = FiCalc()
        self.financial_info.fi_info.npp = 12
        self.financial_info.fi_info.ir = 8.5
        self.financial_info.fi_info.pv = 15000.0
        self.financial_info.fi_info.pmt = -400.0
        self.financial_info.fi_info.CF = 12
        self.financial_info.fi_info.PF = 12
        self.financial_info.fi_info.bep = False
        self.financial_info.fi_info.disc = True
        self.financial_info.fi_info.prec = frac_digits

        self.financial_info.print_finfo()

        self.financial_info.future_value()

        self.financial_info.print_finfo()


    def normalize_period (self, period):

        for i in xrange(len(self.periods)-1,0,-1):
            if period >= self.periods[i]:
                return (i,self.periods[i])

        return (0,self.periods[0])

    def fi_to_gui (self):

        npp = GncNumeric(self.financial_info.fi_info.npp, 1)

        self.amounts[FinCalcDialog.FinCalcValues.PAYMENT_PERIODS].set_amount(npp)

        self.amounts[FinCalcDialog.FinCalcValues.INTEREST_RATE].set_damount(self.financial_info.fi_info.ir)
        self.amounts[FinCalcDialog.FinCalcValues.PRESENT_VALUE].set_damount(self.financial_info.fi_info.pv)
        self.amounts[FinCalcDialog.FinCalcValues.PERIODIC_PAYMENT].set_damount(self.financial_info.fi_info.pmt)
        self.amounts[FinCalcDialog.FinCalcValues.FUTURE_VALUE].set_damount(self.financial_info.fi_info.fv)

        pmt = gnucash.gnucash_core_c.double_to_gnc_numeric(self.financial_info.fi_info.pmt, 100000, GNC_HOW_RND_ROUND_HALF_UP)
        pmt = GncNumeric(instance=pmt)

        #commodity = gnc_default_currency()

        #total = npp.mul(pmt, commodity.get_fraction(), GNC_HOW_RND_ROUND_HALF_UP)
        total = npp.mul(pmt, 1000, GNC_HOW_RND_ROUND_HALF_UP)

        #total_string = str(total)
        #total_string = PrintAmount(total, gnc_default_print_info(False))
        total_string = PrintAmount(total)

        self.payment_total_label.set_text(total_string)

        (i, self.financial_info.fi_info.CF) = self.normalize_period(self.financial_info.fi_info.CF)
        self.compounding_combo.set_active(i)

        (i, self.financial_info.fi_info.PF) = self.normalize_period(self.financial_info.fi_info.PF)
        self.payment_combo.set_active(i)

        self.end_of_period_radio.set_active(not self.financial_info.fi_info.bep)

        self.discrete_compounding_radio.set_active(self.financial_info.fi_info.disc)

    def gui_to_fi (self):

        #pdb.set_trace()

        npp = self.amounts[FinCalcDialog.FinCalcValues.PAYMENT_PERIODS].get_amount()
        self.financial_info.fi_info.npp = npp.num()

        self.financial_info.fi_info.ir = self.amounts[FinCalcDialog.FinCalcValues.INTEREST_RATE].get_damount()
        self.financial_info.fi_info.pv = self.amounts[FinCalcDialog.FinCalcValues.PRESENT_VALUE].get_damount()
        self.financial_info.fi_info.pmt = self.amounts[FinCalcDialog.FinCalcValues.PERIODIC_PAYMENT].get_damount()
        self.financial_info.fi_info.fv = self.amounts[FinCalcDialog.FinCalcValues.FUTURE_VALUE].get_damount()
        self.financial_info.fi_info.fv = -self.financial_info.fi_info.fv

        i = self.compounding_combo.get_active()
        self.financial_info.fi_info.CF = self.periods[i]

        i = self.payment_combo.get_active()
        self.financial_info.fi_info.PF = self.periods[i]

        toggle = self.end_of_period_radio
        self.financial_info.fi_info.bep = not toggle.get_active()

        toggle = self.discrete_compounding_radio
        self.financial_info.fi_info.disc = toggle.get_active()

        #self.financial_info.fi_info.prec = gnc_locale_decimal_places()
        self.financial_info.fi_info.prec = 4



class DialogFinCalcTool(ToolTemplate):

    def __init__ (self):

        super(DialogFinCalcTool,self).__init__()

        # need to set the  base variables
        self.version = 1
        self.name = N_("Loan Repayment Calculator")
        self.tool_guid = "d0ce1382f0eb429399ef11695fbaf786"
        self.menu_name = N_("Loan Repayment Calculator")
        self.menu_tip = N_("A Loan Repayment Calculator")
        #self.menu_path = N_("Tool Path")
        #self.stock_id = None

        self.amounts = {}

    def run (self):

        fcd = FinCalcDialog()

        fcd.init_fi()

        fcd.fi_to_gui()

        fcd.dialog.show()
