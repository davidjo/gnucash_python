
# add a Report object for details of each report
# not sure what to inherit from

import pdb

import gobject

from report_options import OptionsDB
from report_options import StringOption,MultiChoiceOption

import dialog_options


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
        return [ [ 'dummystyle', 'Dummy Style', 'A Dummy style sheet.' ] ]


class ReportTemplate(object):
    def __init__ (self):
        # these are the scheme template data items

        # the following items are defined on report creation
        # seems to me in python these become arguments to the Report class instantiation
        # and we define the functions as a subclass 
        self.version = None
        self.name = "Welcome to GnuCash"
        self.report_guid = None
        self.menu_name = None
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
        stylesheet = MultiChoiceOption("General","Stylesheet", "0b", N_("Select a stylesheet for the report."), 'dummystyle', Stylesheet.get_html_style_sheets())
        #pdb.set_trace()
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

    def options_changed_cb (self):
        pass


class Report(object):

    # this encodes the scheme report id functionality
    # do this as class variables or module globals??
    report_next_serial_id = 0;
    report_ids = {}

    def __init__ (self, report_type, options=None):

        # this is the equivalent of the following scheme
        # except currently we are 
        # ;; gnc:make-report instantiates a report from a report-template.
        # ;; The actual report is stored away in a hash-table -- only the id is returned.

        #pdb.set_trace()

        # something about template parents here which dont understand
        # apparently the passed report type could a child of a report

        # somehow this is where the template is stored - possibly through hash id in scheme
        # or could well be by report guid
        # yes it looks as though in scheme this is actually the guid of the report template
        # (see gnc:make-report in report.scm)
        if report_type != None:
            self.report_type = report_type
        else:
            self.report_type = ReportTemplate()

        self.id = None

        self.options = None

        self.dirty = False
        self.needs_save = False
        self.report_editor_widget = None
        self.ctext = None
        self.custom_template = None

        # this follows the scheme more closely
        if options != None:
            self.options = options
        else:
            self.options = self.report_type.new_options()

        # this does a lambda function in scheme
        # need explicit function here because of python limitations in lambda definitions
        # not quite sure of replacement yet
        # lambda_callback should be in the OptionsDB
        # I think we are doing this in order to set the dirty flag in this instance
        # on any option change
        #self.options.register_callback(None, None, lambda x : self.lambda_callback(x))


        # ah - this is where the scheme id is set and returned
        # these are defined in gnc-report.c
        # where we see the id is actually a simple count of the number of reports
        # instantiated
        #(gnc:report-set-id! r (gnc-report-add r))
        #(gnc:report-id r))
        self.id = self.report_add()


    def lambda_callback (self):
        # I think this is the primary feature of this coding - we need to set the dirty flag
        # in this instance if any of the options are changed
        self.dirty = True
        cb = self.report_type.options_changed_cb
        if cb:
            cb()

    def report_add (self):
        if self.id != None:
            if not self.id in Report.report_ids:
                Report.report_ids[self.id] = self
                return self.id
        Report.report_next_serial_id += 1
        while Report.report_next_serial_id < gobject.G_MAXINT:
            new_id = Report.report_next_serial_id 
            if not new_id in Report.report_ids:
                Report.report_ids[new_id] = self
                return new_id
            Report.report_next_serial_id += 1

        #g_warning("Unable to add report to table. %d reports in use.", G_MAXINT);


    def get_editor (self):
        return self.report_editor_widget

    def get_report_type (self):
        return self.report_type

    def options_editor (self):
        # this changes the editor for some report type
        if self.report_type == 'd8ba4a2e89e8479ca9f6eccdeb164588':
            #gnc-column-view-edit-options
            pass
        else:
            return self.default_params_editor

    def edit_options (self):
        if self.report_editor_widget:
           print type(self.report_editor_widget)
           self.report_editor_widget.present()
        else:
           if self.options:
               options_editor = self.options_editor()
               self.report_editor_widget = options_editor(self.options)
           else:
               # what to do about a parent??
               #parent = self.win.dialog
               dialog = gtk.MessageDialog(parent,gtk.DIALOG_DESTROY_WITH_PARENT,
                       gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,N_("This report has no options."))
               dialog.connect("response", self.dialog_destroy)
               dialog.show()

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
           # GncOptionDB essentially wraps those options in code for interacting with those options
           # using gtk
           default_params_data.options = self.options
           default_params_data.cur_report = self
           default_params_data.db = dialog_options.GncOptionDB(default_params_data.options)

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


# note these dicts store the report templates

python_reports_by_name = {}
python_reports_by_guid = {}

def load_python_reports ():
    # yes we need the global to write into these objects
    global python_reports_by_name
    global python_reports_by_guid
    # ok im wrong - we can instantiate here as long as do
    # very little in the __init__ - in particular no GUI
    # OK looks like this lookup is done by class - not instance
    # no - Im thinking it is instance now
    # the 'edited' reports seem to be the html text result of running the report
    # cancel the above I now think its a class again
    # not clear what the advantage is in python - we just loose the local variable
    # space with an instance compared to the class
    python_reports_by_name = {}
    python_reports_by_guid = {}

    from reports.hello_world import HelloWorld
    python_reports_by_name['HelloWorld'] = HelloWorld()
    python_reports_by_guid[python_reports_by_name['HelloWorld'].report_guid] = python_reports_by_name['HelloWorld']

    from reports.price_scatter import PriceScatter
    python_reports_by_name['PriceScatter'] = PriceScatter()
    python_reports_by_guid[python_reports_by_name['PriceScatter'].report_guid] = python_reports_by_name['PriceScatter']

