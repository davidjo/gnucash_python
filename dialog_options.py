
# this is a recoding of the options dialog (defined in dialog-options.c)
# in python

import os

import sys

import bisect

from operator import attrgetter

import gobject

import gtk



import _sw_app_utils
import gnc_plugin_page
import ctypes


import traceback

import pdb


from gnucash_log import PERR

log_module = "gnc.gui.python"


# junky internationalization function
def N_(msg):
    return msg

# option dialog calls

#12 0x000000010003f262 in gnc_plugin_page_report_options_cb ()
#1  0x000000010004135a in gnc_report_window_default_params_editor ()
#0  0x00000001001e9354 in gnc_options_dialog_build_contents ()


class GNCOption(object):

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
        # we call a function in the GNCOptionDB class
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
        type = self.guile_option.type
        if use_default:
            value = self.guile_option.default_getter()
        else:
            value = self.guile_option.getter()
        option_def = self.ui_get_option(type)
        if option_def:
            bad_value = option_def.set_value(self,use_default,widget,value)
            if bad_value:
                PERR(log_module,"bad value")
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

        #pdb.set_trace()

        #oldwidget = widget.get_ancestor(gtk.Dialog)
        while widget and not isinstance(widget, gtk.Dialog):
            widget = widget.parent
        if widget == None:
            return

        widget.set_response_sensitive(gtk.RESPONSE_OK, sensitive)
        widget.set_response_sensitive(gtk.RESPONSE_APPLY, sensitive)


    def call_widget_changed_proc (self):
        if hasattr(self,"widget_changed_proc"):
            value = self.get_ui_value()
            if value != None:
                self.widget_changed_proc(value)

    def changed_widget_cb (self, entry):
        print "changed_widget_cb"
        self.changed = True
        #self.call_widget_changed_proc()
        # ah - the widget is the dialog box the option is in
        self.changed_internal(entry,True)

    def multichoice_cb (self, entry):
        print "multichoice_cb"
        # this just maps GtkColorButton to widget and calls changed_widget_cb
        self.changed_widget_cb(entry)


    def commit (self):
        print "commit called"
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
                dialog = gtk.MessageDialog(None,gtk.DIALOG_DESTROY_WITH_PARENT,
                        gtk.MESSAGE_ERROR,gtk.BUTTONS_OK,N_("There is a problem with option %s:%s.\n%s")%(section,name,oops))
                dialog.run()
                dialog.destroy()
            else:
                print "There is a problem with option %s:%s.\n%s"%(section,name,oops)


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
            except Exception, errexc:
                traceback.print_exc()
                pdb.set_trace()
        else:
            PERR(log_module,"Unknown option type. Ignoring option \"%s\"."%name)
            pdb.set_trace()

        if not packed and enclosing != None:

            eventbox = gtk.EventBox()

            eventbox.add(enclosing)
            page_box.pack_start(eventbox, expand=False, fill=False, padding=0)

            eventbox.set_tooltip_text(documentation)

        if value != None:
            value.set_tooltip_text(documentation)


    # load of set callback functions
    def set_ui_widget_boolean (self, page_box):
        pass
    def set_ui_value_boolean (self, use_default, widget, value):
        pass
    def get_ui_value_boolean (self, widget):
        pass

    def set_ui_widget_string (self, page_box, name, documentation):

        colon_name = name + ":"
        label = gtk.Label(colon_name)
        label.set_alignment(1.0, 0.5)

        enclosing = gtk.HBox(homogeneous=False, spacing=0)

        value = gtk.Entry()

        self.widget = value
        self.set_ui_value(False)

        value.connect("changed",self.changed_widget_cb)

        enclosing.pack_start(label, expand=False, fill=False, padding=0)
        enclosing.pack_start(value, expand=False, fill=False, padding=0)
        enclosing.show_all()

        # need to figure what goes on with padding - is it pass through??
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
        pass
    def set_ui_value_text (self, use_default, widget, value):
        pass
    def get_ui_value_text (self, widget):
        pass
    def set_ui_widget_currency (self, page_box,  name, documentation, enclosing=None, packed=None):
        pass
    def set_ui_value_currency (self, use_default, widget, value):
        pass
    def get_ui_value_currency (self, widget):
        pass
    def set_ui_widget_commodity (self, page_box,  name, documentation, enclosing=None, packed=None):
        pass
    def set_ui_value_commodity (self, use_default, widget, value):
        pass
    def get_ui_value_commodity (self, widget):
        pass
    def set_ui_widget_multichoice (self, page_box,  name, documentation, enclosing=None, packed=None):
        colon_name = name + ":"
        label = gtk.Label(colon_name)
        label.set_alignment(1.0, 0.5)

        enclosing = gtk.HBox(homogeneous=False, spacing=5)

        value = self.create_multichoice_widget()

        self.widget = value
        self.set_ui_value(False)

        enclosing.pack_start(label, expand=False, fill=False, padding=0)
        enclosing.pack_start(value, expand=False, fill=False, padding=0)
        enclosing.show_all()

        # need to figure what goes on with padding - is it pass through??
        return (value, enclosing, None)
    def set_ui_value_multichoice (self, use_default, widget, value):
        value = value - 1
        if value > 0 and value < len(self.guile_option.ok_values):
            widget.set_active(value)
            return False
        else:
            return True
    def get_ui_value_multichoice (self, widget):
        # big question is whether to base from 0 or 1
        # raw indexes are base 0
        newmulti = widget.get_active() + 1
        # need to check utf-8'ness here
        return newmulti
    def set_ui_widget_date (self, page_box,  name, documentation, enclosing=None, packed=None):
        pass
    def set_ui_value_date (self, use_default, widget, value):
        pass
    def get_ui_value_date (self, widget):
        pass
    def set_ui_widget_account_list (self, page_box,  name, documentation, enclosing=None, packed=None):
        pass
    def set_ui_value_account_list (self, use_default, widget, value):
        pass
    def get_ui_value_account_list (self, widget):
        pass
    def set_ui_widget_account_sel (self, page_box,  name, documentation, enclosing=None, packed=None):
        pass
    def set_ui_value_account_sel (self, use_default, widget, value):
        pass
    def get_ui_value_account_sel (self, widget):
        pass
    def set_ui_widget_list (self, page_box,  name, documentation, enclosing=None, packed=None):
        pass
    def set_ui_value_list (self, use_default, widget, value):
        pass
    def get_ui_value_list (self, widget):
        pass

    def create_multichoice_widget (self):
        num_values = len(self.guile_option.ok_values)

        store = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_STRING)
        for indx,opt in enumerate(self.guile_option.ok_values):
            #label = opt.name
            #tip = opt.description
            label = opt[0]
            tip = opt[1]
            store.append((label,tip))

        widget = self.gnc_combott(store)
        # not seeing where this is done in scheme/C
        # note this is making the default value the index
        widget.set_active(self.guile_option.default_value-1)
        #widget.set_model(store)
        widget.connect("changed",self.multichoice_cb)

        return widget

    def gnc_combott (self, model):
        # thats a load of implementing - just go with plain combo box for the moment
        # OK - it is important that the model is added BEFORE the add_attribute
        combobox = gtk.ComboBox(model)
        cell = gtk.CellRendererText()
        combobox.pack_start(cell, True)
        combobox.add_attribute(cell, 'text', 0)
        return combobox


    def create_radiobutton_widget (self):
        num_values = len(self.guile_option.ok_values)

        frame = gtk.Frame()
        box = gtk.HBox(homogeneous=False, spacing=5)
        frame.add(box)

        widget = None
        for indx,opt in enumerate(self.guile_option.ok_values):
            label = opt.name
            tip = opt.description

            widget = gtk.RadioButton(group=widget,label=N_(label))
            widget.set_data("gnc_radiobutton_index",indx)
            widget.set_tooltip_text(N_(tip))
            widget.connect("toggled",self.radiobutton_cb)
            box.pack_start(expand=False,fill=False,padding=0)

        return frame

