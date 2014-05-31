
# add a Report object for details of each report
# not sure what to inherit from

from report_options import OptionsDB
from report_options import StringOption,MultiChoiceOption


# define a function equivalent to N_ for internationalization
def N_(msg):
    return msg


# hmm there seems to be a similar report class in scheme
# which stores details of the report

# for the moment lets use combo class
# still need to figure about report templates
# although for python different instances might be how to do it
# - the class is the template and each instance a specific report

# so report is going to be the base class and the different types
# become subclasses??


class ParamsData(object):
    def __init__ (self):
        self.win = None
        self.db = None
        self.options = None
        self.cur_report = None

    def apply_cb (self):
        print "paramsdata apply_cb called"
        self.db.commit()
        self.cur_report.dirty = True
    def help_cb (self):
        print "paramsdata help_cb called"
        parent = self.win.dialog
        dialog = gtk.MessageDialog(parent,gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_INFO,gtk.BUTTONS_OK,N_("Set the report options you want using this dialog."))
        dialog.connect("response", self.dialog_destroy)
        dialog.show()
    def close_cb (self):
        print "paramsdata close_cb called"
        self.cur_report.report_editor_widget = None
        self.win.dialog_destroy()
        self.db.destroy()
    def dialog_destroy (self, widget, response):
        widget.destroy()


class Stylesheet(object):
    def __init__ (self):
        pass
    @classmethod
    def get_html_style_sheets(cls):
        return []


class ReportTemplate(object):
    def __init__ (self):
        # these are the scheme template data items

        # the following items are defined on report creation
        # seems to me in python these become arguments to the Report class instantiation
        # and we define the functions as a subclass 
        self.version = None
        self.name = "Welcome to GnuCash"
        self.report_guid = None
        self.menu_tip = None
        self.menu_path = None

        # in scheme this contains a function which is defined in the actual report .scm file
        self.options_generator = None

        # in scheme this contains a function which is defined in the actual report .scm file
        self.renderer = None

        # do not do any GUI stuff in here - we instantiate before actually needed
        # in order to get menu name to build menu

        # these are additional variables
        self.parent_type = None

        self.options_cleanup_cb = None
        self.options_changed_cb = None

        self.in_menu = False

        self.menu_name = None
        self.export_types = None
        self.export_thunk = None

    def init_gui (self):
        # this is a function to init GUI stuff if needed
        pass

    def get_template_name (self):
        return self.name

    def new_options (self):
        # OK finally figured what this does in scheme
        # gnc:report-template-new-options gets the generator from self.options_generator
        # in ReportTemplate
        # we define these 2 options
        # it then calls gnc:new-options if the generator is not defined
        # gnc:new-options creates the hash table(s) databases
        namer = StringOption("General","Report name", "0a", N_("Enter a descriptive name for this report."), self.name)
        stylesheet = MultiChoiceOption("General","Stylesheet", "0b", N_("Select a stylesheet for the report."), Stylesheet.get_html_style_sheets())
        # think Ive got this - the report creates the options_generator function
        # which defines the reports options
        if self.options_generator:
            options = self.options_generator()
        else:
            options = OptionsDB()
        # I think these are added in addition
        options.register_option(namer)
        options.register_option(stylesheet)

        return options


class Report(object):

    def __init__ (self, report_name, report_type=None):

        #pdb.set_trace()

        self.report_name = report_name

        # somehow this is where the template is stored - possibly through hash id in scheme
        if report_type != None:
            self.report_type = report_type
        else:
            self.report_type = ReportTemplate()

        self.report_editor_widget = None
        self.id = None

        self.options = self.report_type.new_options()

        self.needs_save = False
        self.dirty = False
        self.ctext = None
        self.custom_template = None

    def get_editor (self):
        return self.report_editor_widget

    def get_report_type (self):
        return self.report_type

    def start_editor (self):

        if self.report_editor_widget:
           print type(self.report_editor_widget)
           self.report_editor_widget.present()
        else:
           self.report_editor_widget = self.default_params_editor(self.options)

    # yet I think in python we need to invert the arguments here report first, options next
    # not clear why the report editor isnt just part of the Report object
    # - yes Im thinking this makes much more sense -  in which case the report argument becomes self

    def default_params_editor (self, options):

       editor = self.get_editor()
       if editor:
           editor.present()
           # why return NULL here - doesnt make sense
           # maybe we never get here in real code
           # this whole test does not make sense
           # returning this makes the process cyclic
           # return None
           return editor
       else:

           # is this just used for the callbacks??
           # think so
           default_params_data = ParamsData()

           # in scheme self.options are the options in scheme which is where the option value is stored
           # GNCOptionDB essentially wraps those options in code for interacting with those options
           # using gtk
           default_params_data.options = self.options
           default_params_data.cur_report = self
           default_params_data.db = dialog_options.GNCOptionDB(default_params_data.options)

           rpttyp = self.get_report_type()
           # this is C code
           #tmplt = rpttyp.get_template()
           #title = tmplt.get_template_name()
           # so for in python only need this
           title = rpttyp.get_template_name()

           default_params_data.win = dialog_options.DialogOption.OptionsDialog_New(title)

           default_params_data.win.build_contents(default_params_data.db)
           default_params_data.db.clean()

           # OK changing this to work in python
           # we make these functions part of ParamsData then only need to pass the function!!
           #default_params_data.win.set_apply_cb(default_params_data.apply_cb,default_params_data)
           #default_params_data.win.set_help_cb(default_params_data.help_cb,default_params_data)
           #default_params_data.win.set_close_cb(default_params_data.close_cb,default_params_data)
           # oh maybe its even easier in python - we just directly set the attribute name!!
           default_params_data.win.apply_cb = default_params_data.apply_cb
           default_params_data.win.help_cb = default_params_data.help_cb
           default_params_data.win.close_cb = default_params_data.close_cb

           # could use
           #return default_params_data.win.dialog
           return default_params_data.win.widget()



# have a hash table for reports - this ensures the
# report objects are not deallocated
# for the moment use a global here
reports = {}

