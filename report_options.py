# finally we need to create a new class
# to run reports in python

import sys

import os

import numbers

from operator import itemgetter


import pdb

import traceback


import gtk

import gobject


try:
    import sw_app_utils
    import gnucash
    #from gnucash import *
    #from _sw_core_utils import gnc_prefs_is_extra_enabled
except Exception, errexc:
    print >> sys.stderr, "Failed to import!!"
    print >> sys.stderr, str(errexc)
    pdb.set_trace()


#pdb.set_trace()


# define a function equivalent to N_ for internationalization
def N_(msg):
    return msg



class OptionsDB(object):
    # note this is a scheme database in normal gnucash
    def __init__ (self,options=None):
        self.option_hash = {}
        self.options_changed = False
        self.changed_hash = {}
        self.callback_hash = {}
        self.last_callback_id = 0
    def lookup_name (self, section, option_name):
        section_hash = self.option_hash[section]
        option = section_hash[option_name]
        # apparently options can be renamed in scheme
        # theres a load of coding renaming some options
        return option
    def option_changed (self, section, option_name):
        self.options_changed = True
        if section not in self.changed_hash: 
            self.changed_hash[section] = {}
        self.changed_hash[section][option_name] = True
    def clear_changes (self):
        self.options_changed = False
        self.changed_hash = {}
    def register_callback (self, section, name, callback):
        print "optionsDB register_callback"
        self.last_callback_id += 1
        self.callback_hash[self.last_callback_id] = [section, name, callback]
        return self.last_callback_id
    def unregister_callback (self, callback_id):
        print "optionsDB unregister_callback"
        if callback_id in self.callback_hash:
            del self.callback_hash[self.last_callback_id]
        else:
            print "unregister callback - nonexistent ID!!", callback_id
            pdb.set_trace()
            print "unregister callback - nonexistent ID!!", callback_id
    def run_callbacks (self):
        if self.options_changed:
            cblist = []
            for idky in self.callback_hash:
                cblist.append((idky,self.callback_hash[idky]))
            cblist.sort(key=itemgetter(1))
            for clbitm in cblist:
                self.run_callback(clbitm[0],clbitm[1])
        self.clear_changes()
    def run_callback (self, id, cbdata):
        #pdb.set_trace()
        section = cbdata[0] 
        name = cbdata[1] 
        callback = cbdata[2] 
        if not section:
            callback()
        else:
            section_changed_hash = self.changed_hash[section]
            if section_changed_hash:
                if name == None:
                    callback()
                elif name in section_changed_hash:
                    callback()
    def register_option (self, new_option):
        name = new_option.name
	section = new_option.section
        if section in self.option_hash:
            self.option_hash[section][name] = new_option
        else:
            self.option_hash[section]= {}
            self.option_hash[section][name] = new_option
        # this doesnt make sense in python
        new_option.changed_callback = lambda : self.option_changed(section,name)
    def options_for_each (self):
        #pdb.set_trace()
        for section_hash in self.option_hash:
            option_hash = self.option_hash[section_hash]
            for name in option_hash:
                yield option_hash[name]

    def add_report_date (self, pagename, optname, sort_tag):
        self.register_option(EndDateOption(pagename, optname, sort_tag, N_("Select a date to report on.")))

    def add_date_interval (self, pagename, name_from, name_to, sort_tag):
        # scheme has a make-date-interval - but that just ends up as 2 DateOptions
        # create FromDataOption and use that here
        # just do 2 date options here - as we cant call register_option as scheme does
        # this is better
        date_from = FromDateOption(pagename, name_from, sort_tag+"a", N_("Start of reporting period."))
        date_to = EndDateOption(pagename, name_to, sort_tag+"b", N_("End of reporting period."))
        self.register_option(date_from)
        self.register_option(date_to)

    def add_interval_choice (self, pagename, optname, sort_tag, default):
        self.register_option(MultiChoiceOption(pagename, optname, sort_tag,
                                                N_("The amount of time between data points."),
                                                default,
                                                [ \
                                                 ('DayDelta', N_("Day"), N_("One Day.")),
                                                 ('WeekDelta', N_("Week"), N_("One Week.")),
                                                 ('TwoWeekDelta', N_("2Week"), N_("Two Weeks.")),
                                                 ('MonthDelta', N_("Month"), N_("One Month.")),
                                                 ('QuarterDelta', N_("Quarter"), N_("One Quarter.")),
                                                 ('HalfYearDelta', N_("HalfYear"), N_("HalfYear.")),
                                                 ('YearDelta', N_("Year"), N_("One Year.")),
                                                ]))

    def add_currency (self, pagename, name_report_currency, sort_tag):
        self.register_option(CurrencyOption(pagename, name_report_currency, sort_tag,
                                             N_("Select the currency to display the values of this report in."),
                                             sw_app_utils.default_report_currency()))

    def add_plot_size (self, pagename, name_width, name_height, sort_tag, default_width, default_height):
        self.register_option(NumberRangeOption(pagename, name_width, sort_tag+"a",
                                                 N_("Width of plot in pixels."), default_width,
                                                 100, 20000, 0, 5))
        self.register_option(NumberRangeOption(pagename, name_height, sort_tag+"b",
                                                 N_("Height of plot in pixels."), default_height,
                                                 100, 20000, 0, 5))

    def add_marker_choice (self, pagename, optname, sort_tag, default):
        self.register_option(MultiChoiceOption(pagename, optname, sort_tag,
                                                N_("Choose the marker for each data point."),
                                                default,
                                                [ \
                                                 ('diamond', N_("Diamond"), N_("Hollow diamond")),
                                                 ('circle', N_("Circle"), N_("Hollow circle")),
                                                 ('square', N_("Square"), N_("Hollow square")),
                                                 ('cross', N_("Cross"), N_("Cross")),
                                                 ('plus', N_("Plus"), N_("Plus")),
                                                 ('dash', N_("Dash"), N_("Dash")),
                                                 ('filleddiamond', N_("Filled Diamond"), N_("Diamond filled with color")),
                                                 ('filledcircle', N_("Filled circle"), N_("Circle filled with color")),
                                                 ('filledsquare', N_("Filled square"), N_("Square filled with color")),
                                                ]))


