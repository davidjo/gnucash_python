
# sorting by locale
import locale

locale.setlocale(locale.LC_ALL, "")
#junk.sort(cmp=locale.strcoll)


import gtk


import pdb

import traceback


import gnucash


def N_(msg):
    return msg


from gnc_builder import GncBuilder

import gnc_utils

import sw_app_utils


# hmm - question is which is the primary object to choose as the
# defining class - DialogCommodity or SelectCommodityWindow
# also are the objects or GObjects??


class DialogCommodity(object):

    DIAG_COMM_CURRENCY     = 0   # /**< Dialog box should only allow selection
                                 #  of a currency. */
    DIAG_COMM_NON_CURRENCY = 1   # /**< Dialog box should allow selection of
                                 #  anything but a currency. */
    DIAG_COMM_ALL          = 2   # /**< Dialog box should allow selection of
                                 #  anything. */

    def __init__ (self, orig_sel, parent, mode, user_message=None, cusip=None, fullname=None, mnemonic=None):

        # this function split out into this init function and a run function
        # as per gtk.Dialog - in C this function sets up the dialog and runs it,
        # returning the selected item - python cant return from __init__

        retval = None

        self.win = SelectCommodityWindow.gnc_ui_select_commodity_create(orig_sel, mode)
        self.win.default_cusip = cusip
        self.win.default_fullname = fullname
        self.win.default_mnemonic = mnemonic
        self.win.default_user_symbol = ""

        if parent:
            self.win.dialog.set_transient_for(parent)

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

        self.win.select_user_prompt.set_text(user_prompt_text)


    def run (self):

        done = False

        while not done:

            value = self.win.dialog.run()

            if value == gtk.RESPONSE_OK:
                # protect against missing builder handler setup
                try:
                    retval = self.win.selection
                except Exception, errexc:
                    traceback.print_exc()
                    retval = None
                done = True
            elif value == gnc_utils.RESPONSE_NEW:
                self.win.gnc_ui_select_commodity_new_cb()
            else:
                retval = None
                done = True

        self.win.dialog.destroy()

        return retval

    @classmethod
    def gnc_ui_select_commodity_modal_full (cls, orig_sel, parent, mode, user_message=None, cusip=None, fullname=None, mnemonic=None):
        newobj = cls(orig_sel, parent, mode, user_message=user_message, cusip=cusip, fullname=fullname, mnemonic=mnemonic)
        return newobj

    @classmethod
    def gnc_ui_select_commodity_modal (cls, orig_sel, parent, mode):
        return cls.gnc_ui_select_commodity_modal_full(orig_sel, parent, mode)


