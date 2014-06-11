

def N_(msg):
    return msg


import gnc_utils


class DialogCommodity(object):

    DIAG_COMM_CURRENCY     = 0   # /**< Dialog box should only allow selection
                                 #  of a currency. */
    DIAG_COMM_NON_CURRENCY = 1   # /**< Dialog box should allow selection of
                                 #  anything but a currency. */
    DIAG_COMM_ALL          = 2   # /**< Dialog box should allow selection of
                                 #  anything. */

    def __init__ (self):
        pass


class SelectCommodityWindow(object):
    pass

if True:

    def gnc_ui_select_commodity_modal_full (orig_sel, parent, mode, user_message=None, cusip=None, fullname=None, mnemonic=None):

        retval = None

        win = self.gnc_ui_select_commodity_create(orig_sel, mode)
        win.default_cusip = cusip
        win.default_fullname = fullname
        win.default_mnemonic = mnemonic
        win.default_user_symbol = ""

        if parent:
            win.dialog.set_transient_for(parent)

        if user_message:
           initial = user_message
        elif cusip or fullname or mnemonic:
           initial = N_("\nPlease select a commodity to match:")
        else:
           initial = ""

        user_prompt_text = "%s%s%s%s%s%s%s"%( \
                                initial,
                                N_("\nCommodity: ") if fullname else "", 
                                fullname if fullname else "",
                                N_("\nExchange code (ISIN, CUSIP or similar): ") if cusip else "",
                                cusip if cusip else "",
                                N_("\nMnemonic (Ticker symbol or similar): ") if mnemonic else "",
                                mnemonic if mnemonic else "")

        win.select_user_prompt.set_text(user_prompt_text)

        done = False

        while not done:

            value = win.dialog.run()

            if value == gtk.RESPONSE_OK:
                retval = win.selection
                done = True
            elif value == gtk.RESPONSE_NEW:
                win.commodity_new_cb()
            else:
                retval = None
                done = True

        win.dialog.destroy()

        return retval

    def gnc_ui_select_commodity_modal (orig_sel, parent, mode):
        return gnc_ui_select_commodity_modal_full(orig_sel, parent, mode)

    def gnc_ui_select_commodity_create (orig_sel, mode):

        retval = SelectCommodityWindow()

        builder = gtk.Builder()
        builder.add_from_file("dialog-commodity.glade", "liststore1")
        builder.add_from_file("dialog-commodity.glade", "liststore2")
        builder.add_from_file("dialog-commodity.glade", "Security Selector Dialog")

        builder.connect_signals({})

        retval.dialog = builder.get_object("Security Selector Dialog")
        retval.namespace_combo = builder.get_object("ss_namespace_cbwe")
        retval.commodity_combo = builder.get_object("ss_commodity_cbwe")
        retval.select_user_prompt = builder.get_object("select_user_prompt")
        retval.ok_button = builder.get_object("ss_ok_button")

        label = builder.get_object("item_label")

        gnc_utils.gnc_cbwe_require_list_item(retval.namespace_combo)
        gnc_utils.gnc_cbwe_require_list_item(retval.commodity_combo)

        retval.select_user_prompt.set_text("")

        if mode == DialogCommodity.DIAG_COMM_ALL:
            title = N_("Select security/currency")
            text = N_("_Security/currency:")
        elif mode == DialogCommodity.DIAG_COMM_NON_CURRENCY:
            title = N_("Select security")
            text = N_("_Security:")
        #elif mode == DialogCommodity.DIAG_COMM_CURRENCY:
        else:
            title = N_("Select currency")
            text = N_("Cu_rrency:")
            button = builder.get_object("ss_new_button")
            button.destroy()

        retval.dialog.set_title(title)
        retval.dialog.set_text(text)

        gnc_ui_update_namespace_picker(retval.namespace_combo,gnc_commodity_get_namespace(orig_sel),mode)
        namespace = gnc_ui_namespace_picker_ns(retval.namespace_combo)
        gnc_ui_update_commodity_picker(retval.commodity_combo,gnc_commodity_get_printname(orig_sel),mode)

        return retval

    def gnc_ui_select_commodity_new_cb (self, *args):
        print "gnc_ui_select_commodity_new_cb",args

        w = args[1]

        namespace = gnc_ui_namespace_picker_ns(w.namespace_combo)

        new_commodity = gnc_ui_new_commodity_modal_full(namespace,
                                                        w.dialog,
                                                        w.default_cusip,
                                                        w.default_fullname,
                                                        w.default_mnemonic,
                                                        w.default_user_symbol,
                                                        w.default_fraction)

        if new_commodity:

            gnc_ui_update_namespace_picker(w.namespace_combo,gnc_commodity_get_namespace(new_commodity),DialogCommodity.DIAG_COMM_ALL)

            gnc_ui_update_commodity_picker(w.commodity_combo,gnc_commodity_get_namespace(new_commodity),gnc_commodity_get_printname(new_commodity))