# for the moment try making some classes based on the scheme/C
# these probably will be changed

# python implementation of the scheme options
# we have a class for each type??
# trying this first


# bugger these options are more complicated
# looks like they are stored in some form of hash table
# which also stores the optons-changed callback

# oh great there is a further underlying class for options in scheme

class OptionBase(object):

    def __init__ (self):

        # ;; The category of this option
        self.section = None
        self.name = None
        # ;; The sort-tag determines the relative ordering of options in
        # ;; this category. It is used by the gui for display.
        self.sort_tag = None
        self.type = None
        self.documentation_string = None 
        self.getter = None
        # ;; The setter is responsible for ensuring that the value is valid.
        self.setter = None
        self.default_getter = None
        # ;; Restore form generator should generate an ascii representation
        # ;; of a function taking one argument. The argument will be an
        # ;; option. The function should restore the option to the original
        # ;; value.
        self.generate_restore_form = None
        # ;; the scm->kvp and kvp->scm functions should save and load
        # ;; the option to a kvp.  The arguments to these function will be
        # ;; a kvp-frame and a base key-path list for this option.
        self.scm_to_kvp = None
        self.kvp_to_scm = None
        # ;; Validation func should accept a value and return (#t value)
        # ;; on success, and (#f "failure-message") on failure. If #t,
        # ;; the supplied value will be used by the gui to set the option.
        self.value_validator = None
        # ;;; free-form storage depending on type.
        self.option_data = None
        # ;; If this is a "multiple choice" type of option,
        # ;; this should be a vector of the following five functions:
        # ;;
        # ;; Function 1: taking no arguments, giving the number of choices
        # ;;
        # ;; Function 2: taking one argument, a non-negative integer, that
        # ;; returns the scheme value (usually a symbol) matching the
        # ;; nth choice
        # ;;
        # ;; Function 3: taking one argument, a non-negative integer,
        # ;; that returns the string matching the nth choice
        # ;;
        # ;; Function 4: takes one argument and returns the description
        # ;; containing the nth choice
        # ;;
        # ;; Function 5: giving a possible value and returning the index
        # ;; if an option doesn't use these,  this should just be a #f
        self.option_data_fns = None
        # this seems to be an additional callback
        self.changed_callback = None
        # ;; This function should return a list of all the strings
        # ;; in the option other than the section, name, (define
        # ;; (list-lookup list item) and documentation-string that
        # ;; might be displayed to the user (and thus should be
        # ;; translated).
        self.strings_getter = None
        # ;; This function will be called when the GUI representation
        # ;; of the option is changed.  This will normally occur before
        # ;; the setter is called, because setters are only called when
        # ;; the user selects "OK" or "Apply".  Therefore, this
        # ;; callback shouldn't be used to make changes to the actual
        # ;; options database.
        self.widget_changed_cb = None

        # value storage for the moment
        self.option_value = None

        # make the getters/setters default to the functions defined in base?
        # these are defined in the gnc:make-... functions in scheme
        # but generally as lambda functions rather than explict functions
        # dont see why lambda needed in python
        self.getter = self.get_value
        self.default_getter = self.get_default_value
        self.setter = self.set_value

        # unlike scheme going to make this explicit
        self.setter_function_called_cb = None

    # havent seen where this is defined - probably in scheme somewhere
    def get_default_value (self):
        return self.default_value

    # havent seen where this is defined - probably in scheme somewhere
    def get_value (self):
        # I think gnucash is storing these in the Kvp database - hence
        # those functions
        # punting for the moment
        if self.option_value == None:
            return self.default_value
        return self.option_value

    # havent seen where this is defined - probably in scheme somewhere
    # the getter and setter seemed to be defined as lambda functions in scheme
    # we can only do one-line lambdas in python so need to make explicit functions
    def set_value (self, value):
        # I think gnucash is storing these in the Kvp database - hence
        # those functions
        # punting for the moment
        # this ought to be calling the setter/getter functions
        # and the validator functions
        self.option_value = value

        if callable(self.setter_function_called_cb):
            self.setter_function_called_cb(value)

        if self.changed_callback:
            self.changed_callback()
        