class SelectCommodityWindow(object):

    def __init__ (self, orig_sel, mode):

        #retval = SelectCommodityWindow()

        builder = GncBuilder()
        builder.add_from_file("dialog-commodity.glade", "liststore1")
        builder.add_from_file("dialog-commodity.glade", "liststore2")
        builder.add_from_file("dialog-commodity.glade", "Security Selector Dialog")

        self.builder_handlers = { \
                                # 'onDeleteWindow' : gtk.main_guit,
                                'gnc_ui_select_commodity_changed_cb' : self.gnc_ui_select_commodity_changed_cb,
                                'gnc_ui_select_commodity_namespace_changed_cb' : self.gnc_ui_select_commodity_namespace_changed_cb,
                                }

        builder.connect_signals(self.builder_handlers)


        builder.connect_signals({})

        self.dialog = builder.get_object("Security Selector Dialog")
        namespace_combo = builder.get_object("ss_namespace_cbwe")
        self.namespace_combo = NamespacePicker(namespace_combo)
        commodity_combo = builder.get_object("ss_commodity_cbwe")
        self.commodity_combo = CommodityPicker(commodity_combo)
        self.select_user_prompt = builder.get_object("select_user_prompt")
        self.ok_button = builder.get_object("ss_ok_button")

        label = builder.get_object("item_label")

        self.namespace_combo.require_list_item()
        self.commodity_combo.require_list_item()

        self.select_user_prompt.set_text("")

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

        #pdb.set_trace()
        self.dialog.set_title(title)
        label.set_text_with_mnemonic(text)

        #gnc_ui_update_namespace_picker(self.namespace_combo,orig_sel.get_namespace(),mode)
        #namespace = gnc_ui_namespace_picker_ns(self.namespace_combo)
        #gnc_ui_update_commodity_picker(self.commodity_combo,namespace,orig_sel.get_printname())
        self.namespace_combo.gnc_ui_update_namespace_picker(orig_sel.get_namespace(),mode)
        namespace = self.namespace_combo.gnc_ui_namespace_picker_ns()
        self.commodity_combo.gnc_ui_update_commodity_picker(namespace,orig_sel.get_printname())

    @classmethod
    def gnc_ui_select_commodity_create (cls, orig_sel, mode):
        return cls(orig_sel, mode)


    def gnc_ui_select_commodity_new_cb (self, *args):
        print "gnc_ui_select_commodity_new_cb",args

        #w = args[1]

        namespace = self.namespace_combo.gnc_ui_namespace_picker_ns()

        new_commodity = gnc_ui_new_commodity_modal_full(namespace,
                                                        self.dialog,
                                                        self.default_cusip,
                                                        self.default_fullname,
                                                        self.default_mnemonic,
                                                        self.default_user_symbol,
                                                        self.default_fraction)

        if new_commodity:

            self.namespace_combo.gnc_ui_update_namespace_picker(new_commodity.get_namespace(),DialogCommodity.DIAG_COMM_ALL)

            self.commodity_combo.gnc_ui_update_commodity_picker(new_commodity.get_namespace(),new_commodity.get_printname())


    def gnc_ui_select_commodity_namespace_changed_cb (self, *args):
        print "gnc_ui_select_commodity_namespace_changed_cb",args

        #ENTER("cbwe=%p, user_data=%p", cbwe, user_data)

        # this is actual gtk combobox object
        combobox = args[0]

        #DEBUG("namespace=%s", namespace)

        namespace = self.namespace_combo.gnc_ui_namespace_picker_ns()

        self.commodity_combo.gnc_ui_update_commodity_picker(namespace,None)

    def gnc_ui_select_commodity_changed_cb (self, *args):
        print ".gnc_ui_select_commodity_changed_cb",args
        #pdb.set_trace()

        #ENTER("cbwe=%p, user_data=%p", cbwe, user_data)

        # this is actual gtk combobox object
        combobox = args[0]

        #DEBUG("namespace=%s", namespace)

        namespace = self.namespace_combo.gnc_ui_namespace_picker_ns()
        fullname = self.commodity_combo.commodity_combo.get_child().get_text()

        table = sw_app_utils.get_current_book().get_table()

        try:
            #self.selection = table.lookup(namespace,fullname)
            self.selection = table.find_full(namespace,fullname)
        except RuntimeError, errexc:
            # fail to find it
            self.selection = None

        #pdb.set_trace()

        ok = self.selection != None

        self.dialog.set_default_response(0 if ok else 2)

        #LEAVE("sensitive=%d, default = %d", ok, ok ? 0 : 2)


