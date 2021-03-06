
# this is a recoding of the options dialog (defined in dialog-options.c)
# in python
# needed because dialog-options.c has functions with SCM data
# which need to be replaced

# some functions also taken from option-util.c in app-utils

import os

import sys

import bisect

import numbers

import time

import traceback

import pdb

from operator import attrgetter

from gi.repository import GObject

from gi.repository import Gtk
from gi.repository import Gdk


import ctypes


import gc


import sw_core_utils
import sw_app_utils


try:
    from gnc_builder import GncBuilder
    from gnc_date_edit import GncDateEdit
    from gnc_currency_edit import GncCurrencyEdit
    from gnc_general_select import GncGeneralSelect
    from gnc_commodity_edit import GncCommodityEdit
    import gnc_tree_view_account
except Exception as errexc:
    traceback.print_exc()
    pdb.set_trace()


import gnucash

from gnucash_log import PERR

log_module = "gnc.gui.python"


NUM_ACCOUNT_TYPES = gnucash.gnucash_core_c.NUM_ACCOUNT_TYPES


# junky internationalization function
def N_(msg):
    return msg

# option dialog calls

#12 0x000000010003f262 in gnc_plugin_page_report_options_cb ()
#1  0x000000010004135a in gnc_report_window_default_params_editor ()
#0  0x00000001001e9354 in gnc_options_dialog_build_contents ()


