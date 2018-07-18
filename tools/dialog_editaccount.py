

import sys

import os

import gi

gi.require_version('Gtk', '3.0')

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

import gnucash_ext

#import sw_engine
import engine_ctypes

from gnucash import GncNumeric

from gnucash import GNC_HOW_RND_ROUND_HALF_UP


from sw_app_utils import GncPrintAmountInfo
from sw_app_utils import get_current_book
from sw_app_utils import CommodityPrintInfo

import gnc_tree_view_account

from tool_objects import ToolTemplate

from gnc_builder import GncBuilder

from gnc_amount_edit import GNCAmountEditPython

from gnc_commodity_edit import GncCommodityEdit

from gnc_date_edit import GncDateEdit

import gnc_tree_model_account_types

from dialog_commodity import DialogCommodity

import swighelpers


#import qof_ctypes


from pygobjectcapi import PyGObjectCAPI
#from pygobjectcapi_gi import PyGObjectCAPI


Cgobject = PyGObjectCAPI()



class EditAccountWindow(object):

    NEW_ACCOUNT = 0
    EDIT_ACCOUNT = 1


    def __init__ (self, parent, account):

        self.book = get_current_book()

        self.dialog_type = EditAccountWindow.EDIT_ACCOUNT

        # and another one not right
        self.acc_type = account.GetType()

        # this is not right - not sure where initialized
        self.valid_types = 0

        self.commodity_mode = 0

        self.account = account

        # as of gnucash 3 we now can get access to these via GObject properties supposedly
        #pdb.set_trace()

        # this is how to convert from SWIG object to underlying GObject
        # note not sure if this checks the SWIG object is a GObject!!
        account_ptr = self.account.instance.__int__()
        accountobj = Cgobject.to_object(account_ptr)

        # note that get_property returns a gobject - so need to transform to swig/gnucash form
        check_inc = accountobj.find_property("ofx-associated-income-account")
        if check_inc != None:
            income_guid_gobj = accountobj.get_property("ofx-associated-income-account")
            if income_guid_gobj != None:
                pdb.set_trace()
                income_guid_str = income_guid_gobj.to_string()
                income_guid = gnucash.GUID.string_to_guid(income_guid_str)
            else:
                income_guid = None
                income_guid_str = "None"
        else:
            income_guid = None
            income_guid_str = "None"

        #income_guid_str = qof_ctypes.GetAssociatedAccountGUIDString(self.account,"ofx/associated-income-account")

        print("income_guid", income_guid_str, file=sys.stderr)

        #income_guid = qof_ctypes.GetAssociatedAccountGUID(self.account,"ofx/associated-income-account")

        if income_guid != None:
            self.income_account = gnucash.GUID.AccountLookup(income_guid, self.book)
            if self.income_account != None:
                print("income_acc", self.income_account.GetName(), file=sys.stderr)
        else:
            self.income_account = None

        print("income_guid", income_guid, file=sys.stderr)

        check_fee = accountobj.find_property("ofx-associated-fee-account")
        if check_fee != None:
            fee_guid_gobj = accountobj.get_property("ofx-associated-fee-account")
            if fee_guid_gobj != None:
                pdb.set_trace()
                fee_guid_str = fee_guid_gobj.to_string()
                fee_guid = gnucash.GUID.string_to_guid(fee_guid_str)
            else:
                fee_guid = None
                fee_guid_str = "None"
        else:
            fee_guid = None
            fee_guid_str = "None"

        #fee_guid_str = qof_ctypes.GetAssociatedAccountGUIDString(self.account,"ofx/associated-fee-account")

        print("fee_guid", fee_guid_str, file=sys.stderr)

        #fee_guid = qof_ctypes.GetAssociatedAccountGUID(self.account,"ofx/associated-fee-account")

        if fee_guid != None:
            self.fee_account = gnucash.GUID.AccountLookup(fee_guid, self.book)
            if self.fee_account != None:
                print("fee_acc", self.fee_account.GetName(), file=sys.stderr)
        else:
            self.fee_account = None

        #pdb.set_trace()

        builder = GncBuilder()
        gnc_builder_dir = os.path.join(os.environ['HOME'],'.gnucash','gtkbuilder')
        fname = os.path.join(gnc_builder_dir,"dialog-account.glade")
        builder.add_from_file(fname, "fraction_liststore")
        builder.add_from_file(fname, "account_dialog")

        # junkily we need to list all signals here
        # the gnucash code somehow figures all signals
        self.builder_handlers = { \
                                'gnc_account_window_destroy_cb' : self.destroy_cb,
                                'opening_equity_cb' : self.opening_equity_cb,
                                'gnc_account_name_changed_cb' : self.name_changed_cb,
                                'gnc_account_name_insert_text_cb' : self.name_insert_text_cb,
                                'gnc_account_color_default_cb' : self.color_default_cb,
                                'gnc_account_assoc_fee_changed_cb' : self.fee_changed_cb,
                                'gnc_account_assoc_fee_insert_text_cb' : self.fee_insert_text_cb,
                                'gnc_account_assoc_income_changed_cb' : self.income_changed_cb,
                                'gnc_account_assoc_income_insert_text_cb' : self.income_insert_text_cb,
                                }

        # in gnucash this can be modal or not - if modal then DONT connect signals
        # as we are doing this externally I think this is not modal

        #builder.connect_signals(self)
        #builder.connect_signals(self.builder_handlers)

        self.dialog = builder.get_object("account_dialog")

        # this registers the dialog so the initial count check works
        #gnc_register_gui_component (DIALOG_FINCALC_CM_CLASS,
        #                            NULL, close_handler, fcd);

        # set style and parent
        #self.dialog.get_path().iter_set_object_name(0,"GncAccountDialog")
        if parent != None:
            self.dialog.set_transient_for(parent)

        # why is this not working - works for other objects??
        # as of gtk3 this is just a python property
        # well thats not working!!
        #self.dialog.set_data("dialog_info",self)
        self.dialog.dialog_info = self

        if not self.dialog.get_modal():
             self.dialog.connect("response", self.response_cb)
        else:
             self.dialog.set_modal(True)

        self.notebook = builder.get_object("account_notebook")
        self.name_entry = builder.get_object("name_entry")
        self.description_entry = builder.get_object("description_entry")
        self.color_entry_button = builder.get_object("color_entry_button")
        self.color_default_button = builder.get_object("color_default_button")
        self.code_entry = builder.get_object("code_entry")

        self.notes_text_buffer = builder.get_object("notes_text").get_buffer()

        self.fee_entry = builder.get_object("fee_entry")
        self.income_entry = builder.get_object("income_entry")

        box = builder.get_object("commodity_hbox")

        # we are not doing this right!!
        self.commodity_edit = GncCommodityEdit()
        #DialogCommodity.DIAG_COMM_ALL

        box.pack_start(self.commodity_edit, expand=True,fill=True,padding=0)
        self.commodity_edit.show()

        label = builder.get_object("security_label")
        self.commodity_edit.make_mnemonic_target(label)

        self.commodity_edit.connect("changed", self.commodity_changed_cb, self)

        self.account_scu = builder.get_object("account_scu")

        box = builder.get_object("parent_scroll")

        self.parent_tree = gnc_tree_view_account.new(True)
        box.add(self.parent_tree)
        self.parent_tree.show()
        selection = self.parent_tree.get_selection()
        selection.connect("changed", self.parent_changed_cb, self)

        self.tax_related_button = builder.get_object("tax_related_button")
        self.placeholder_button = builder.get_object("placeholder_button")
        self.hidden_button = builder.get_object("hidden_button")

        box = builder.get_object("opening_balance_box")

        amount = GNCAmountEditPython()
        self.opening_balance_edit = amount

        box.pack_start(amount,expand=True,fill=True,padding=0)
        amount.set_evaluate_on_enter(True)
        amount.show()

        label = builder.get_object("balance_label")
        label.set_mnemonic_widget(amount)

        box = builder.get_object("opening_balance_date_box")
        # which version to choose here
        date_edit = GncDateEdit.new(datetime.datetime.now(), True, True)
        self.opening_balance_date_edit = date_edit
        box.pack_start(date_edit,expand=True,fill=True,padding=0)
        date_edit.show()

        self.opening_balance_page = self.notebook.get_nth_page(1)

        self.opening_equity_radio = builder.get_object("opening_equity_radio")

        box = builder.get_object("transfer_account_scroll")
        self.transfer_account_scroll = box

        self.transfer_tree = gnc_tree_view_account.new(False)
        selection = self.transfer_tree.get_selection()
        selection.set_select_function(self.account_commodity_filter, self)

        box.add(self.transfer_tree)
        self.transfer_tree.show()

        label = builder.get_object("parent_label")
        label.set_mnemonic_widget(self.parent_tree)

        # /* This goes at the end so the select callback has good data. */
        self.type_view = builder.get_object("type_view")
        self.type_view_create()

        #self.dialog.restore_window_size()

        self.name_entry.grab_focus()

        #self.connect_signals()
        builder.connect_signals(self.builder_handlers)

    def destroy_cb (self, actionobj, userdata=None):
        print("destroy_cb",actionobj,userdata, file=sys.stderr)
        self.dialog.destroy()

    def delete_cb (self, actionobj, userdata=None):
        print("delete_cb",actionobj,userdata, file=sys.stderr)
        self.dialog.destroy()

    def response_cb (self, actionobj, response=None):
        print("response_cb",actionobj,response, file=sys.stderr)
        if response == Gtk.ResponseType.OK or \
           response == Gtk.ResponseType.CLOSE:
            #gnc_save_window_size(GNC_PREFS_GROUP, self.dialog)
            pass
        #gnc_close_gui_component_by_data (DIALOG_FINCALC_CM_CLASS, fcd)
        self.dialog.destroy()

    def opening_equity_cb (self, actionobj, userdata=None):
        print("opening_equity_cb",actionobj,userdata, file=sys.stderr)
        use_equity = actionobj.get_active()
        self.transfer_account_scroll.set_sensitive(not use_equity)


    def name_changed_cb (self, actionobj, userdata=None):
        print("name_changed_cb",actionobj,userdata, file=sys.stderr)
        self.set_name()

    def name_insert_text_cb (self, actionobj, text, text_length_or_position, userdata=None):
        print("name_insert_text_cb",actionobj,text,text_length_or_position,userdata, file=sys.stderr)
        editable = actionobj
        separator = engine_ctypes.GetAccountSeparatorString()
        strsplt = text.split(separator)
        if len(strsplt) > 1:
            result = "".join(strsplt)
            print("name_insert_text_cb",result, file=sys.stderr)
            # how do I get the handler ID for these
            #editable.handler_block(self.name_insert_text_cb_id)
            editable.insert_text(result)
            #editable.handler_unblock(self.name_insert_text_cb_id)
            #editable.emit_stop_by_name("insert_text")
            

    def fee_changed_cb (self, actionobj, userdata=None):
        print("fee_changed_cb",actionobj,userdata, file=sys.stderr)
        #self.set_name()

    def fee_insert_text_cb (self, actionobj, text, text_length_or_position, userdata=None):
        print("fee_insert_text_cb",actionobj,text,text_length_or_position,userdata, file=sys.stderr)
        editable = actionobj
        #separator = sw_engine.gnc_get_account_separator_string()
        separator = engine_ctypes.GetAccountSeparatorString()
        strsplt = text.split(separator)
        if len(strsplt) > 1:
            result = "".join(strsplt)
            print("fee_insert_text_cb",result, file=sys.stderr)
            # how do I get the handler ID for these
            #editable.handler_block(self.fee_insert_text_cb_id)
            editable.insert_text(result)
            #editable.handler_unblock(self.fee_insert_text_cb_id)
            #editable.emit_stop_by_name("insert_text")


    def income_changed_cb (self, actionobj, userdata=None):
        print("income_changed_cb",actionobj,userdata, file=sys.stderr)
        #self.set_name()

    def income_insert_text_cb (self, actionobj, text, text_length_or_position, userdata=None):
        print("income_insert_text_cb",actionobj,text,text_length_or_position,userdata, file=sys.stderr)
        editable = actionobj
        #separator = sw_engine.gnc_get_account_separator_string()
        separator = engine_ctypes.GetAccountSeparatorString()
        strsplt = text.split(separator)
        if len(strsplt) > 1:
            result = "".join(strsplt)
            print("income_insert_text_cb",result, file=sys.stderr)
            # how do I get the handler ID for these
            #editable.handler_block(self.income_insert_text_cb_id)
            editable.insert_text(result)
            #editable.handler_unblock(self.income_insert_text_cb_id)
            #editable.emit_stop_by_name("insert_text")


    def color_default_cb (self, actionobj, userdata=None):
        print("color_default_cb",actionobj,userdata, file=sys.stderr)
        color =  Gtk.Gdk.color_parse("#ededececebeb")
        self.color_entry_button.set_color(color)

    def commodity_changed_cb (self, actionobj, selected, userdata=None):
        print("commodity_changed_cb",actionobj,selected,userdata, file=sys.stderr)

        currency = actionobj.get_selected()
        if currency == None:
            return

        # at the moment CommodityPrintInfo is not part of GncCommodity class
        self.opening_balance_edit.set_fraction(currency.get_fraction())
        self.opening_balance_edit.set_print_info(CommodityPrintInfo(currency,False))

        selection = self.transfer_tree.get_selection()
        selection.unselect_all()

    def parent_changed_cb (self, actionobj, userdata=None):
        print("parent_changed_cb",actionobj,userdata, file=sys.stderr)
        parent_account = self.parent_tree.do_get_selected_account()
        print("parent_changed_cb",parent_account, file=sys.stderr)
        if parent_account == None:
            return

        if parent_account.is_root():
            acc_types = self.valid_types
        else:
            #acc_types = self.valid_types & sw_engine.xaccParentAccountTypesCompatibleWith(parent_account.GetType())
            acc_types = self.valid_types & engine_ctypes.ParentAccountTypesCompatibleWith(parent_account.GetType())

        type_model = self.type_view.get_model()

    def type_changed_cb (self, selection, userdata=None):
        print("type_changed_cb",selection,userdata, file=sys.stderr)
        sensitive = False

        type_id = gnc_tree_model_account_types.get_selection_single(selection)

        if type_id == gnucash.gnucash_core_c.ACCT_TYPE_NONE:
            self.acc_type = gnucash.gnucash_core_c.ACCT_TYPE_INVALID
        else:
            self.acc_type = type_id
            self.preferred_acc_type = type_id

            self.commodity_from_type(True)

            sensitive = (self.acc_type != gnucash.gnucash_core_c.ACCT_TYPE_EQUITY and \
                         self.acc_type != gnucash.gnucash_core_c.ACCT_TYPE_CURRENCY and \
                         self.acc_type != gnucash.gnucash_core_c.ACCT_TYPE_STOCK and \
                         self.acc_type != gnucash.gnucash_core_c.ACCT_TYPE_MUTUAL and \
                         self.acc_type != gnucash.gnucash_core_c.ACCT_TYPE_TRADING)


    def set_name (self):

        # self.get_ui_fullname()

        # this gets a full account path name
        if self.dialog_type == EditAccountWindow.EDIT_ACCOUNT:
            self.dialog.set_title(N_("Edit Account"+" - "+self.account.GetName()))
        #allows for multiple new accounts?? - not implemented
        else:
            self.dialog.set_title(N_("New Account"))

    def type_view_create (self):

        if self.valid_types == 0:
            #self.valid_types = sw_engine.xaccAccountTypesValid() | (1 << self.acc_type)
            self.valid_types = engine_ctypes.AccountTypesValid() | (1 << self.acc_type)
            self.preferred_account_type = self.acc_type
        elif (self.valid_types & (1 << self.acc_type)) != 0:
            self.preferred_account_type = self.acc_type
        elif (self.valid_types & (1 << self.last_used_account_type)) != 0:
            self.acc_type = self.last_used_account_type
            self.preferred_account_type = self.last_used_account_type
        else:
            pass

        model = gnc_tree_model_account_types.filter_using_mask(self.valid_types)

        # extract the static model and save
        self.account_types_tree_model = model.get_model()

        self.type_view.set_model(model)
        # c unrefs model - g_object_unref(model) - do we need to do this??

        renderer = Gtk.CellRendererText()

        self.type_view.insert_column_with_attributes(-1,"",renderer,text=gnc_tree_model_account_types.GNC_TREE_MODEL_ACCOUNT_TYPES_COL_NAME)

        self.type_view.set_search_column(gnc_tree_model_account_types.GNC_TREE_MODEL_ACCOUNT_TYPES_COL_NAME)

        selection = self.type_view.get_selection()
        selection.connect("changed", self.type_changed_cb, self)

        gnc_tree_model_account_types.set_selection(selection, 1 << self.acc_type)


    def account_commodity_filter (self, selection, unused_model, s_path, path_currently_selected, userdata):

        if path_currently_selected:
            return True

        account = self.transfer_tree.get_account_from_path(s_path)

        if not account:
            return False

        commodity = self.commodity_edit.get_selected()

        #retval = sw_engine.gnc_commodity_equiv(account.GetCommodity(), commodity)
        retval = engine_ctypes.CommodityEquiv(account.GetCommodity(), commodity)

        return retval

    def commodity_from_type (self, update):

        if self.acc_type == gnucash.gnucash_core_c.ACCT_TYPE_TRADING:
            new_mode = DialogCommodity.py.DIAG_COMM_ALL
        elif (self.acc_type == gnucash.gnucash_core_c.ACCT_TYPE_TRADING) or (self.acc_type == gnucash.gnucash_core_c.ACCT_TYPE_MUTUAL):
            new_mode = DialogCommodity.DIAG_COMM_NON_CURRENCY
        else:
            new_mode = DialogCommodity.DIAG_COMM_CURRENCY

        if update and (new_mode != self.commodity_mode):

            self.commodity_edit.set_selected(None)

        self.commodity_mode = new_mode

    def account_to_ui (self):

        #print(dir(self.account), file=sys.stderr)

        #pdb.set_trace()

        # this leads to error message Warning: g_value_get_int: assertion 'G_VALUE_HOLDS_INT (value)' failed
        # - apparently due to bug in gobject introspection
        self.name_entry.set_text(self.account.GetName())
        self.description_entry.set_text(self.account.GetDescription())
        # the C code does not check for Not Set - how does it work??
        if self.account.GetColor() != None and self.account.GetColor() != 'Not Set':
            print("color is",self.account.GetColor(), file=sys.stderr)
            self.color_entry_button.set_color(Gtk.Gdk.color_parse(self.account.GetColor()))
        self.commodity_edit.set_selected(self.account.GetCommodity())
        self.commodity_from_type(False)
        # weird SCU stuff here
        self.code_entry.set_text(self.account.GetCode())
        if self.account.GetNotes() != None:
            self.notes_text_buffer.set_text(self.account.GetNotes())
        self.tax_related_button.set_active(self.account.GetTaxRelated())
        self.placeholder_button.set_active(self.account.GetPlaceholder())
        self.hidden_button.set_active(self.account.GetHidden())

        if self.fee_account != None:
            self.fee_entry.set_text(self.fee_account.GetName())
        if self.income_account != None:
            self.income_entry.set_text(self.income_account.GetName())