# these only fill partial values of above
# going with a subclass

class ComplexBooleanOption(OptionBase):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value=None, setter_function_called_cb=None,option_widget_changed_cb=None):
        super(ComplexBooleanOption,self).__init__()
        self.section = section
        self.name = optname
        self.type = 'boolean'
        self.sort_tag = sort_tag
        self.documentation_string = tool_tip # AKA documentation_string
        self.default_value = default_value

        # need to deal with setter and getter functions
        #self.setter = self.local_setter(x)

        self.widget_changed_cb = option_widget_changed_cb

        # this is stored via a lambda in scheme
        self.setter_function_called_cb = setter_function_called_cb

        # the setter and getter seem to store in the Kvp database

    def local_setter (self, x):
        self.option_value = x
        if callable(self.setter_function_called_cb):
            self.setter_function_called_cb(x)

    def value_validator (self, x):
        if type(x) == bool:
            return [ True, x ]
        else:
            return [ False, "boolean-option: not a boolean" ]


class SimpleBooleanOption(ComplexBooleanOption):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value=None):
        super(SimpleBooleanOption,self).__init__(section, optname, sort_tag, tool_tip, default_value=default_value,setter_function_called_cb=None,option_widget_changed_cb=None)

class StringOption(OptionBase):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value=None):
        super(StringOption,self).__init__()
        self.section = section
        self.name = optname
        self.type = 'string'
        self.sort_tag = sort_tag
        self.documentation_string = tool_tip # AKA documentation_string
        self.default_value = default_value