# for some reason this function is called in the gncmod module initialization function for gnome-utils
# gnc_options_ui_initialize
# the following implements gnc_options_ui_initialize at python module level

# not sure where to define this yet
# either as global for this module or as class variable in GNCOption??
# the following is confusing as option_name actually really should be option_type_name
optionTable = {}

class GNCOptionDef(object):
    def __init__ (self, option_name, set_widget, set_value, get_value):
        self.option_name = option_name
        self.set_widget = set_widget
        self.set_value = set_value
        self.get_value = get_value

options = [ \
          GNCOptionDef("boolean", GNCOption.set_ui_widget_boolean,
            GNCOption.set_ui_value_boolean, GNCOption.get_ui_value_boolean),
          GNCOptionDef("string", GNCOption.set_ui_widget_string,
            GNCOption.set_ui_value_string, GNCOption.get_ui_value_string),
          GNCOptionDef("text", GNCOption.set_ui_widget_text,
            GNCOption.set_ui_value_text, GNCOption.get_ui_value_text),
          GNCOptionDef("currency", GNCOption.set_ui_widget_currency,
            GNCOption.set_ui_value_currency, GNCOption.get_ui_value_currency),
          GNCOptionDef("commodity", GNCOption.set_ui_widget_commodity,
            GNCOption.set_ui_value_commodity, GNCOption.get_ui_value_commodity),
          GNCOptionDef("multichoice", GNCOption.set_ui_widget_multichoice,
            GNCOption.set_ui_value_multichoice, GNCOption.get_ui_value_multichoice),
          GNCOptionDef("date", GNCOption.set_ui_widget_date,
            GNCOption.set_ui_value_date, GNCOption.get_ui_value_date),
          GNCOptionDef("account-list", GNCOption.set_ui_widget_account_list,
            GNCOption.set_ui_value_account_list, GNCOption.get_ui_value_account_list),
          GNCOptionDef("account-sel", GNCOption.set_ui_widget_account_sel,
            GNCOption.set_ui_value_account_sel, GNCOption.get_ui_value_account_sel),
          GNCOptionDef("list", GNCOption.set_ui_widget_list,
            GNCOption.set_ui_value_list, GNCOption.get_ui_value_list),
          ]