class DialogEditAccount(object):


    def __init__ (self, parent=None):

        self.parent = parent

        #self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        #self.window.set_position(gtk.WIN_POS_CENTER)
        self.window = Gtk.Window()
        #self.window.set_position(Gtk.WIN_POS_CENTER)
        self.window.set_default_size(300,300)
        self.window.set_border_width(0)
        self.window.connect('destroy-event', self.destroy_cb)
        self.window.connect('delete-event', self.delete_cb)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_homogeneous(False)
        # using str= parameter does not work
        #label = Gtk.Label(str=N_("Enter Account Name:"))
        # which one to use??
        label = Gtk.Label()
        label.set_text(N_("Enter Account Name:"))
        #label.set_label(N_("Enter Account Name:"))
        # no keyword args for introspection??
        #hbox.pack_start(label, expand=False, fill=False, padding=0)
        hbox.pack_start(label, False, False, 0)
        entry = Gtk.Entry()
        entry.set_max_length(50)
        entry.select_region(0,len(entry.get_text()))
        entry.connect_object("activate", self.edit_account_cb, entry)
        hbox.pack_start(entry, False, False, 0)
        button = Gtk.Button(label="My Button")
        self.window.add(hbox)
        self.window.show_all()

    def destroy_cb (self, actionobj, userdata=None):
        self.window.destroy()

    def delete_cb (self, actionobj, userdata=None):
        self.window.destroy()

    def edit_account_cb (self, actionobj, userdata=None):
        print("edit_account_cb",actionobj,userdata, file=sys.stderr)

        # I think all the following is done in the run function

        # this I think detects if the dialog is already open
        #edit_account = gnc_find_first_gui_component (DIALOG_EDIT_ACCOUNT_CM_CLASS,
        #                               find_by_account, account))
        #if edit_account != None:
        #    edit_account.dialog.present()
        #    self.window.destroy()
        #    return

        account_name = actionobj.get_text()
        print("account name",account_name)
        book = get_current_book()
        root = book.get_root_account()
        editacnt = root.LookupByName(account_name)
        edit_account = EditAccountWindow(self.parent,editacnt)
        edit_account.account_to_ui()
        edit_account.dialog.show()
        self.window.destroy()



class DialogEditAccountTool(ToolTemplate):

    def __init__ (self):

        super(DialogEditAccountTool,self).__init__()

        # need to set the  base variables
        self.version = 1
        self.name = N_("Edit Account Tool")
        self.tool_guid = "a9046faf72dd48dcb4976902af097b99"
        self.menu_name = N_("Edit Account Tool")
        self.menu_tip = N_("Edit Account Tool")
        #self.menu_path = N_("Tool Path")
        #self.stock_id = None

        #self.amounts = {}

    def run (self, parent):

        dea = DialogEditAccount(parent)

        #dea.init_fi()

        #dea.fi_to_gui()

        dea.window.show()

        # junky direct fixup while alpha debugging
        #book = get_current_book()
        #root = book.get_root_account()
        #editacnt = root.LookupByName("Books")
        #editwindw = EditAccountWindow(editacnt)
        #editwindw.account_to_ui()
        #editwindw.dialog.show()
