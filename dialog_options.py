
# this is a recoding of the options dialog (defined in dialog-options.c)
# in python

import os

import sys

import gobject

import gtk


import _sw_app_utils
import gnc_plugin_page
import ctypes


import pdb


# junky internationalization function
def N_(msg):
    return msg

# option dialog calls

#12 0x000000010003f262 in gnc_plugin_page_report_options_cb ()
#1  0x000000010004135a in gnc_report_window_default_params_editor ()
#0  0x00000001001e9354 in gnc_options_dialog_build_contents ()


class GNCOption(object):

    def __init__ (self, guile_option, changed=False, widget=None, odb=None):
        self.guile_option = guile_option
        self.changed = changed
        self.widget = widget
        self.odb = odb

    def get_ui_value (self):
        # OK this is really stupid - we have multiple redirection here
        # we call a function in the GNCOptionDB class
        # which by default is set to the internal function in this class
        #return self.odb.get_ui_value(self)
        # for the moment punt just call the internal function directly
        return self.get_ui_value_internal()

    def set_ui_value (self, use_default):
        # this is weird - wheres the value 
        #if self.odb.get_ui_value == None:
        #    return
        #self.odb.set_ui_value(self,use_default)
        # for the moment punt just call the internal function directly
        self.set_ui_value_internal(use_default)

    def ui_get_option (self, option_name):
        global optionTable
        if option_name in optionTable:
            return optionTable[option_name]
        else:
            #PERR("Option lookup for type '%s' failed!", option_name);
            pdb.set_trace()
            return None

    def set_ui_value_internal (self, use_default):

        # ah - now see what this is doing - we are copying the value
        # from scheme into the optionTable hash version

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
                #PERR("bad value\n");
                pdb.set_trace()
                pass
        else:
            #PERR("Unknown type. Ignoring.\n");
            pdb.set_trace()
            pass

    def get_ui_value_internal (self):

        widget = self.widget
        if widget == None:
            return None
        type = self.guile_option.type
        option_def = self.ui_get_option(type)
        if option_def:
            result = option_def.get_value(self,widget)
        else:
            #PERR("Unknown type for refresh. Ignoring.\n");
            pdb.set_trace()
            result = None
        return result

    def set_selectable_internal (self, selectable):

        widget = self.widget
        if widget == None:
            return None
        widget.set_sensitive(selectable)

    def set_ui_widget (self, page_box):

        #ENTER("option %p(%s), box %p",
        #      option, gnc_option_name(option), page_box);
        if self.type == None:
            #LEAVE("bad type");
            return

        raw_name = self.name
        if raw_name != None and raw_name != "":
            name = N_(raw_name)
        else:
            name = None

        raw_documention = self.documentation
        if raw_documentation != None and raw_documentation != "":
            documentation = N_(raw_documentation)
        else:
            documentation = None

        option_def = self.guile_option.ui_get_option(type)

        value = None
        enclosing = None
        packed = None
        if option_def and option_def.set_widget != None:
            (value, enclosing, packed) = option_def.set_widget(page_box, name, documentation)
        else:
            #PERR("Unknown option type. Ignoring option \"%s\".\n", name);
            pdb.set_trace()

        if not packed and enclosing != None:

            eventbox = gtk.EventBox()

            eventbox.add(enclosing)
            pagebox.pack_start(eventbox, expand=False, fill=False, padding=0)

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
    def set_ui_widget_string (self, page_box, name, documentation, enclosing, packed):
        # we need to return enclosing and packed
        pass
    def set_ui_value_string (self, use_default, widget, value):
        pass
    def get_ui_value_string (self, widget):
        pass
    def set_ui_widget_text (self, page_box,  name, documentation, enclosing, packed):
        pass
    def set_ui_value_text (self, use_default, widget, value):
        pass
    def get_ui_value_text (self, widget):
        pass
    def set_ui_widget_currency (self, page_box,  name, documentation, enclosing, packed):
        pass
    def set_ui_value_currency (self, use_default, widget, value):
        pass
    def get_ui_value_currency (self, widget):
        pass
    def set_ui_widget_commodity (self, page_box,  name, documentation, enclosing, packed):
        pass
    def set_ui_value_commodity (self, use_default, widget, value):
        pass
    def get_ui_value_commodity (self, widget):
        pass
    def set_ui_widget_multichoice (self, page_box,  name, documentation, enclosing, packed):
        pass
    def set_ui_value_multichoice (self, use_default, widget, value):
        pass
    def get_ui_value_multichoice (self, widget):
        pass
    def set_ui_widget_date (self, page_box,  name, documentation, enclosing, packed):
        pass
    def set_ui_value_date (self, use_default, widget, value):
        pass
    def get_ui_value_date (self, widget):
        pass
    def set_ui_widget_account_list (self, page_box,  name, documentation, enclosing, packed):
        pass
    def set_ui_value_account_list (self, use_default, widget, value):
        pass
    def get_ui_value_account_list (self, widget):
        pass
    def set_ui_widget_account_sel (self, page_box,  name, documentation, enclosing, packed):
        pass
    def set_ui_value_account_sel (self, use_default, widget, value):
        pass
    def get_ui_value_account_sel (self, widget):
        pass
    def set_ui_widget_list (self, page_box,  name, documentation, enclosing, packed):
        pass
    def set_ui_value_list (self, use_default, widget, value):
        pass
    def get_ui_value_list (self, widget):
        pass