class GncOption(object):

    # ah - the primary purpose of this class is to provide the functionality
    # to interact with an options value through the gtk GUI

    def __init__ (self, guile_option, changed=False, widget=None, odb=None):
        self.guile_option = guile_option
        self.changed = changed
        self.widget = widget
        self.odb = odb

        # we may define a widget_changed_proc
        #self.widget_changed_proc = None

    def get_ui_value (self):
        # OK this is really stupid - we have multiple redirection here
        # we call a function in the GncOptionDB class
        # which by default is set to the internal function in this class
        # note that this is for getting the option value from the GUI
        # and storing it in the basic option
        #return self.odb.get_ui_value(self)
        # for the moment punt just call the internal function directly
        return self.get_ui_value_internal()

    def set_ui_value (self, use_default):
        # this is weird - wheres the value 
        # not needed - this sets the ui widget value to the option value!!
        #if self.odb.get_ui_value == None:
        #    return
        #self.odb.set_ui_value(self,use_default)
        # for the moment punt just call the internal function directly
        self.set_ui_value_internal(use_default)

    def ui_get_option (self, option_type_name):
        # this should really be ui_get_option_type
        global optionTable
        if option_type_name in optionTable:
            return optionTable[option_type_name]
        else:
            PERR(log_module,"Option lookup for type '%s' failed!"%option_type_name)
            print("Option lookup for type '%s' failed!"%option_type_name)
            pdb.set_trace()
            return None

    def value_validator (self):
        if hasattr(self.guile_option, 'value_validator'):
            return self.guile_option.value_validator
        else:
            return None

    def set_ui_value_internal (self, use_default):

        # this uses the option type (string, boolean)
        # to set the scheme value into the widget for the option
        #pdb.set_trace()

        widget = self.widget
        if widget == None:
            return None
        option_type = self.guile_option.type
        if use_default:
            value = self.guile_option.default_getter()
        else:
            value = self.guile_option.getter()
        option_def = self.ui_get_option(option_type)
        if option_def:
            bad_value = option_def.set_value(self,use_default,widget,value)
            if bad_value:
                PERR(log_module,"bad value")
                print("bad value for option", option_type,self.guile_option.name,value)
                pdb.set_trace()
                pass
        else:
            PERR(log_module,"Unknown type. Ignoring.")
            pdb.set_trace()
            pass

    def get_ui_value_internal (self):

        widget = self.widget
        if widget == None:
            return None
        option_type = self.guile_option.type
        option_def = self.ui_get_option(option_type)
        if option_def:
            result = option_def.get_value(self,widget)
        else:
            PERR(log_module,"Unknown type for refresh. Ignoring.")
            pdb.set_trace()
            result = None
        return result

    def set_selectable_internal (self, selectable):

        widget = self.widget
        if widget == None:
            return None
        widget.set_sensitive(selectable)

    def changed_internal (self, widget, sensitive):
        # this needs to start in this class

        print("GncOption changed_internal",str(widget),type(widget))
        #pdb.set_trace()

        #oldwidget = widget.get_ancestor(Gtk.Dialog)
        print("changed_internal 1a",str(widget),isinstance(widget, Gtk.Dialog))
        while widget and not isinstance(widget, Gtk.Dialog):
            print("changed_internal 1a",str(widget),isinstance(widget, Gtk.Dialog))
            widget = widget.get_parent()
        print("changed_internal 2",str(widget),isinstance(widget, Gtk.Dialog))
        if widget == None:
            return

        widget.set_response_sensitive(Gtk.ResponseType.OK, sensitive)
        widget.set_response_sensitive(Gtk.ResponseType.APPLY, sensitive)


    def call_widget_changed_proc (self):
        if hasattr(self,"widget_changed_proc"):
            value = self.get_ui_value()
            if value != None:
                self.widget_changed_proc(value)

    def changed_widget_cb (self, entry):
        print("changed_widget_cb",str(entry))
        #pdb.set_trace()
        #gc.collect()
        self.changed = True
        #self.call_widget_changed_proc()
        # ah - the widget is the dialog box the option is in
        self.changed_internal(entry,True)

    def multichoice_cb (self, entry):
        print("multichoice_cb")
        # this just maps GtkColorButton to widget and calls changed_widget_cb
        self.changed_widget_cb(entry)


    def commit (self):
        print("commit called")
        value = self.get_ui_value()
        if value == None:
            return
        validator = self.value_validator()
        if validator != None:
            result = validator(value)
        else:
            # punt for the moment
            result = [True, value, None]

        # from scheme looks like we get a list
        if result == None or not isinstance(result,list):
            PERR("bad validation result")
            return
        ok = result[0]
        if not isinstance(ok,bool):
            PERR("bad validation result")
            return
        if ok:
            value = result[1]
            self.guile_option.setter(value)
            self.set_ui_value(False)
        else:
            oops = result[2]
            if not isinstance(oops,str):
                PERR("bad validation result")
                return
            #utf8 conversion here
            name = self.name
            section = self.section
            if True:
                dialog = Gtk.MessageDialog(None,Gtk.DialogFlags.DESTROY_WITH_PARENT,
                        Gtk.MessageType.ERROR,Gtk.ButtonsType.OK,N_("There is a problem with option %s:%s.\n%s")%(section,name,oops))
                dialog.run()
                dialog.destroy()
            else:
                print("There is a problem with option %s:%s.\n%s"%(section,name,oops))


    def set_ui_widget (self, page_box):

        packed = False

        guile_option = self.guile_option

        #ENTER("option %p(%s), box %p",
        #      option, gnc_option_name(option), page_box);
        if guile_option.type == None:
            #LEAVE("bad type");
            return

        raw_name = guile_option.name
        if raw_name != None and raw_name != "":
            name = N_(raw_name)
        else:
            name = None

        raw_documentation = guile_option.documentation_string
        if raw_documentation != None and raw_documentation != "":
            documentation = N_(raw_documentation)
        else:
            documentation = None

        # we store the option type (string, boolean etc) in optionTable
        # and we lookup the function to use by option type
        option_def = self.ui_get_option(guile_option.type)

        value = None
        enclosing = None
        packed = None

        # so in python I think we just set the function by the various option classes
        # the scheme solution defines functions by type - with python would have
        # functions by option instance - but cannot figure if would ever want to be able
        # to change function definitions in middle of report globally by type
        # interesting - we do need to add a first argument for this indirect call
        # is it because we used the class definition of the function??
        if option_def and option_def.set_widget != None:
            try:
                (value, enclosing, packed) = option_def.set_widget(self, page_box, name, documentation)
            except Exception as errexc:
                traceback.print_exc()
                pdb.set_trace()
        else:
            PERR(log_module,"Unknown option type. Ignoring option \"%s\"."%name)
            pdb.set_trace()

        if not packed and enclosing != None:

            eventbox = Gtk.EventBox()

            eventbox.add(enclosing)
            page_box.pack_start(eventbox, False, False, 0)

            eventbox.set_tooltip_text(documentation)

        if value != None:
            value.set_tooltip_text(documentation)

    def get_color_info (self, use_default):
        if use_default:
            #return self.guile_option.default_getter()
            rgba = self.guile_option.default_getter()
            scale = self.guile_option.option_data[0]
        else:
            #return self.guile_option.getter()
            rgba = self.guile_option.getter()
            scale = self.guile_option.option_data[0]
        scale = 1.0/scale
        red = rgba[0]*scale
        green = rgba[1]*scale
        blue = rgba[2]*scale
        alpha = rgba[3]*scale
        return (red, green, blue, alpha)

    def get_range_info (self):
        rng = self.guile_option.option_data
        return rng

    # load of set callback functions
    def set_ui_widget_boolean (self, page_box, name, documentation):

        #colon_name = name + ":"
        #label = Gtk.Label(colon_name)
        #label.set_alignment(1.0, 0.5)

        #enclosing = Gtk.HBox(homogeneous=False, spacing=5)
        enclosing = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        enclosing.set_homogeneous(False)

        value = Gtk.CheckButton(label=name)

        self.widget = value
        self.set_ui_value(False)

        value.connect("toggled",self.changed_widget_cb)

        #enclosing.pack_start(label, False, False, 0)
        enclosing.pack_start(value, False, False, 0)
        enclosing.show_all()

        # need to figure what goes on with packed - is it pass through??
        return (value, enclosing, None)

    def set_ui_value_boolean (self, use_default, widget, value):
        if isinstance(value,bool):
            widget.set_active(value)
            return False
        else:
            return True
    def get_ui_value_boolean (self, widget):
        newval = widget.get_active()
        return newval

    def set_ui_widget_string (self, page_box, name, documentation):

        colon_name = name + ":"
        label = Gtk.Label(colon_name)
        label.set_alignment(1.0, 0.5)

        #enclosing = Gtk.HBox(homogeneous=False, spacing=0)
        enclosing = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        enclosing.set_homogeneous(False)

        value = Gtk.Entry()

        self.widget = value
        self.set_ui_value(False)

        value.connect("changed",self.changed_widget_cb)

        enclosing.pack_start(label, False, False, 0)
        enclosing.pack_start(value, False, False, 0)
        enclosing.show_all()

        # need to figure what goes on with packed - is it pass through??
        return (value, enclosing, None)

    def set_ui_value_string (self, use_default, widget, value):
        if isinstance(value,str):
            # we get conversion to utf8 here - ignoring for the moment
            widget.set_text(value)
            return False
        else:
            return True
    def get_ui_value_string (self, widget):
        newstr = widget.get_text()
        # need to check utf-8'ness here
        return newstr
    def set_ui_widget_text (self, page_box,  name, documentation, enclosing=None, packed=None):
        print("set_ui_widget_text")
    def set_ui_value_text (self, use_default, widget, value):
        print("set_ui_value_text")
    def get_ui_value_text (self, widget):
        print("get_ui_value_text")
    def set_ui_widget_currency (self, page_box,  name, documentation, enclosing=None, packed=None):
        print("set_ui_widget_currency")

        colon_name = name + ":"
        label = Gtk.Label(colon_name)
        label.set_alignment(1.0, 0.5)

        #enclosing = Gtk.HBox(homogeneous=False, spacing=5)
        enclosing = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        enclosing.set_homogeneous(False)

        value = GncCurrencyEdit()

        self.widget = value
        self.set_ui_value(False)

        value.connect("changed",self.changed_widget_cb)

        enclosing.pack_start(label, False, False, 0)
        enclosing.pack_start(value, False, False, 0)
        enclosing.show_all()

        # need to figure what goes on with packed - is it pass through??
        return (value, enclosing, None)
    def set_ui_value_currency (self, use_default, widget, value):
        print("set_ui_value_currency")
        if isinstance(value,gnucash.GncCommodity):
            widget.set_currency(value)
            return False
        else:
            return True
    def get_ui_value_currency (self, widget):
        print("get_ui_value_currency")
        newcommod = widget.get_currency()
        return newcommod
    def set_ui_widget_commodity (self, page_box,  name, documentation, enclosing=None, packed=None):
        print("set_ui_widget_commodity")
        #pdb.set_trace()

        colon_name = name + ":"
        label = Gtk.Label(colon_name)
        label.set_alignment(1.0, 0.5)

        #enclosing = Gtk.HBox(homogeneous=False, spacing=5)
        enclosing = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        enclosing.set_homogeneous(False)

        # this is not very pythonic
        # changing - make GncCommodityEdit subclass of GncGeneralSelect
        #value = GncGeneralSelect(GNC_GENERAL_SELECT_TYPE_SELECT, 
        #                           gnc_commodity_edit_get_string,
        #                           gnc_commodity_edit_new_select)
        value = GncCommodityEdit()

        #pdb.set_trace()

        self.widget = value
        self.set_ui_value(False)

        if documentation:
            value.entry.set_tooltip_text(documentation)

        value.entry.connect("changed",self.changed_widget_cb)

        enclosing.pack_start(label, False, False, 0)
        enclosing.pack_start(value, False, False, 0)
        enclosing.show_all()

        # need to figure what goes on with packed - is it pass through??
        return (value, enclosing, None)
    def set_ui_value_commodity (self, use_default, widget, value):
        print("set_ui_value_commodity")
        #pdb.set_trace()
        if isinstance(value,gnucash.GncCommodity):
            widget.set_selected(value)
            return False
        else:
            return True
    def get_ui_value_commodity (self, widget):
        print("get_ui_value_commodity")
        #pdb.set_trace()
        newcommod = widget.get_selected()
        return newcommod
    def set_ui_widget_multichoice (self, page_box,  name, documentation, enclosing=None, packed=None):
        colon_name = name + ":"
        label = Gtk.Label(colon_name)
        label.set_alignment(1.0, 0.5)

        #enclosing = Gtk.HBox(homogeneous=False, spacing=5)
        enclosing = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        enclosing.set_homogeneous(False)

        value = self.create_multichoice_widget()

        self.widget = value
        self.set_ui_value(False)

        enclosing.pack_start(label, False, False, 0)
        enclosing.pack_start(value, False, False, 0)
        enclosing.show_all()

        # need to figure what goes on with packed - is it pass through??
        return (value, enclosing, None)
    def set_ui_value_multichoice (self, use_default, widget, value):
        indx_value = self.guile_option.lookup_key(value)
        if indx_value >= 0 and indx_value < len(self.guile_option.option_data):
            widget.set_active(indx_value)
            return False
        else:
            return True
    def get_ui_value_multichoice (self, widget):
        # big question is whether to base from 0 or 1 - now going with 0
        # raw indexes are base 0
        newmulti = widget.get_active()
        # lots of options use the function (in option-util.c)
        # gnc_option_permissible_value that checks in value in range
        if newmulti >= 0 and newmulti < len(self.guile_option.option_data):
            newval = self.guile_option.option_data[newmulti][0]
        else:
            newval = None
        #pdb.set_trace()
        return newval
    def set_ui_widget_date (self, page_box,  name, documentation, enclosing=None, packed=None):
        print("set_ui_widget_date")

        colon_name = name + ":"
        label = Gtk.Label(colon_name)
        label.set_alignment(1.0, 0.5)

        #enclosing = Gtk.HBox(homogeneous=False, spacing=0)
        enclosing = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        enclosing.set_homogeneous(False)

        value = self.create_date_widget()

        self.widget = value

        enclosing.pack_start(label, False, False, 0)
        enclosing.pack_start(value, False, False, 0)

        eventbox = Gtk.EventBox()
        eventbox.add(enclosing)
        page_box.pack_start(eventbox, False, False, 0)

        packed = True

        eventbox.set_tooltip_text(self.guile_option.documentation_string)

        self.set_ui_value(False)

        enclosing.show_all()

        # need to figure what goes on with packed - is it pass through??
        return (value, enclosing, packed)
    def set_ui_value_date (self, use_default, widget, value):
        print("set_ui_value_date")
        #pdb.set_trace()
        bad_value = False
        if use_default:
            date_option_type = self.guile_option.default_value[0]
        else:
            date_option_type = self.guile_option.option_data[0]
        vltupl = self.guile_option.getter()
        if vltupl[0] == 'relative':
            relative = vltupl[1]
            indx = self.guile_option.lookup_key(relative)
            if date_option_type == 'relative':
                widget.set_active(indx)
            elif date_option_type == 'both':
                widget_list = widget.get_children()
                rel_date_widget = widget_list[GncDateEdit.GNC_RD_WID_REL_WIDGET_POS]
                self.set_select_method(False,True)
                rel_date_widget.set_active(indx)
        elif vltupl[0] == 'absolute':
            dttm = vltupl[1]
            if date_option_type == 'absolute':
                widget.set_time_dt(dttm)
            elif date_option_type == 'both':
                widget_list = widget.get_children()
                ab_date_widget = widget_list[GncDateEdit.GNC_RD_WID_AB_WIDGET_POS]
                self.set_select_method(True,True)
                ab_date_widget.set_time_dt(dttm)
            else:
                bad_value = True
        else:
            bad_value = True
        return bad_value
    def get_ui_value_date (self, widget):
        print("get_ui_value_date")
        #pdb.set_trace()
        subtype = self.guile_option.option_data[0]
        widget_list = widget.get_children()
        if subtype == 'relative':
            #pdb.set_trace()
            #rel_date_widget = widget_list[GncDateEdit.GNC_RD_WID_REL_WIDGET_POS]
            rel_date_widget = widget
            relval = rel_date_widget.get_active()
            relval = self.guile_option.lookup_index(relval)
            retval = ('relative', relval)
        elif subtype == 'absolute':
            #pdb.set_trace()
            #ab_date_widget = widget_list[GncDateEdit.GNC_RD_WID_AB_WIDGET_POS]
            ab_date_widget = widget
            #absval = ab_date_widget.get_property('time')
            absval = ab_date_widget.get_date()
            retval = ('absolute', absval)
        elif subtype == 'both':
            #pdb.set_trace()
            ab_button = widget_list[GncDateEdit.GNC_RD_WID_AB_BUTTON_POS]
            ab_date_widget = widget_list[GncDateEdit.GNC_RD_WID_AB_WIDGET_POS]
            rel_button = widget_list[GncDateEdit.GNC_RD_WID_REL_BUTTON_POS]
            rel_date_widget = widget_list[GncDateEdit.GNC_RD_WID_REL_WIDGET_POS]
            if ab_button.get_active():
                #absval = ab_date_widget.get_property('time')
                absval = ab_date_widget.get_date()
                retval = ('absolute', absval)
            elif rel_button.get_active():
                relval = rel_date_widget.get_active()
                relval = self.guile_option.lookup_index(relval)
                retval = ('relative', relval)
        return retval
    def set_ui_widget_account_list (self, page_box,  name, documentation, enclosing=None, packed=None):
        print("set_ui_widget_account_list")

        #pdb.set_trace()

        #print("collect in set_ui_widget_account_list 1")
        #gc.collect()

        enclosing = self.create_account_widget(name)
        value = self.widget

        #print("collect in set_ui_widget_account_list 2")
        #gc.collect()

        enclosing.set_tooltip_text(self.guile_option.documentation_string)

        page_box.pack_start(enclosing, True, True, 5)
        packed = True

        self.set_ui_value(False)

        selection = value.get_selection()
        selection.connect("changed", self.account_cb)

        #print("collect in set_ui_widget_account_list 3")
        #gc.collect()

        enclosing.show_all()

        #print("collect in set_ui_widget_account_list 4")
        #gc.collect()

        # need to figure what goes on with packed - is it pass through??
        return (value, enclosing, packed)
    def set_ui_value_account_list (self, use_default, widget, value):
        print("set_ui_value_account_list")
        #pdb.set_trace()
        gnc_tree_view_account.do_set_selected_accounts(widget,value,True)
        return False
    def get_ui_value_account_list (self, widget):
        print("get_ui_value_account_list")
        #pdb.set_trace()
        acc_lst = gnc_tree_view_account.do_get_selected_accounts(widget)
        return acc_lst
    def set_ui_widget_account_sel (self, page_box,  name, documentation, enclosing=None, packed=None):
        print("set_ui_widget_account_sel")
        pdb.set_trace()
    def set_ui_value_account_sel (self, use_default, widget, value):
        print("set_ui_value_account_sel")
        pdb.set_trace()
    def get_ui_value_account_sel (self, widget):
        print("get_ui_value_account_sel")
        pdb.set_trace()
    def set_ui_widget_list (self, page_box,  name, documentation, enclosing=None, packed=None):
        print("set_ui_widget_list")
        #gc.collect()
        colon_name = name + ":"
        label = Gtk.Label(colon_name)
        label.set_alignment(1.0, 0.5)

        enclosing = self.create_list_widget(name)
        value = self.widget

        eventbox = Gtk.EventBox()
        eventbox.add(enclosing)
        page_box.pack_start(eventbox, False, False, 5)
        packed = True

        eventbox.set_tooltip_text(self.guile_option.documentation_string)

        self.set_ui_value(False)

        enclosing.show_all()

        #print("collect in set_ui_widget_value_list")
        #gc.collect()

        # need to figure what goes on with packed - is it pass through??
        return (value, enclosing, packed)
    def set_ui_value_list (self, use_default, widget, value):
        print("set_ui_value_list")
        #pdb.set_trace()
        selection = widget.get_selection()
        selection.unselect_all()
        # so where did I get this from??
        # cant see it in the c code at all
        # I dont know how this worked - I seem to be getting 
        # values as keys but the tree view requires indexes
        # maybe I never updated this from a long time ago??
        # - because the C code needs the gnc_option_permissible_value_index call
        # to convert from the key to index
        #if use_default:
        #    for itm in self.guile_option.default_value:
        #        rw = self.guile_option.lookup_key(itm)
        #        if rw >= 0 and rw < len(self.guile_option.option_data):
        #            selection.select_path((rw,))
        #        else:
        #            return True
        #else:
        if True:
            for itm in value:
                #rw = self.guile_option.permissible_value_index(itm)
                rw = self.guile_option.lookup_key(itm)
                if rw >= 0 and rw < len(self.guile_option.option_data):
                    path = Gtk.TreePath(rw)
                    selection.select_path((path,))
                else:
                    return True
        return False
    def get_ui_value_list (self, widget):
        print("get_ui_value_list")
        #pdb.set_trace()
        # big question is whether to base from 0 or 1 - now going with 0
        # raw indexes are base 0
        selection = widget.get_selection()
        # this has been changed in Gtk3
        #newslc = selection.get_selected_rows()
        # not sure about this for introspection
        #newlst = newslc[1][0].get_indices_with_depth()
        # this is how its done in Gtk3/gnucash 3
        #num_values = self.guile_option.num_permissible_values()
        num_values = len(self.guile_option.option_data)
        newlst = []
        for row,opt in enumerate(self.guile_option.option_data):
            path = Gtk.TreePath(row)
            selected = selection.path_is_selected(path)
            if selected:
                newlst.append(opt[0])
        # what am I supposed to be returning for this??
        # a list of objects seems to work - it does set
        # the option value to a list of the option keys
        #pdb.set_trace()
        return newlst
    def set_ui_widget_number_range (self, page_box,  name, documentation, enclosing=None, packed=None):
        print("set_ui_widget_number_range")
        #pdb.set_trace()
        colon_name = name + ":"
        label = Gtk.Label(colon_name)
        label.set_alignment(1.0, 0.5)

        #enclosing = Gtk.HBox(homogeneous=False, spacing=5)
        enclosing = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        enclosing.set_homogeneous(False)

        (lower_bound, upper_bound, num_decimals, step_size) = self.get_range_info()

        # note in python the 1st argument is the adjustment value - we can set it later
        # so just use a default here
        # NOTA BENE - skipping this 1st argument leads to strange non-errors
        adj = Gtk.Adjustment(0.0, lower_bound, upper_bound, step_size, step_size*5,0)

        value = Gtk.SpinButton.new(adj,step_size, int(num_decimals))
        value.set_numeric(True)

        biggest = abs(lower_bound)
        biggest = max(lower_bound,abs(upper_bound))
        num_digits = 0
        while biggest >= 1:
            num_digits += 1
            biggest = biggest/10
        if num_digits == 0:
            num_digits = 1
        num_digits += int(num_decimals)

        value.set_width_chars(num_digits)

        self.widget = value
        self.set_ui_value(False)

        value.connect("changed",self.changed_widget_cb)

        enclosing.pack_start(label, False, False, 0)
        enclosing.pack_start(value, False, False, 0)
        enclosing.show_all()

        # need to figure what goes on with packed - is it pass through??
        return (value, enclosing, None)
    def set_ui_value_number_range (self, use_default, widget, value):
        print("set_ui_value_number_range")
        #pdb.set_trace()
        if isinstance(value, numbers.Number):
            widget.set_value(value)
            return False
        else:
            return True
    def get_ui_value_number_range (self, widget):
        print("get_ui_value_number_range")
        newnum = widget.get_value()
        #pdb.set_trace()
        # need to check utf-8'ness here
        return newnum
    def set_ui_widget_color (self, page_box,  name, documentation, enclosing=None, packed=None):
        print("set_ui_widget_color")
        colon_name = name + ":"
        label = Gtk.Label(colon_name)
        label.set_alignment(1.0, 0.5)

        #enclosing = Gtk.HBox(homogeneous=False, spacing=5)
        enclosing = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        enclosing.set_homogeneous(False)

        use_alpha = self.guile_option.option_data[1]

        value = Gtk.ColorButton()
        value.set_title(name)
        value.set_use_alpha(use_alpha)
        self.widget = value
        self.set_ui_value(False)

        # gnc_option_color_changed_cb just calls gnc_option_changed_widget_cb
        value.connect("color-set",self.changed_widget_cb)

        enclosing.pack_start(label, False, False, 0)
        enclosing.pack_start(value, False, False, 0)
        enclosing.show_all()

        # need to figure what goes on with packed - is it pass through??
        return (value, enclosing, None)
    def set_ui_value_color (self, use_default, widget, value):
        print("set_ui_value_color")
        #DEBUG("red %f, green %f, blue %f, alpha %f", red, green, blue, alpha)
        # yes in the C the value argument is totally ignored and get_color_info
        # actually gets the value from the option
        clr = self.get_color_info(use_default)
        if clr:
            gclr = Gdk.Color(red=clr[0],green=clr[1],blue=clr[2])
            widget.set_color(gclr)
            widget.set_alpha(int(clr[3]*0x0ffff))
            return False
        return True
    def get_ui_value_color (self, widget):
        print("get_ui_value_color")
        newclr = widget.get_color()
        newalp = widget.get_alpha()
        scl = self.guile_option.option_data[0]
        newval = [newclr[0],newclr[1],newclr[2],newalp]
        return newclr
    def set_ui_widget_font (self, page_box,  name, documentation, enclosing=None, packed=None):
        print("set_ui_widget_font")
    def set_ui_value_font (self, use_default, widget, value):
        print("set_ui_value_font")
    def get_ui_value_font (self, widget):
        print("get_ui_value_font")
    def set_ui_widget_pixmap (self, page_box,  name, documentation, enclosing=None, packed=None):
        print("set_ui_widget_pixmap")
    def set_ui_value_pixmap (self, use_default, widget, value):
        print("set_ui_value_pixmap")
    def get_ui_value_pixmap (self, widget):
        print("get_ui_value_pixmap")
    def set_ui_widget_radiobutton (self, page_box,  name, documentation, enclosing=None, packed=None):
        print("set_ui_widget_radiobutton")
    def set_ui_value_radiobutton (self, use_default, widget, value):
        print("set_ui_value_radiobutton")
    def get_ui_value_radiobutton (self, widget):
        print("get_ui_value_radiobutton")
    def set_ui_widget_dateformat (self, page_box,  name, documentation, enclosing=None, packed=None):
        print("set_ui_widget_dateformat")
    def set_ui_value_dateformat (self, use_default, widget, value):
        print("set_ui_value_dateformat")
    def get_ui_value_dateformat (self, widget):
        print("get_ui_value_dateformat")
    def set_ui_widget_budget (self, page_box,  name, documentation, enclosing=None, packed=None):
        print("set_ui_widget_budget")
    def set_ui_value_budget (self, use_default, widget, value):
        print("set_ui_value_budget")
    def get_ui_value_budget (self, widget):
        print("get_ui_value_budget")


    def create_date_widget (self):

        #pdb.set_trace()

        date_type = self.guile_option.option_data[0]
        show_time = self.guile_option.option_data[1]
        use24 = sw_core_utils.gnc_prefs_get_bool('general', 'clock-24h')

        if date_type != 'relative':
            ab_widget = GncDateEdit.new(time.time(), show_time, use24)
            ab_widget.date_entry.connect("changed", self.changed_option_cb)
            if show_time:
                ab_widget.time_entry.connect("changed", self.changed_option_cb)

        if date_type != 'absolute':

            #num_values = self.guile_option.num_permissible_values()
            num_values = len(self.guile_option.option_data[2])

            store = Gtk.ListStore(GObject.TYPE_STRING,GObject.TYPE_STRING)

            def_val = self.guile_option.default_value

            for indx,itm in enumerate(self.guile_option.option_data[2]):
                itemlst = self.guile_option.lookup_string(itm)
                itemstr = itemlst[0]
                itemdes = itemlst[1]
                store.append((itemstr,itemdes))

            rel_widget = self.gnc_combott(store)
            # not seeing where this is done in scheme/C
            # note this is making the default value the index
            #rel_widget.set_active(self.guile_option.default_value)
            #rel_widget.set_model(store)
            rel_widget.connect("changed",self.multichoice_cb)

        if date_type == 'absolute':
            self.widget = ab_widget
            return ab_widget
        elif date_type == 'relative':
            self.widget = rel_widget
            return rel_widget
        elif date_type == 'both':
            #box = Gtk.HBox(homogeneous=False, spacing=5)
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            box.set_homogeneous(False)
            ab_button = Gtk.RadioButton(group=None)
            ab_button.connect("toggled", self.rd_option_ab_set_cb)
            rel_button = Gtk.RadioButton(group=ab_button)
            rel_button.connect("toggled", self.rd_option_rel_set_cb)
            box.pack_start(ab_button, False,False,0)
            box.pack_start(ab_widget, False,False,0)
            box.pack_start(rel_button, False,False,0)
            box.pack_start(rel_widget, False,False,0)
            self.widget = box
            return box
        else:
            return None


    def changed_option_cb (self, widget):
        self.changed_widget_cb(widget)

    def rd_option_ab_set_cb (self, widget):
        self.set_select_method(True,False)
        self.changed_option_cb(widget)


    def rd_option_rel_set_cb (self, widget):
        self.set_select_method(False,False)
        self.changed_option_cb(widget)

    def set_select_method (self, use_absolute, set_buttons):
        print("set_select_method")
        widget_list = self.widget.get_children()
        ab_button = widget_list[GncDateEdit.GNC_RD_WID_AB_BUTTON_POS]
        ab_widget = widget_list[GncDateEdit.GNC_RD_WID_AB_WIDGET_POS]
        rel_button = widget_list[GncDateEdit.GNC_RD_WID_REL_BUTTON_POS]
        rel_widget = widget_list[GncDateEdit.GNC_RD_WID_REL_WIDGET_POS]

        if use_absolute:
            ab_widget.set_sensitive(True)
            rel_widget.set_sensitive(False)
            if set_buttons:
                ab_button.set_active(True)
        else:
            ab_widget.set_sensitive(False)
            rel_widget.set_sensitive(True)
            if set_buttons:
                rel_button.set_active(True)


    def create_account_widget (self, name):

        #pdb.set_trace()

        #print("collect in create_account_widget 1")
        #gc.collect()

        # is multiple account selection allowed
        multiple_selection = self.guile_option.option_data[0]
        acct_type_list = self.guile_option.option_data[1]

        frame = Gtk.Frame(label=name)

        #vbox = Gtk.VBox(homogeneous=False, spacing=0)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.set_homogeneous(False)
        frame.add(vbox)

        tree = gnc_tree_view_account.new(False)
        tree.do_set_headers_visible(False)
        selection = tree.do_get_selection()
        if multiple_selection:
            selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        else:
            selection.set_mode(Gtk.SelectionMode.BROWSE)

        #print("collect in create_account_widget 2")
        #gc.collect()

        if len(acct_type_list) > 0:
            avi = tree.do_get_view_info()
            for i in range(NUM_ACCOUNT_TYPES):
                avi.include_type[i] = False
            avi.show_hidden = False

            for node in acct_type_list:
                gacctyp = node.data
                avi.include_type[gacctyp] = True

            tree.do_set_view_info(avi)
        else:
            avi = tree.do_get_view_info()
            for i in range(NUM_ACCOUNT_TYPES):
                avi.include_type[i] = True
            avi.show_hidden = False
            tree.do_set_view_info(avi)

        #print("collect in create_account_widget 3")
        #gc.collect()

        scroll_win = Gtk.ScrolledWindow()
        scroll_win.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)

        vbox.pack_start(scroll_win,True,True,0)
        scroll_win.set_border_width(5)
        scroll_win.add(tree)

        bbox = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        bbox.set_layout(Gtk.ButtonBoxStyle.SPREAD)
        vbox.pack_start(bbox, False,False,10)

        #print("collect in create_account_widget 4")
        #gc.collect()

        if multiple_selection:
            button = Gtk.Button(label=N_("Select All"))
            bbox.pack_start(button,False,False,0)
            button.set_tooltip_text(N_("Select all accounts."))

            button.connect("clicked", self.account_select_all_cb)

            button = Gtk.Button(label=N_("Clear All"))
            bbox.pack_start(button,False,False,0)
            button.set_tooltip_text(N_("Clear the selection and unselect all accounts."))

            button.connect("clicked", self.account_clear_all_cb)

            button = Gtk.Button(label=N_("Select Children"))
            bbox.pack_start(button,False,False,0)
            button.set_tooltip_text(N_("Select all descendents of selected account."))

            button.connect("clicked", self.account_select_children_cb)

        #print("collect in create_account_widget 5")
        #gc.collect()

        button = Gtk.Button(label=N_("Select Default"))
        bbox.pack_start(button,False,False,0)
        button.set_tooltip_text(N_("Select the default account selection."))

        button.connect("clicked", self.default_cb)

        if multiple_selection:
            bbox = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
            bbox.set_layout(Gtk.ButtonBoxStyle.START)
            vbox.pack_start(bbox,False,False,0)

        button = Gtk.CheckButton(label=N_("Show Hidden Accounts"))
        bbox.pack_start(button,False,False,0)
        button.set_tooltip_text(N_("Show accounts that have been marked hidden."))
        button.set_active(False)
        button.connect("toggled", self.show_hidden_toggled_cb)

        #print("collect in create_account_widget 6")
        #gc.collect()

        self.widget = tree

        return frame

    def create_list_widget (self, name):

        frame = Gtk.Frame(label=name)
        #hbox = Gtk.HBox(homogeneous=False, spacing=0)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        hbox.set_homogeneous(False)
        frame.add(hbox)

        store = Gtk.ListStore(GObject.TYPE_STRING)
        view = Gtk.TreeView(model=store)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("",renderer,text=0)
        view.append_column(column)
        view.set_headers_visible(False)

        #num_values = self.guile_option.num_permissible_values()
        num_values = len(self.guile_option.option_data)

        for indx,opt in enumerate(self.guile_option.option_data):
            #label = self.guile_option.permissible_value_name(indx)
            #label = opt.name
            #tip = opt.description
            label = opt[0]
            tip = opt[1]
            store.append((label,))

        hbox.pack_start(view,False,False,0)

        selection = view.get_selection()
        selection.set_mode(Gtk.SelectionMode.MULTIPLE)

        selection.connect("changed",self.list_changed_cb)

        # this seems to have been removed at gnucash 3/gtk 3
        # so how is default value selected??
        #for rw in self.guile_option.default_value:
        #    selection.select_path((rw,))
        # looks like we cant just use strings any more - we need to
        # do the following where row is row index
        #path = Gtk.TreePath(row)
        #selected = selection.select_path(path)

        bbox = Gtk.ButtonBox(orientation=Gtk.Orientation.VERTICAL)
        bbox.set_layout(Gtk.ButtonBoxStyle.SPREAD)
        hbox.pack_start(bbox,False,False,10)

        button = Gtk.Button(label=N_("Select All"))
        bbox.pack_start(button,False,False,0)
        button.set_tooltip_text(N_("Select all entries."))

        button.connect("clicked", self.list_select_all_cb)

        button = Gtk.Button(label=N_("Clear All"))
        bbox.pack_start(button,False,False,0)
        button.set_tooltip_text(N_("Clear the selection and unselect all entries."))

        button.connect("clicked", self.list_clear_all_cb)

        button = Gtk.Button(label=N_("Select Default"))
        bbox.pack_start(button,False,False,0)
        button.set_tooltip_text(N_("Select the default selection."))

        button.connect("clicked", self.default_cb)

        self.widget = view

        return frame


    def account_select_all_cb (self, selection):
        print("select_all_cb")
        #pdb.set_trace()
        view = self.widget
        selection = view.get_selection()
        selection.select_all()
        self.changed_widget_cb(view)

    def account_clear_all_cb (self, selection):
        print("clear_all_cb")
        #pdb.set_trace()
        view = self.widget
        selection = view.get_selection()
        selection.unselect_all()
        self.changed_widget_cb(view)

    def account_select_children_cb (self, selection):
        print("account_select_children_cb")
        #pdb.set_trace()
        view = self.widget
        account = view.do_get_cursor_account()
        if account == None:
            return
        view.do_select_subaccounts(account)


    def show_hidden_toggled_cb (self, widget):
        pdb.set_trace()
        view = self.widget
        avi = view.get_view_info()
        avi.show_hidden = widget.get_active()
        view.set_view_info(avi)
        self.changed_widget_cb(view)



    def account_cb (self, selection):
        #pdb.set_trace()
        print("account_cb")
        print(self)
        print(selection)
        view = selection.get_tree_view()
        self.changed_widget_cb(view)



    def list_changed_cb (self, selection):
        #pdb.set_trace()
        view = selection.get_tree_view()
        self.changed_widget_cb(view)

    def list_select_all_cb (self, selection):
        #pdb.set_trace()
        view = self.widget
        selection = view.get_selection()
        selection.select_all()
        self.changed_widget_cb(view)

    def list_clear_all_cb (self, selection):
        #pdb.set_trace()
        view = self.widget
        selection = view.get_selection()
        selection.unselect_all()
        self.changed_widget_cb(view)

    def default_cb (self, widget):
        #pdb.set_trace()
        self.set_ui_value(True)
        self.changed = True
        self.changed_internal(widget,True)


    def create_multichoice_widget (self):

        num_values = len(self.guile_option.option_data)

        store = Gtk.ListStore(GObject.TYPE_STRING,GObject.TYPE_STRING)
        for indx,opt in enumerate(self.guile_option.option_data):
            #label = opt.name
            #tip = opt.description
            label = opt[0]
            tip = opt[1]
            store.append((label,tip))

        widget = self.gnc_combott(store)
        # not seeing where this is done in scheme/C
        # note this is making the default value the index
        widget.set_active(self.guile_option.option_data_dict[self.guile_option.default_value])
        #widget.set_model(store)
        widget.connect("changed",self.multichoice_cb)

        return widget

    def gnc_combott (self, model):
        # thats a load of implementing - just go with plain combo box for the moment
        # OK - it is important that the model is added BEFORE the add_attribute
        combobox = Gtk.ComboBox.new_with_model(model)
        cell = Gtk.CellRendererText()
        combobox.pack_start(cell, True)
        combobox.add_attribute(cell, 'text', 0)
        return combobox


    def create_radiobutton_widget (self):
        num_values = len(self.guile_option.option_data)

        frame = Gtk.Frame()
        #box = Gtk.HBox(homogeneous=False, spacing=5)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        box.set_homogeneous(False)
        frame.add(box)

        widget = None
        for indx,opt in enumerate(self.guile_option.option_data):
            label = opt.name
            tip = opt.description

            widget = Gtk.RadioButton(group=widget,label=N_(label))
            #widget.set_data("gnc_radiobutton_index",indx)
            widget.gnc_radiobutton_index = indx
            widget.set_tooltip_text(N_(tip))
            widget.connect("toggled",self.radiobutton_cb)
            box.pack_start(False,False,0)

        return frame