class MultiChoiceCallbackOption(OptionBase):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value=None,ok_values=[],setter_function_called_cb=None,option_widget_changed_cb=None):
        super(MultiChoiceCallbackOption,self).__init__()
        self.section = section
        self.name = optname
        self.type = 'multichoice'
        self.sort_tag = sort_tag
        self.documentation_string = tool_tip # AKA documentation_string
        self.option_data = ok_values
        self.option_data_fns = [ \
                                lambda : len(self.option_data),
                                lambda x: self.option_data[x][0],
                                lambda x: self.option_data[x][1],
                                lambda x: self.option_data[x][2],
                                lambda x: self.lookup(x),
                               ]
        # cant do this till set option_data!!
        # scheme stores the key index string - here we store the index
        self.default_value = self.lookup_key(default_value)

        #self.setter = self.local_setter

        # the setter and getter seem to store in the Kvp database

        # 

        self.widget_changed_cb = option_widget_changed_cb

        self.strings_getter = self.multichoice_strings

        self.setter_function_called_cb = setter_function_called_cb

    def local_setter (self, x):
        if self.legal(x):
            if callable(self.setter_function_called_cb):
                self.setter_function_called_cb(x)
        else:
            # gnc:error "Illegal Multichoice option set"
            pass

    def lookup_key (self, x):
        # return the index for a key string
        for indx,itm in enumerate(self.option_data):
            if itm[0] == x:
                return indx
        return -1

    def lookup (self, x):
        # return whole sublist for a key as per scheme
        for indx,itm in enumerate(self.option_data):
            if itm[0] == x:
                return itm
        return None

    def legal (self, x):
        # this checks the key string (index 0) - not the displayed strings (index 1 or 2)
        for itm in self.option_data:
            if itm[0] == x:
                return True
        return False

    def multichoice_strings (self):
        # this returns the displayed strings - the option string and its tool tip
        if len(self.option_data) == 0:
           return []
        return [ (x[1],x[2]) for itm in self.option_data ]


class MultiChoiceOption(MultiChoiceCallbackOption):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value=None,ok_values=[]):
        super(MultiChoiceOption,self).__init__(section, optname, sort_tag, tool_tip, default_value=default_value,ok_values=ok_values,setter_function_called_cb=None,option_widget_changed_cb=None)


class DateOption(OptionBase):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_getter=None,show_time=False,subtype=None,relative_date_list=[]):
        super(DateOption,self).__init__()
        self.section = section
        self.name = optname
        self.type = 'date'
        self.sort_tag = sort_tag
        self.documentation_string = tool_tip # AKA documentation_string

        # although this is called the default_getter its actually the default value
        # these are lambda functions in scheme but dont know why
        self.default_value = default_getter

        #self.generate_restore_form = ??.restore_form_generator(self.option_value)

        self.option_data = (subtype, show_time, relative_date_list)
        self.option_data_fns = (lambda : len(relative_date_list),
                                lambda (x): relative_date_list[x],
                                lambda (x): self.get_relative_date_string(relative_date_list[x]),
                                lambda (x): self.get_relative_date_desc(relative_date_list[x]),
                                lambda (x): self.relative_date_list.index(x))
        # two False slots in addition
        self.changed_callback = None
        self.strings_getter = None
        # which means this is not set
        #self.widget_changed_cb = None

    def default_setter (self, date):
        if self.date_legal(date):
            self.option_value = date
        else:
            #gnc:error "Illegal date value set:" date
            pass

        # the setter and getter seem to store in the Kvp database

    def default_value_validator (self, date):
        if self.date_legal(date):
            return [True, date]
        else:
            return [False, "date-option: illegal date"]


class EndDateOption(DateOption):

    def __init__ (self, section, optname, sort_tag, tool_tip):
        super(EndDateOption,self).__init__ (section, optname, sort_tag, tool_tip,
                                             ('relative', 'end-accounting-period'),
                                             False,
                                             'both',
                                             ('today',
                                              'end-this-month',
                                              'end-prev-month',
                                              'end-current-quarter',
                                              'end-prev-quarter',
                                              'end-cal-year',
                                              'end-prev-year',
                                              'end-accounting-period',
                                             ))

class FromDateOption(DateOption):

    def __init__ (self, section, optname, sort_tag, tool_tip):
        super(FromDateOption,self).__init__(section, optname, sort_tag, tool_tip,
                                             ('relative', 'start-accounting-period'),
                                             False,
                                             'both',
                                             ('today',
                                              'start-this-month',
                                              'start-prev-month',
                                              'start-current-quarter',
                                              'start-prev-quarter',
                                              'start-cal-year',
                                              'start-prev-year',
                                              'start-accounting-period',
                                             ))