for optobj in options:
    optionTable[optobj.option_name] = optobj


last_db_handle = 0
option_dbs = {}


class GNCSection(object):

    def __init__ (self, section_name):
        self.section_name = section_name
        self.options = []

class GNCOptionDB(object):
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
        # this should copy options from guile_options into the GNCOptionDB
        for option in self.guile_options.options_for_each():
            self.register_option_db(option)

        # in python changing so we now sort after inserting
        # option_sections is simply a list of names which we lookup in the dict
        self.option_sections_names = sorted(self.option_sections_dict.keys())
        self.option_sections = [ self.option_sections_dict[x] for x in self.option_sections_names ]
        for section in self.option_sections:
            secopts = self.option_sections_dict[section.section_name].options
            secopts.sort(key=attrgetter('guile_option.sort_tag'))
        print "junk"

    def register_option_db (self, guile_option):
        odb = option_dbs[self.handle]
        odb.options_dirty = True
        option = GNCOption(guile_option,False,None,odb)
        section_name = guile_option.section
        # hmm there is a list of sections (sorted) which is searched for the section name
        # doing it the C/scheme way is complicated - it stores the section structure
        # and searches by name
        # going to have a name list and sections list
        # probably should use a sorted dict
        # of course this fails if called outside send_options
        if section_name in self.option_sections_dict:
            self.option_sections_dict[section_name].options.append(option)
        else:
            self.option_sections_dict[section_name] = GNCSection(section_name)


    def set_ui_callbacks (self, get_ui_value, set_ui_value, set_selectable):
        self.get_ui_value_cb = get_ui_value
        self.set_ui_value_cb = set_ui_value
        self.set_selectable_cb = set_selectable

    def get_ui_value (self, lcl_option):
        # this is really contorted - we need to pass the GNCOption object
        # and the function has to be defined in the GNCOption class in any case
        # if its the internal object
        func_attr = getattr(lcl_option,self.get_ui_value_cb)
        return func_attr()

    def set_ui_value (self, lcl_option):
        # this is really contorted - we need to pass the GNCOption object
        # and the function has to be defined in the GNCOption class in any case
        # if its the internal object
        func_attr = getattr(lcl_option,self.set_ui_value_cb)
        return func_attr()

    def set_selectable (self, lcl_option):
        # this is really contorted - we need to pass the GNCOption object
        # and the function has to be defined in the GNCOption class in any case
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
        pass

    def destroy (self):
        # in python just make sure we remove holding values
        for section in self.option_sections:
            section.options = None
        self.option_sections = None



