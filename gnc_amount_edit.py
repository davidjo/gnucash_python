

import sys

#import gobject

from gi.repository import GObject

#import gtk

from gi.repository import Gtk
from gi.repository import Gdk



import re


import pdb


from sw_app_utils import GncPrintAmountInfo

from gnucash import GncNumeric


# how to do internationalization in python
#import gettext
#gettext.bindtextdomain('myapplication', '/path/to/my/language/directory')
#gettext.textdomain('myapplication')
#_ = gettext.gettext
# dummy function for internationalization
def N_(msg):
    return msg


class GNCAmountEditPython(Gtk.Entry):

    # we must make this a new GObject type to allow for original gnucash definition

    __gtype_name__ = 'GNCAmountEditPython'

    __gsignals__ = {
                   'amount_changed' : (GObject.SignalFlags.RUN_FIRST, None, (int,))
                   }


    def __init__ (self, min_places=0, max_places=0, fraction=1):
        super(GNCAmountEditPython,self).__init__()

        self.need_to_parse = False

        self.print_info = GncPrintAmountInfo()
        self.print_info.min_decimal_places = min_places
        self.print_info.max_decimal_places = max_places

        self.fraction = fraction

        self.evaluate_on_enter = True

        # gnc_amount_edit_set_print_info (edit, print_info);
        # gnc_amount_edit_set_fraction (edit, fraction);
        # gnc_amount_edit_set_evaluate_on_enter (edit, TRUE);

        # gtk_entry_set_alignment (GTK_ENTRY(edit), 1.0);
        self.set_alignment(1.0)

        self.amount = GncNumeric(0,1)

        self.connect("changed", self.changed_cb)

        self.connect("key-press-event", self.key_press_event)

        self.connect("activate", self.activate)

    def changed_cb (self, actionobj, userdata=None):
        print >> sys.stderr, "edit changed_cb",actionobj,userdata
        self.need_to_parse = True

    def key_press_event (self, widget, event):
        print "key_press_event", widget, event
        # this code changes keypad decimal key for currencies
        if event.keyval == Gdk.KEY_KP_Decimal:
            #if self.print_info.monetary:
            #    event.keyval = gnc_localeconv.mon_deciman_point[0]
            #    event.string[0] = gnc_localeconv.mon_deciman_point[0]
            pass

        # this calls parent function??
        # DONT DO THIS!! (it doesnt exist in any case)
        #result = super(GNCAmountEditPython,self).key_press_event(widget,event)
        # just ensure return False to perform more key event processing
        # returning True from this function means stop processing key event now
        result = False

        if event.keyval == Gdk.KEY_Return:
            if not self.evaluate_on_enter:
                if not (event.state & (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD1_MASK | Gdk.ModifierType.SHIFT_MASK)):
                    return result
        elif event.keyval == Gdk.KEY_KP_Enter:
            pass
        else:
            return result

        self.evaluate()

        return True

    def activate (self, widget, event=None):
        # this function is called on Return/Enter
        print "activate", widget, event


    def set_amount (self, amount):
        amount_string = PrintAmount(amount,self.print_info)
        #amount_string = str(amount)
        self.set_text(amount_string)
        self.amount = amount
        self.need_to_parse = False

    def get_amount (self):
        self.evaluate()
        return self.amount

    def set_damount (self, damount):
        #amount_string = PrintAmount(amount,self.print_info)
        #amount_string = str(amount)

        if self.fraction > 0:
            fraction = self.fraction
        else:
            fraction = 100000

        amount = gnucash.gnucash_core_c.double_to_gnc_numeric(damount, fraction, GNC_HOW_RND_ROUND_HALF_UP)
        amount = GncNumeric(instance=amount)

        self.set_amount(amount)

    def get_damount (self):
        self.evaluate()
        return self.amount.to_double()

    def expr_is_valid (self, empty_ok):

        txt_string = self.get_text()

        if txt_string == None or txt_string == "":

            amount = GncNumeric(0,1)

            if empty_ok:
                return (-1, amount)
            else:
                return (0, amount)

        error_loc = None

        # where to get this function??
        #ok = GncExpParserParse(txt_string, amount, error_loc)

        # junkily check for the moment
        #pdb.set_trace()
        mtch = re.search(r'^[0-9.,]+$',txt_string)
        if mtch == None:
            error_loc = len(txt_string)
            ok = False
        else:
            ok = True
            if txt_string.find(',') >= 0:
                txt_string = txt_string.replace(',','')
            if txt_string.find('.') >= 0:
                tmpval = float(txt_string)*self.fraction
                amount = GncNumeric(int(tmpval),self.fraction)
            else:
                tmpval = int(txt_string)*self.fraction
                amount = GncNumeric(tmpval,self.fraction)

        if ok:
            return (0, amount)

        if error_loc != None:
            return (error_loc, None)

        return (1, None)


    def set_evaluate_on_enter (self, evaluate_on_enter):

        self.evaluate_on_enter = evaluate_on_enter


    def evaluate (self):

        if not self.need_to_parse:
            return True

        (result, amount) = self.expr_is_valid(False)

        if result == -1:
            return True

        if result == 0:

            old_amount = self.amount

            if self.fraction > 0:
                amount = amount.convert(self.fraction,GNC_HOW_RND_ROUND_HALF_UP)

            self.set_amount(amount)

            if not amount == old_amount:
                self.emit("amount_changed",0)

            return True

        self.set_position(result)

        return False

    def set_print_info (self, print_info):

        self.print_info = self.print_info

        self.print_info.use_symbol = 0

    def set_fraction (self, fraction):

        # ensure positive
        fraction = max(0,fraction)

        self.fraction = fraction