class CurrencyOption(OptionBase):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value):
        super(CurrencyOption,self).__init__()
        self.section = section
        self.name = optname
        self.type = 'currency'
        self.sort_tag = sort_tag
        self.documentation_string = tool_tip # AKA documentation_string

        # currency default is a GncCommodity object
        self.default_value = default_value

        # what to do about getters/setters
        # the issue is are we storing a proper gnc_commodity structure pointer
        # or the currency string - looks like the structure pointer
        # this is one way to call the super function
        # in a local getter/setter function
        self.super_getter = self.getter
        self.super_setter = self.setter
        self.getter = self.local_getter
        self.setter = self.local_setter

        #self.generate_restore_form = ??.restore_form_generator(self.option_value)

        self.value_validator = lambda x : [ True, x ]

    def local_getter (self):
        # need python bindings here
        #pdb.set_trace()
        currency = self.super_getter()
        # this appears to be what scheme is doing
        if isinstance(currency,str):
            cmd_tbl = sw_app_utils.get_current_book().get_table()
            cmd_cur = cmd_tbl.lookup("CURRENCY",currency)
        else:
            cmd_cur = currency
        return cmd_cur

    def local_setter (self, currency):
        pdb.set_trace()
        if isinstance(currency,str):
            retval = currency
        else:
            retval = currency.get_mnemonic()
        # ignoring scheme lambda
        self.super_setter(retval)


class CommodityOption(OptionBase):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value):
        super(CommodityOption,self).__init__()
        self.section = section
        self.name = optname
        self.type = 'commodity'
        self.sort_tag = sort_tag
        self.documentation_string = tool_tip # AKA documentation_string

        # commodity option is a mnemonic string
        # this is not right - we appear to just pass a string
        # which somehow needs to map to this internal form
        # dont see how this is setup
        # this is very junky and assumes default_value is a currency
        self.default_value = ('commodity-scm', "CURRENCY", default_value)

        # what to do about getters/setters
        # the issue is are we storing a proper gnc_commodity structure pointer
        # or the currency string - looks like the structure pointer
        self.super_getter = self.getter
        self.super_setter = self.setter
        self.getter = self.local_getter
        self.setter = self.local_setter

        #self.generate_restore_form = ??.restore_form_generator(self.option_value)

        self.value_validator = lambda x : [ True, x ]

    def local_getter (self):
        # need python bindings here
        #pdb.set_trace()
        commodity_str = self.super_getter()
        # this appears to be what scheme is doing
        cmd_tbl = sw_app_utils.get_current_book().get_table()
        cmd_cur = cmd_tbl.lookup(commodity_str[1], commodity_str[2])
        return cmd_cur

    def local_setter (self, commodity):
        # need python bindings here
        #pdb.set_trace()
        # this appears to be what scheme is doing
        if isinstance(commodity,str):
            option_value = ( 'commodity-scm', "CURRENCY", commodity )
        else:
            option_value = ( 'commodity-scm', commodity.get_namespace(), commodity.get_mnemonic() )
        self.super_setter(option_value)


class NumberRangeOption(OptionBase):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value, lower_bound, upper_bound, num_decimals, step_size):
        super(NumberRangeOption,self).__init__()
        self.section = section
        self.name = optname
        self.type = 'number-range'
        self.sort_tag = sort_tag
        self.documentation_string = tool_tip # AKA documentation_string

        # what to do about getters/setters

        self.default_value = default_value

        self.option_data = (lower_bound, upper_bound, num_decimals, step_size)

    def value_validator (self, x):
        if not isinstance(x, numbers.Number):
            return [ False, "number-range-option: not a number" ]
        if x < self.option_data[0] or x > self.option_data[1]:
            return [ False, "number-range-option: out of range" ]
        return [ True, x ]


class ColorOption(OptionBase):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value, range, use_alpha):
        super(ColorOption,self).__init__()
        self.section = section
        self.name = optname
        self.type = 'color'
        self.sort_tag = sort_tag
        self.documentation_string = tool_tip # AKA documentation_string

        # what to do about getters/setters

        self.default_value = default_value

        self.option_data = (range, use_alpha)

    def values_in_range (self, color):
        for x in color:
            if x < 0 or x > self.option_data[0]:
                return False
        return True

    def value_validator (self, color):
        if not isinstance(color, list):
            return [ False, "color-option: not a list" ]
        elif len(color) != 4:
            return [ False, "color-option: wrong length" ]
        elif not self.values_in_range(color):
            return [ False, "color-option: bad color values" ]
        return [ True, color ]