# for some reason this function is called in the gncmod module initialization function for gnome-utils
# gnc_options_ui_initialize
# the following implements gnc_options_ui_initialize at python module level

# not sure where to define this yet
# either as global for this module or as class variable in GNCOption??
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


option_dbs = {}


class GNCSection(object):

    def __init__ (self, section_name):
        self.section_name = section_name
        self.options = []

class GNCOptionDB(object):
    def __init__ (self, guile_options):
        # copy of guile options
        self.guile_options = guile_options
        self.option_sections = []
        self.options_dirty = False
        self.handle = None
        # we have to rename these in python
        #self.get_ui_value = None
        #self.set_ui_value = None
        #self.set_selectable = None
        self.get_ui_value_cb = None
        self.set_ui_value_cb = None
        self.set_selectable_cb = None

        # this is in gnc_option_db_init
        self.send_options()

    def send_options (self):
        # this should copy options from guile_options into the GNCOptionDB
        #pdb.set_trace()
        #for option in self.guile_options:
        #    self.register_option_db(option)
        pass

    def register_option_db (self, guile_option):
        odb = option_dbs[handle]
        option = GNCOption(guile_option,False,None,odb)
        section_name = guile_option.section()
        section = GNCSection(section_name)
        # hmm there is a list of sections (sorted) which is searched for the section name
        # doing it the C/scheme way is complicated - it stores the section structure
        # and searches by name
        try:
            old = self.option_sections.index(section_name)
            section = old
        except ValueError:
            self.option_sections.append(section_name)
            self.option_sections = sorted(self.option_sections)

        section.options.append(option)
        self.option = sorted(self.options)

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
            #PWARN ("Couldn't load builder file: %s", error->message);
            print "Couldn't load builder file: "
            pass
        return result


PAGE_NAME = 1

class DialogOption(object):

    # note this class wraps the GNCOptionWin struct of C gnucash

    # NOTA BENE - switched order so can default modal
    # this combines gnc_options_dialog_new and gnc_options_dialog_new_modal
    def __init__ (self, title=None, modal=False):

        # these are defined in gnc_option_win

        # these are all gkt.Widget type
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
                    self.apply_cb()
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


    def add_option (self, option_box, option):
        option.set_ui_widget(option_box)

    # not sure we really need this - just access dialog attribute
    def widget (self):
        return self.dialog

    def changed_internal (self, widget, sensitive):

        #oldwidget = widget.get_ancestor(gtk.Dialog)
        while widget and not isinstance(widget, gtk.Dialog):
            widget = widget.parent()
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

        for option in section.options():
            self.add_option(options_box, option)



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
                if option.widget_changed_proc:
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