class NamespacePicker(object):

    def __init__ (self, namespace_combo):
        # nice idea but wont work here - namespace_combo not defined using class
        #newsubcls = type("ComboBoxWithUtils",(namespace_combo.__class__,gnc_utils.GncCBWEMixin),{})
        #namespace_combo.__class__ = newsubcls
        self.namespace_combo = namespace_combo
        gnc_utils.add_utils(self.namespace_combo)

    def require_list_item(self):
        self.namespace_combo.require_list_item()

    def gnc_ui_update_namespace_picker (self, init_string, mode):

        model = self.namespace_combo.get_model()
        model.clear()
        self.namespace_combo.set_active(-1)

        if mode == DialogCommodity.DIAG_COMM_ALL:
            # get_namespaces crashes
            # not clear what the difference is
            #namespaces = sw_app_utils.get_current_commodities().get_namespaces()
            namelst = sw_app_utils.get_current_commodities().get_namespaces_list()
            namespaces = [ (x.get_name(),x) for x in namelst ]
        elif mode == DialogCommodity.DIAG_COMM_NON_CURRENCY:
            #namespaces = sw_app_utils.get_current_commodities().get_namespaces()
            namelst = sw_app_utils.get_current_commodities().get_namespaces_list()
            #namespaces = [ (x.get_name(),x) for x in namelst ]
            namespaces = []
            #node = g_list_find_custom(namespaces, 'CURRENCY', collate)
            #if node:
            #    namespaces = g_list_remove_link(namespaces, node)
            for x in namelst:
                if x.get_name() == 'CURRENCY':
                    continue
                namespaces.append((x.get_name(),x))
            if gnc_commodity_namespace_is_iso(init_string):
                init_string = None
        #elif mode == DialogCommodity.DIAG_COMM_CURRENCY:
        else:
            #namespaces = g_list_prepend(None, 'CURRENCY')
            namespacecur = sw_app_utils.get_current_commodities().find_namespace('CURRENCY')
            namespaces = [ ('CURRENCY',namespacecur) ]

        #namespaces = g_list_sort(namespaces, collate)
        namespaces.sort(cmp=lambda x,y: locale.strcoll(x[0],y[0]))
        current = 0
        match = 0
        #for node in namespaces:
        #    if g_utf8_collate(node.data, "GNC_LEGACY_CURRENCIES") == 0:
        #        continue
        #    if g_utf8_collate(node.data, "template") != 0:
        #        model.append((node.data,))
        #    if g_utf8_collate(node.data, init_string) == 0:
        #        match = current
        #    current += 1
        for current,node in enumerate(namespaces):
            if node[0] == "GNC_LEGACY_CURRENCIES":
                continue
            if node[0] != "template":
                model.append((node[0],))
            if node[0] == init_string:
                match = current
        #    current += 1

        self.namespace_combo.set_active(match)

    def gnc_ui_namespace_picker_ns (self):

        namespace = self.namespace_combo.get_child().get_text()

        if namespace == 'ISO4217':
            return 'CURRENCY'

        return namespace

class CommodityPicker(object):

    def __init__ (self, commodity_combo):
        self.commodity_combo = commodity_combo
        gnc_utils.add_utils(self.commodity_combo)

    def require_list_item(self):
        self.commodity_combo.require_list_item()

    def gnc_ui_update_commodity_picker (self, namespace, init_string):

        #pdb.set_trace()

        model = self.commodity_combo.get_model()
        model.clear()
        entry = self.commodity_combo.get_child()
        entry.delete_text(0,-1)

        self.commodity_combo.set_active(-1)

        table = sw_app_utils.get_current_book().get_table()
        commodities = table.get_commodities(namespace)
        commodity_items = []
        for commod in commodities:
            commodity_items.append(commod.get_printname())
        #commodity_items.sort(cmp=lambda x,y: locale.strcoll(x[0],y[0]))
        commodity_items.sort(cmp=locale.strcoll)
        match = 0
        for current,commod in enumerate(commodity_items):
            model.append((commod,))
            if commod == init_string:
                match = current

        self.commodity_combo.set_active(match)



class CommonCommodityModal(object):

    def __init__ (self,commodity,parent,namespace,cusip,fullname,mnemonic,user_symbol,fraction):

        # as before splitting the C code into this init and a run function

        # this is equivalent of gnc_ui_common_commodity_modal
        #ENTER(" ")
        retval = None

        if commodity:
            namespace = commodity.get_namespace()
            fullname = commodity.get_fullname()
            mnemonic = commodity.get_mnemonic()
            user_symbol = commodity.get_user_symbol()
            cusip = commodity.get_cusip()
            fraction = commodity.get_fraction()
        else:
            if sw_app_utils.gnc_commodity_namespace_is_iso(namespace):
                namespace = None

        self.win = gnc_ui_build_commodity_dialog(namespace, parent, fullname,
                                        mnemonic, user_symbol, cusip,
                                        fraction, commodity != None)

        self.win.update_quote_info(commodity)
        self.win.edit_commodity = commodity

        #self.win.gnc_ui_commodity_quote_info_cb(self.win.get_quote_check)

        #LEAVE(" ")


    def run (self):

        done = False

        while not done:

            value = self.win.dialog.run()

            if value == gtk.RESPONSE_OK:
                #DEBUG("case OK")
                done = self.win.gnc_ui_commodity_dialog_to_object()
                retval = self.win.edit_commodity
            elif value == gtk.RESPONSE_HELP:
                #DEBUG("case HELP")
                if help_callback:
                    help_callback()
            else:
                #DEBUG("default: %d", value)
                retval = None
                done = True

        self.win.dialog.destroy()

        return retval


    @classmethod
    def gnc_ui_new_commodity_modal_full (cls,namespace,parent,cusip,fullname,mnemonic,user_symbol,fraction):
        #return gnc_ui_new_commodity_modal_full(None,parent,namespace,cusip,fullname,mnemonic,user_symbol,fraction)
        return CommonCommodityModal(None,parent,namespace,cusip,fullname,mnemonic,user_symbol,10000)