# for some reason this function is called in the gncmod module initialization function for gnome-utils
# gnc_options_ui_initialize
# the following implements gnc_options_ui_initialize at python module level

# not sure where to define this yet
# either as global for this module or as class variable in GncOption??
# the following is confusing as option_name actually really should be option_type_name
optionTable = {}

class GncOptionDef(object):
    def __init__ (self, option_name, set_widget, set_value, get_value):
        self.option_name = option_name
        self.set_widget = set_widget
        self.set_value = set_value
        self.get_value = get_value

options = [ \
          GncOptionDef("boolean", GncOption.set_ui_widget_boolean,
            GncOption.set_ui_value_boolean, GncOption.get_ui_value_boolean),
          GncOptionDef("string", GncOption.set_ui_widget_string,
            GncOption.set_ui_value_string, GncOption.get_ui_value_string),
          GncOptionDef("text", GncOption.set_ui_widget_text,
            GncOption.set_ui_value_text, GncOption.get_ui_value_text),
          GncOptionDef("currency", GncOption.set_ui_widget_currency,
            GncOption.set_ui_value_currency, GncOption.get_ui_value_currency),
          GncOptionDef("commodity", GncOption.set_ui_widget_commodity,
            GncOption.set_ui_value_commodity, GncOption.get_ui_value_commodity),
          GncOptionDef("multichoice", GncOption.set_ui_widget_multichoice,
            GncOption.set_ui_value_multichoice, GncOption.get_ui_value_multichoice),
          GncOptionDef("date", GncOption.set_ui_widget_date,
            GncOption.set_ui_value_date, GncOption.get_ui_value_date),
          GncOptionDef("account-list", GncOption.set_ui_widget_account_list,
            GncOption.set_ui_value_account_list, GncOption.get_ui_value_account_list),
          GncOptionDef("account-sel", GncOption.set_ui_widget_account_sel,
            GncOption.set_ui_value_account_sel, GncOption.get_ui_value_account_sel),
          GncOptionDef("list", GncOption.set_ui_widget_list,
            GncOption.set_ui_value_list, GncOption.get_ui_value_list),
          GncOptionDef("number-range", GncOption.set_ui_widget_number_range,
            GncOption.set_ui_value_number_range, GncOption.get_ui_value_number_range),
          GncOptionDef("color", GncOption.set_ui_widget_color,
            GncOption.set_ui_value_color, GncOption.get_ui_value_color),
          GncOptionDef("font", GncOption.set_ui_widget_font,
            GncOption.set_ui_value_font, GncOption.get_ui_value_font),
          GncOptionDef("pixmap", GncOption.set_ui_widget_pixmap,
            GncOption.set_ui_value_pixmap, GncOption.get_ui_value_pixmap),
          GncOptionDef("radiobutton", GncOption.set_ui_widget_radiobutton,
            GncOption.set_ui_value_radiobutton, GncOption.get_ui_value_radiobutton),
          GncOptionDef("dateformat", GncOption.set_ui_widget_dateformat,
            GncOption.set_ui_value_dateformat, GncOption.get_ui_value_dateformat),
          GncOptionDef("budget", GncOption.set_ui_widget_budget,
            GncOption.set_ui_value_budget, GncOption.get_ui_value_budget),
          ]