class GNCBuilder(gtk.Builder):

    def __init__ (self):
        super(gtk.Builder,self).__init__()

    def add_from_file (self, filename,  root):

        # find some global directory
        #gnc_builder_dir = gnc_path_get_gtkbuilderdir ()
        gnc_builder_dir = "/opt/local/share/gnucash/gtkbuilder"
        fname = os.path.join(gnc_builder_dir,filename)
        print "builder loading from %s root %s"%(fname,root)
        buildobjs = [ root ]
        result = self.add_objects_from_file(fname, buildobjs)
        if result == 0:
            # dont see immediate way we get errors
            #PWARN(log_module,"Couldn't load builder file: %s"%"IO ERROR")
            print "Couldn't load builder file: "
            pass
        return result


PAGE_INDEX = 0
PAGE_NAME = 1

MAX_TAB_COUNT = 4

class DialogOption(object):

    # note this class wraps the GNCOptionWin struct of C gnucash

    # NOTA BENE - switched order so can default modal
    # this combines gnc_options_dialog_new and gnc_options_dialog_new_modal
    def __init__ (self, title=None, modal=False):

        # these are defined in gnc_option_win

        # these are all gtk.Widget type
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

        # this is the GNCOptionDB type
        self.option_db = None

    def response_cb (self, dialog, response):
        print "response_cb called"
        if response == gtk.RESPONSE_HELP:
            self.help_cb()
        else:
            if response == gtk.RESPONSE_OK or response == gtk.RESPONSE_APPLY:
                self.changed_internal(self.dialog, False)
                close_cb = self.close_cb
                self.close_cb = None
                if self.apply_cb != None:
                    try:
                        self.apply_cb()
                    except Exception, errexc:
                        traceback.print_exc()
                        pdb.set_trace()
                self.close_cb = close_cb
            if response != gtk.RESPONSE_APPLY:
                if self.close_cb != None:
                    self.close_cb()
                else:
                    self.dialog.hide()

    def dialog_new (self, title, modal=False):

        # break init up similar to gnucash

        # this is a dict of signal names and functions to call
        # this could be a class object in which the single names become function names
        # unfortunately we have to use the full gnucash name
        self.builder_handlers = { \
                                # 'onDeleteWindow' : gtk.main_guit,
                                'gnc_options_dialog_response_cb' : self.response_cb,
                                }

        self.builder = GNCBuilder()
        self.builder.add_from_file("dialog-options.glade", "GnuCash Options")

        self.dialog = self.builder.get_object("GnuCash Options")
        self.page_list = self.builder.get_object("page_list_scroll")

        self.page_list_view = self.builder.get_object("page_list_treeview")

        store = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING)
        self.page_list_view.set_model(store)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(N_("Page"), renderer, text=1)
        self.page_list_view.append_column(column)
        column.set_alignment(0.5)

        selection = self.page_list_view.get_selection()
        selection.set_mode(gtk.SELECTION_BROWSE)

        selection.connect("changed", self.list_select_cb)


        #gtk_builder_connect_signals_full (builder, gnc_builder_connect_full_func, retval);
        self.builder.connect_signals(self.builder_handlers)

        if title:
            self.dialog.set_title(title)

        if modal:
            apply_button = self.builder.get_object("applybutton")
            apply_button.hide()

        hbox = self.builder.get_object("notebook placeholder")
        self.notebook = gtk.Notebook()
        self.notebook.show()
        hbox.pack_start(self.notebook, expand=True, fill=True, padding=5)

        component_close_callback_type = ctypes.CFUNCTYPE(None,ctypes.c_void_p)

        component_id = gnc_plugin_page.libgnc_apputils.gnc_register_gui_component("dialog-options", None, component_close_callback_type(self.component_close_handler), hash(self))

        #session = _sw_app_utils.gnc_get_current_session()
        session = gnc_plugin_page.libgnc_apputils.gnc_get_current_session()

        #_sw_app_utils.gnc_gui_component_set_session(component_id, session)
        gnc_plugin_page.libgnc_apputils.gnc_gui_component_set_session(component_id, session)


    def component_close_handler (self, arg):
        gtk.Dialog.response(arg.dialog, gtk.REPONSE_CANCEL)

    def dialog_destroy (self):

        gnc_plugin_page.libgnc_apputils.gnc_unregister_gui_component_by_data("dialog-options", hash(self))

        self.dialog.destroy()

        self.dialog = None
        self.notebook = None
        self.apply_cb = None
        self.help_cb = None


    # these are the primary creation methods
    # - trying to solve the way the C code splits the new functions

    @classmethod
    def OptionsDialog_New(cls, title, modal=False):
        newobj = cls(title,modal)
        newobj.dialog_new(title,modal)
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
        print "reset cb", args
        # args are clicked widget then dialog_option


    def add_option (self, option_box, option):
        option.set_ui_widget(option_box)

    # not sure we really need this - just access dialog attribute
    def widget (self):
        return self.dialog

    def changed_internal (self, widget, sensitive):

        #pdb.set_trace()

        #oldwidget = widget.get_ancestor(gtk.Dialog)
        while widget and not isinstance(widget, gtk.Dialog):
            widget = widget.parent
        if widget == None:
            return

        widget.set_response_sensitive(gtk.RESPONSE_OK, sensitive)
        widget.set_response_sensitive(gtk.RESPONSE_APPLY, sensitive)


    def append_page (self, section):

        name = section.section_name
        if name == None or name == "":
            return None

        if name[0:2] == '__':
            return None

        advanced = name[0:2] == '_+'
        name_offset = 2 if advanced else 0

        page_label = gtk.Label(str=N_(name[name_offset:]))
        #PINFO("Page_label is %s", _(name + name_offset));
        page_label.show()

        page_content_box = gtk.VBox(homogeneous=False, spacing=2)
        page_content_box.set_border_width(12)

        options_box = gtk.VBox(homogeneous=False, spacing=5)
        options_box.set_border_width(0)
        page_content_box.pack_start(options_box, expand=True, fill=True, padding=0)

        for option in section.options:
            self.add_option(options_box, option)

        buttonbox = gtk.HButtonBox()
        buttonbox.set_layout(gtk.BUTTONBOX_EDGE)
        buttonbox.set_border_width(5)
        page_content_box.pack_end(buttonbox, expand=False, fill=False, padding=0)

        reset_button = gtk.Button(label=N_("Reset defaults"))
        reset_button.set_tooltip_text(N_("Reset all values to their defaults."))

        reset_button.connect("clicked",self.reset_cb, self)
        reset_button.set_data("section", section)
        buttonbox.pack_end(reset_button, expand=False, fill=False, padding=0)
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

               self.notebook_page.set_data("listitem", None)
               self.notebook_page.set_data("advanced", advanced)

        return page_count


    def build_contents (self, odb):
        self.build_contents_full(odb, True)

    def build_contents_full (self, odb, show_dialog=True):

        # this doesnt work the same in python
        # get_ui_value_internal is a method of GNCOption class
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