class QuoteSourceType(object):
    SOURCE_SINGLE = 0   # /**< This quote source pulls from a single
                        #  *   specific web site.  For example, the
                        #  *   yahoo_australia source only pulls from
                        #  *   the yahoo web site. */
    SOURCE_MULTI = 1    #         /**< This quote source may pull from multiple
                        #  *   web sites.  For example, the australia
                        #  *   source may pull from ASX, yahoo, etc. */
    SOURCE_UNKNOWN = 2  # /**< This is a locally installed quote source
                        #  *   that gnucash knows nothing about. May
                        #  *   pull from single or multiple
                        #  *   locations. */
    SOURCE_MAX = 3
    SOURCE_CURRENCY = SOURCE_MAX  #/**< The special currency quote source. */


class CommodityWindow(object):

    def __init__ (self, namespace, parent, fullname,mnemonic, user_symbol, cusip, fraction, edit):

        #ENTER("widget=%p, selected namespace=%s, fullname=%s, mnemonic=%s",
        #      parent, selected_namespace, fullname, mnemonic);

        builder = GncBuilder()
        builder.add_from_file ("dialog-commodity.glade", "liststore2")
        builder.add_from_file ("dialog-commodity.glade", "adjustment1")
        builder.add_from_file ("dialog-commodity.glade", "Security Dialog")

        self.connect_signals({})

        self.dialog = builder.get_object("Security Dialog")
        if parent != None:
            self.dialog.set_transient_for(parent)
        self.edit_commodity = None

        self.help_button = builder.get_object("help_button")
        if not help_callback:
            help_button.hide()

        self.source_button = [None,None,None]

        self.fullname_entry = builder.get_object("fullname_entry")
        self.mnemonic_entry = builder.get_object("mnemonic_entry")
        self.user_symbol_entry = builder.get_object("user_symbol_entry")
        self.namespace_combo = builder.get_object("namespace_cbwe")
        self.code_entry = builder.get_object("code_entry")
        self.fraction_spinbutton = builder.get_object("fraction_spinbutton")
        self.ok_button = builder.get_object("ok_button")
        self.get_quote_check = builder.get_object("get_quote_check")
        self.source_label = get_object("source_label")
        self.source_button[QuoteSourceType.SOURCE_SINGLE] = builder.get_object("single_source_button")
        self.source_button[QuoteSourceType.SOURCE_MULTI] = builder.get_object("multi_source_button")
        self.quote_tz_label = builder.get_object("quote_tz_label")

        self.table = builder.get_object("edit_table")
        sec_label = builder.get_object("security_label")
        self.comm_section_top = self.table.child_get(sec_label, "bottom-attach")
        widget = builder.get_object("quote_label")
        self.comm_section_bottom = self.table.child_get(widget, "top-attach")
        self.comm_symbol_line = self.table.child_get(self.user_symbol_entry, "top-attach")

        # theres more!!


    @classmethod
    def gnc_ui_build_commodity_dialog(cls,namespace, parent, fullname,
                                        mnemonic, user_symbol, cusip,
                                        fraction, edit):
        return cls(namespace, parent, fullname,mnemonic, user_symbol, cusip, fraction, edit)