for optobj in options:
    optionTable[optobj.option_name] = optobj


last_db_handle = 0
option_dbs = {}


class GncSection(object):

    def __init__ (self, section_name):
        self.section_name = section_name
        self.options = []

class GncOptionDB(object):

    # this class is instantiated many times in C/Scheme
    # - each time the option icon is clicked for a report
    # and each time the report is displayed (if options updated)

    def __init__ (self, guile_options):
        global option_dbs
        global last_db_handle
        # copy of guile options
        self.guile_options = guile_options
        self.option_sections = []
        self.option_sections_names = []
        self.option_sections_dict = {}
        self.options_dirty = False
        self.handle = None
        # we have to rename these in python
        #self.get_ui_value = None
        #self.set_ui_value = None
        #self.set_selectable = None
        self.get_ui_value_cb = None
        self.set_ui_value_cb = None
        self.set_selectable_cb = None

        #
        while True:
            self.handle = last_db_handle
            if not self.handle in option_dbs:
                break
            last_db_handle += 1

        option_dbs[self.handle] = self

        # this is in gnc_option_db_init
        self.send_options()

    def send_options (self):
        # this should copy options from guile_options into the GncOptionDB
        for option in self.guile_options.options_for_each():
            #print("option send",type(option),option)
            self.register_option_db(option)

        # in python changing so we now sort after inserting
        # option_sections is simply a list of names which we lookup in the dict
        self.option_sections_names = sorted(self.option_sections_dict.keys())
        self.option_sections = [ self.option_sections_dict[x] for x in self.option_sections_names ]
        for section in self.option_sections:
            secopts = section.options
            secopts.sort(key=attrgetter('guile_option.sort_tag'))
        #pdb.set_trace()
        #for sect_name in self.option_sections_dict:
        #    print("sect",sect_name)
        #    for optn in self.option_sections_dict[sect_name].options:
        #        print(optn.guile_option.section,optn.guile_option.name)

    def register_option_db (self, guile_option):
        odb = option_dbs[self.handle]
        odb.options_dirty = True
        option = GncOption(guile_option,False,None,odb)
        section_name = guile_option.section
        # hmm there is a list of sections (sorted) which is searched for the section name
        # doing it the C/scheme way is complicated - it stores the section structure
        # and searches by name
        # going to have a name list and sections list
        # probably should use a sorted dict
        # of course this fails if called outside send_options
        if section_name not in self.option_sections_dict:
            self.option_sections_dict[section_name] = GncSection(section_name)
        self.option_sections_dict[section_name].options.append(option)


    def register_change_callback (self, callback, section=None, name=None):
        print("register_change_callback")
        return self.guile_options.register_callback(section, name, callback)

    def unregister_change_callback (self, callback_id):
        print("unregister_change_callback")
        self.guile_options.unregister_callback(callback_id)


    def set_ui_callbacks (self, get_ui_value, set_ui_value, set_selectable):
        self.get_ui_value_cb = get_ui_value
        self.set_ui_value_cb = set_ui_value
        self.set_selectable_cb = set_selectable

    def get_ui_value (self, lcl_option):
        # this is really contorted - we need to pass the GncOption object
        # and the function has to be defined in the GncOption class in any case
        # if its the internal object
        func_attr = getattr(lcl_option,self.get_ui_value_cb)
        return func_attr()

    def set_ui_value (self, lcl_option):
        # this is really contorted - we need to pass the GncOption object
        # and the function has to be defined in the GncOption class in any case
        # if its the internal object
        func_attr = getattr(lcl_option,self.set_ui_value_cb)
        return func_attr()

    def set_selectable (self, lcl_option):
        # this is really contorted - we need to pass the GncOption object
        # and the function has to be defined in the GncOption class in any case
        # if its the internal object
        func_attr = getattr(lcl_option,self.set_selectable_cb)
        return func_attr()

    def num_sections (self):
        return len(self.option_sections)

    def get_default_section (self):
        # this is got from scheme
        # gnc:options-get-default-section
        # self.guile_options.get_default_section()
        # blast in a junk name
        # ah - the default section is defined by each specific report scheme definition
        return "Default Section"

    def clean (self):
        self.options_dirty = False

    def commit (self):
        changed_something = False
        for section in self.option_sections:
            for option in section.options:
                if option.changed:
                    option.commit()
                    changed_something = True
                    option.changed = False
        if changed_something:
            self.change_callbacks()

    def change_callbacks (self):
        #proc = gnc:options-run-callbacks
        #if proc == None:
        #    PERR("not a procedure")
        #    return
        #proc(self.guile_options)
        self.guile_options.run_callbacks()

    def destroy (self):
        # in python just make sure we remove holding values
        for section in self.option_sections:
            section.options = None
        self.option_sections = None

    def lookup_string_option (self, section, name, default_value=None):

        option = self.get_option_by_name(section,name)

        if option != None:
            value = option.guile_option.getter()
            if value != None:
                return value

        if default_value == None:
            return None

        return default_value

    def get_option_by_name (self, section, name):

        if section in self.option_sections_dict:
            section_dict = self.option_sections_dict[section]
        else:
            return None

        for opt in section_dict.options:
            if opt.guile_option.name == name:
                return opt

        return None



PAGE_INDEX = 0
PAGE_NAME = 1

MAX_TAB_COUNT = 4

class DialogOption(object):

    # note this class wraps the GncOptionWin struct of C gnucash

    # NOTA BENE - switched order so can default modal
    # this combines gnc_options_dialog_new and gnc_options_dialog_new_modal
    def __init__ (self, title=None, modal=False):

        # these are defined in gnc_option_win

        # these are all Gtk.Widget type
        self.dialog = None
        self.notebook = None
        self.page_list_view = None
        self.page_list = None

        self.toplevel = False

        # these are callbacks
        # in python these are directly set to functions
        # the data attribute is not used in python
        self.apply_cb = None
        #self.apply_cb_data = None

        self.help_cb = None
        #self.help_cb_data = None

        self.close_cb = None
        #self.close_cb_data = None

        # this is the GncOptionDB type
        self.option_db = None

    def response_cb (self, dialog, response):
        print("response_cb called")
        # traceback showing how this response callback ends up running
        # the report
        #0  0x00000001001a5bd4 in gnc_run_report ()
        #1  0x00000001001a5cf3 in gnc_run_report_id_string ()
        #2  0x00000001000408a3 in gnc_html_report_stream_cb ()
        #3  0x00000001001c853e in load_to_stream ()
        #4  0x00000001001c8d97 in impl_webkit_show_url ()
        #5  0x00000001001c5fb1 in gnc_html_show_url ()
        #6  0x0000000103e08c76 in _wrap_gncp_option_invoke_callback ()
        #7  0x0000000104192c26 in deval ()
        #8  0x000000010419afd1 in scm_dapply ()
        #9  0x0000000108678d5a in scm_srfi1_for_each ()
        #10 0x000000010419398d in deval ()
        #11 0x0000000104192860 in deval ()
        #12 0x000000010419afd1 in scm_dapply ()
        #13 0x0000000100041520 in gnc_options_dialog_apply_cb ()
        #14 0x00000001001e83d8 in gnc_options_dialog_response_cb ()
        if response == Gtk.ResponseType.HELP:
            self.help_cb()
        else:
            if response == Gtk.ResponseType.OK or response == Gtk.ResponseType.APPLY:
                self.changed_internal(self.dialog, False)
                close_cb = self.close_cb
                self.close_cb = None
                if self.apply_cb != None:
                    try:
                        self.apply_cb()
                    except Exception as errexc:
                        traceback.print_exc()
                        pdb.set_trace()
                self.close_cb = close_cb
            if response != Gtk.ResponseType.APPLY:
                if self.close_cb != None:
                    self.close_cb()
                else:
                    self.dialog.hide()

    def dialog_new (self, title, parent, modal=False):

        self.dialog_new_modal(title, parent, component_class=None, modal=False)

    def dialog_new_modal (self, title, parent, component_class=None, modal=False):

        # break init up similar to gnucash

        # this is a dict of signal names and functions to call
        # this could be a class object in which the single names become function names
        # unfortunately we have to use the full gnucash name
        self.builder_handlers = { \
                                # 'onDeleteWindow' : Gtk.main_guit,
                                'gnc_options_dialog_response_cb' : self.response_cb,
                                }

        # we use a proper subclass of GtkBuilder to extend it with add_from_file
        # (actual gnucash extension function is gnc_builder_add_from_file)
        self.builder = GncBuilder()
        self.builder.add_from_file("dialog-options.glade", "gnucash_options_dialog")

        self.dialog = self.builder.get_object("gnucash_options_dialog")
        self.page_list = self.builder.get_object("page_list_scroll")

        # so looks as though the python bindings do this differently
        # - there is no set_style_context
        # this may be the replacement - well it seems to work
        # and dialog still looks the same
        self.dialog.get_path().iter_set_object_name(0,"GncOptionsDialog")
        #self.dialog.set_style_context("GncOptionsDialog")
        self.dialog.set_transient_for(parent)

        self.page_list_view = self.builder.get_object("page_list_treeview")

        store = Gtk.ListStore(GObject.TYPE_INT, GObject.TYPE_STRING)
        self.page_list_view.set_model(store)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(N_("Page"), renderer, text=1)
        self.page_list_view.append_column(column)
        column.set_alignment(0.5)

        selection = self.page_list_view.get_selection()
        selection.set_mode(Gtk.SelectionMode.BROWSE)

        selection.connect("changed", self.list_select_cb)


        #gtk_builder_connect_signals_full (builder, gnc_builder_connect_full_func, retval);
        self.builder.connect_signals(self.builder_handlers)

        if title:
            self.dialog.set_title(title)

        if modal:
            apply_button = self.builder.get_object("applybutton")
            apply_button.hide()

        hbox = self.builder.get_object("notebook_placeholder")
        self.notebook = Gtk.Notebook()
        self.notebook.show()
        hbox.pack_start(self.notebook, True, True, 5)

        component_close_callback_type = ctypes.CFUNCTYPE(None,ctypes.c_void_p)

        component_id = sw_app_utils.libgnc_apputils.gnc_register_gui_component(b"dialog-options", None, component_close_callback_type(self.component_close_handler), hash(self))

        #component_refresh_callback_type = ctypes.CFUNCTYPE(None,ctypes.c_void_p,ctypes.c_void_p)
        #component_id = sw_app_utils.libgnc_apputils.gnc_register_gui_component(b"dialog-options", component_refresh_callback_type(self.component_refresh_handler), component_close_callback_type(self.component_close_handler), hash(self))

        #session = sw_app_utils.gnc_get_current_session()
        session = sw_app_utils.libgnc_apputils.gnc_get_current_session()

        #sw_app_utils.gnc_gui_component_set_session(component_id, session)
        sw_app_utils.libgnc_apputils.gnc_gui_component_set_session(component_id, session)


    def component_close_handler (self, arg):
        Gtk.Dialog.response(arg.dialog, Gtk.REPONSE_CANCEL)

    # there is now a refresh handler for a specific situation
    # - ignoring for now
    # and as of 3.2 the code is commented so this is a dummy function in any case
    def component_refresh_handler (self, changes, user_data):
        pass

    def dialog_destroy (self):

        sw_app_utils.libgnc_apputils.gnc_unregister_gui_component_by_data(b"dialog-options", hash(self))

        self.dialog.destroy()

        self.dialog = None
        self.notebook = None
        self.apply_cb = None
        self.help_cb = None


    # these are the primary creation methods
    # - trying to solve the way the C code splits the new functions

    @classmethod
    def OptionsDialog_New(cls, title, parent, modal=False):
        newobj = cls(title,modal)
        newobj.dialog_new(title,parent,modal)
        return newobj

    @classmethod
    def OptionsDialog_NewWithDialog(cls, title, dialog):
        newobj = cls(title)
        newobj.dialog = dialog
        return newobj

    def list_select_cb (self, *args):
        pass

    # again this setting of callbacks doesnt quite work in python
    # - we can only set callbacks to existing functions in this class
    # in fact we completely ignore this in python
    # - we just directly set the original attribute

    #def set_apply_cb (self, cb, data):
    #    self.apply_cb = cb
    #    self.apply_cb_data = data

    #def set_help_cb (self, cb, data):
    #    self.help_cb = cb
    #    self.help_cb_data = data

    #def set_help_cb (self, cb, data):
    #    self.close_cb = cb
    #    self.close_cb_data = data


    def reset_cb (self, *args):
        print("reset cb", args)
        # args are clicked widget then dialog_option


    def add_option (self, option_box, option):
        option.set_ui_widget(option_box)

    # not sure we really need this - just access dialog attribute
    def widget (self):
        return self.dialog

    def changed_internal (self, widget, sensitive):

        #pdb.set_trace()
        print("DialogOption changed_internal",str(widget),type(widget))

        #oldwidget = widget.get_ancestor(Gtk.Dialog)
        print("changed_internal 1a",str(widget),isinstance(widget, Gtk.Dialog))
        while widget and not isinstance(widget, Gtk.Dialog):
            print("changed_internal 1a",str(widget),isinstance(widget, Gtk.Dialog))
            widget = widget.parent
        print("changed_internal 1",str(widget))
        if widget == None:
            return

        print("changed_internal 2",str(widget))
        widget.set_response_sensitive(Gtk.ResponseType.OK, sensitive)
        widget.set_response_sensitive(Gtk.ResponseType.APPLY, sensitive)


    def append_page (self, section):

        name = section.section_name
        if name == None or name == "":
            return None

        if name[0:2] == '__':
            return None

        advanced = name[0:2] == '_+'
        name_offset = 2 if advanced else 0

        page_label = Gtk.Label(N_(name[name_offset:]))
        #PINFO("Page_label is %s", _(name + name_offset));
        page_label.show()

        #page_content_box = Gtk.VBox(homogeneous=False, spacing=2)
        page_content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        page_content_box.set_homogeneous(False)

        page_content_box.set_border_width(12)

        #options_box = Gtk.VBox(homogeneous=False, spacing=5)
        options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        options_box.set_homogeneous(False)
        options_box.set_border_width(0)
        page_content_box.pack_start(options_box, True, True, 0)

        for option in section.options:
            self.add_option(options_box, option)

        buttonbox = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        buttonbox.set_layout(Gtk.ButtonBoxStyle.EDGE)
        buttonbox.set_border_width(5)
        page_content_box.pack_end(buttonbox, False, False, 0)

        reset_button = Gtk.Button(label=N_("Reset defaults"))
        reset_button.set_tooltip_text(N_("Reset all values to their defaults."))

        reset_button.connect("clicked",self.reset_cb, self)
        # ah - I think is what the error message meant!
        # we create a python attribute and set the data!!
        #reset_button.set_data("section", section)
        reset_button.section = section
        buttonbox.pack_end(reset_button, False, False, 0)
        page_content_box.show_all()
        self.notebook.append_page(page_content_box, page_label)

        page_count = self.notebook.page_num(page_content_box)

        if self.page_list_view:

            view = self.page_list_view
            list = view.get_model()

            #PINFO("Page name is %s and page_count is %d", name, page_count);
            list.append((page_count, N_(name)))

            if page_count > MAX_TAB_COUNT:
               self.page_list.show()
               self.notebook.set_show_tabs(False)
               self.notebook.set_show_border(False)
            else:
               self.page_list.hide()

            if advanced:

               notebook_page = self.notebook.get_nth_page(page_count)

               #self.notebook_page.set_data("listitem", None)
               #self.notebook_page.set_data("advanced", advanced)
               self.notebook_page.listitem = None
               self.notebook_page.advanced = advanced

        return page_count


    def build_contents (self, odb):
        self.build_contents_full(odb, True)

    def build_contents_full (self, odb, show_dialog=True):

        # this doesnt work the same in python
        # get_ui_value_internal is a method of GncOption class
        #pdb.set_trace()
        #odb.set_ui_callbacks(self.get_ui_value_internal, self.set_ui_value_internal, self.set_selctable_internal)

        self.option_db = odb

        num_sections = self.option_db.num_sections()

        default_section_name = self.option_db.get_default_section()

        #PINFO("Default Section name is %s", default_section_name);

        default_page = None

        for section in self.option_db.option_sections:

            page = self.append_page(section)

            section_name = section.section_name

            if section_name == default_section_name:
                default_page = page

        for section in self.option_db.option_sections:
            for option in section.options:
                if hasattr(option,"widget_changed_proc"):
                    option.widget_changed_proc(section)

        self.notebook.popup_enable()

        if default_page:

            selection = self.page_list_view.get_selection()

            model = self.page_list_view.get_model()

            model_iter = model.iter_nth_child(None, default_page)

            selection.select_iter(model_iter)

            self.notebook.set_current_page(default_page)

        self.changed_internal(self.dialog,False)

        if show_dialog:
            self.dialog.show()
