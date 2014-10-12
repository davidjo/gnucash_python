# finally we need to create a new class
# to run reports in python

import sys

import os

import numbers

import datetime

from operator import itemgetter


import pdb

import traceback


# not apparently needed
# either
#from gi.repository import Gtk
#from gi.repository import GObject
# or
#import gtk
#import gobject


try:
    import sw_app_utils
    import gnucash
    #from gnucash import *
    #from _sw_core_utils import gnc_prefs_is_extra_enabled
except Exception, errexc:
    print >> sys.stderr, "Failed to import!!"
    print >> sys.stderr, str(errexc)
    pdb.set_trace()

import date_utils

import gnucash_log


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
        self.default_section = None
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
        gnucash_log.dbglog("optionsDB register_callback")
        self.last_callback_id += 1
        self.callback_hash[self.last_callback_id] = [section, name, callback]
        return self.last_callback_id
    def unregister_callback (self, callback_id):
        gnucash_log.dbglog("optionsDB unregister_callback")
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
        if section == None:
            callback()
        else:
            section_changed_hash = self.changed_hash[section]
            if section_changed_hash != None:
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
        # oh maybe it does - we get multiple instances of the lambda each with
        # a different section, name variables
        new_option.changed_callback = lambda lcl_sect=section,lcl_name=name: self.option_changed(lcl_sect,lcl_name)
    def options_for_each (self):
        #pdb.set_trace()
        for section_hash in self.option_hash:
            option_hash = self.option_hash[section_hash]
            for name in option_hash:
                yield option_hash[name]
    def set_default_section (self, section_name):
        self.default_section = section_name
    def get_default_section (self):
        return self.default_section

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

    def add_price_source (self, pagename, optname, sort_tag, default):
        self.register_option(MultiChoiceOption(pagename, optname, sort_tag,
                                             N_("The source of price information."),
                                             default,
                                             [ \
                                               ('average-cost', N_("Average Cost"), N_("The volume-weighted average cost of purchases.")),
                                               ('weighted-average', N_("Weighted Average"), N_("The weighted average of all currency transactions of the past.")),
                                               ('weighted-average', N_("Weighted Average"), N_("The weighted average of all currency transactions of the past.")),
                                               ('pricedb-latest', N_("Most recent"), N_("The most recent recorded price.")),
                                               ('pricedb-nearest', N_("Nearest in time"), N_("The price recorded nearest in time to the report date.")),
                                             ]))

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

    def add_account_selection (self, pagename, name_display_depth, name_show_subaccounts, name_accounts, sort_tag, default_depth, default_accounts, default_show_subaccounts):
        self.add_account_levels(pagename, name_display_depth, sort_tag+"a",
                                                N_("Show accounts to this depth, overriding any other option."),
                                                default_depth)
        self.register_option(SimpleBooleanOption(pagename, name_show_subaccounts, sort_tag+"b",
                                                N_("Override account-selection and show sub-accounts of all selected accounts?"), default_show_subaccounts))
        self.register_option(AccountListOption(pagename, name_accounts, sort_tag+"c",
                                                N_("Report on these accounts, if display depth allows."), default_accounts, False, True))

    def add_account_levels (self, pagename, name_display_depth, sort_tag, help_string, default_depth):
        self.register_option(MultiChoiceOption(pagename, name_display_depth, sort_tag,
                                                help_string,
                                                default_depth,
                                                [ \
                                                 ('all', N_("All"), N_("All accounts")),
                                                 ('1', N_("1"), N_("Top-level.")),
                                                 ('2', N_("2"), N_("Second-level.")),
                                                 ('3', N_("3"), N_("Second-level.")),
                                                 ('4', N_("4"), N_("Fourth-level.")),
                                                 ('5', N_("5"), N_("Fifth-level.")),
                                                 ('6', N_("6"), N_("Sixth-level.")),
                                                ]))


# for the moment try making some classes based on the scheme/C
# these probably will be changed

# python implementation of the scheme options
# we have a class for each type??
# trying this first


# these options are more complicated
# looks like they are stored in some form of hash table
# which also stores the options-changed callback

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
        # this seems to be an additional callback
        # ah - the make-option function defines the callback function as none
        # so needs to be explicitly defined in a subclass
        self.changed_callback = None

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

    # now think these functions not defined as scheme not object oriented
    # so all the make-option arguments have lambda functions which define
    # these functions which are then stored in the variable which are called
    # when the variable is accessed

    # havent seen where this is defined - probably in scheme somewhere
    def get_default_value (self):
        return self.default_value

    # havent seen where this is defined - probably in scheme somewhere
    def get_value (self):
        # I think gnucash is storing these in the Kvp database - hence
        # those functions
        # punting for the moment
        if self.option_value == None:
            return self.get_default_value()
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
        # not sorted this yet - we need to allow for a subclass setter
        # which must always call the changed_callback function
        # we probably could use lambdas like scheme
        # which saves the subclass setter function in the lambda function
        # and then the lambda function is stored in the setter attribute
        self.option_value = value

        if callable(self.changed_callback):
            self.changed_callback()

    def set_changed_callback (self, callback):
        # we need to call this function in a subclass to define the callback
        self.changed_callback = callback


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
        # I think because these are variables containing functions
        # we need to do this rather than use super() function
        # need to re-evaluate this sometime and make more pythonic
        self.super_setter = self.setter
        self.setter = self.local_setter


        # this is stored via a lambda in scheme
        self.widget_changed_cb = option_widget_changed_cb

        # this is stored via a lambda in scheme
        self.setter_function_called_cb = setter_function_called_cb

        # the setter and getter seem to store in the Kvp database

    def local_setter (self, x):
        # this is not right - in scheme the super_setter calls
        # the changed_callback after the setter_function_called_cb
        # here its called before
        self.super_setter(x)
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

    def get_value_as_html (self):
        val = self.getter()
        if val:
            return "true"
        return "false"

class StringOption(OptionBase):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value=None):
        super(StringOption,self).__init__()
        self.section = section
        self.name = optname
        self.type = 'string'
        self.sort_tag = sort_tag
        self.documentation_string = tool_tip # AKA documentation_string
        self.default_value = default_value

    # we need to define a validator
    def value_validator (self, x):
        if type(x) == str:
            return [True, x]
        else:
            return [False, "string-option: not a string"]

    def get_option_value (self):
        # again this is a function for returning value in the python script
        # this seems to be viable for strings
        return self.getter()


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
        self.option_data_dict = {}
        for indx,itm in enumerate(self.option_data):
            kywd = itm[0]
            self.option_data_dict[kywd] = indx
        # for the moment check we have a string
        if not isinstance(default_value,str):
            raise TypeError("wrong type for default value in multi-choice option")
        if self.lookup_key(default_value) < 0:
            raise KeyError("unknown key symbol for default value in multi-choice option: %s"%default_value)
        # we are storing the key string now not the key index
        #self.default_value = self.lookup_key(default_value)
        self.default_value = default_value

        # need to deal with setter and getter functions
        # I think because these are variables containing functions
        # we need to do this rather than use super() function
        # need to re-evaluate this sometime and make more pythonic
        self.super_setter = self.setter
        self.setter = self.local_setter

        #self.super_getter = self.getter
        #self.getter = self.local_getter

        # the setter and getter seem to store in the Kvp database

        # 

        self.widget_changed_cb = option_widget_changed_cb

        self.strings_getter = self.multichoice_strings

        self.setter_function_called_cb = setter_function_called_cb

    #def local_getter (self):
    #    pdb.set_trace()
    #    retval = self.super_getter()
    #    return retval

    def local_setter (self, x):
        # this is not right - in scheme the super_setter calls
        # the changed_callback after the setter_function_called_cb
        # here its called before
        if self.legal(x):
            self.super_setter(x)
            if callable(self.setter_function_called_cb):
                self.setter_function_called_cb(x)
        else:
            gnucash_log.gnc_error("Illegal Multichoice option set")

    def lookup_key (self, x):
        # return the index for a key string
        #for indx,itm in enumerate(self.option_data):
        #    if itm[0] == x:
        #        return indx
        if x in self.option_data_dict:
            return self.option_data_dict[x]
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


    def get_option_value (self):
        # again this is a function for returning value in the python script
        # we are now returning the key value
        optmrk = self.getter()
        #return self.option_data[optmrk][0]
        return optmrk



class MultiChoiceOption(MultiChoiceCallbackOption):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value=None,ok_values=[]):
        super(MultiChoiceOption,self).__init__(section, optname, sort_tag, tool_tip, default_value=default_value,ok_values=ok_values,setter_function_called_cb=None,option_widget_changed_cb=None)


class ListOption(OptionBase):

    #  self.options.register_option(ListOption(N_("Hello, World!"), N_("A list option"),"h",
    #                                             N_("This is a list option."),
    #                                             ['good'],
    #                                             [ \
    #                                             [ 'good', N_("The Good"), N_("Good option.") ],
    #                                             [ 'bad', N_("The Bad"), N_("Bad option.") ],
    #                                             [ 'ugly', N_("The Ugly"), N_("Ugly option.") ],
    #                                             ]))

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value=None,ok_values=None,option_widget_changed_cb=None):
        super(ListOption,self).__init__()
        self.section = section
        self.name = optname
        self.type = 'list'
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
        # create dict of values
        # this assumes all keys unique - is this a requirement??
        self.option_data_dict = {}
        for indx,itm in enumerate(self.option_data):
            kywd = itm[0]
            self.option_data_dict[kywd] = indx

        # store a list of key strings as in scheme
        # do a bit of type checking
        self.default_value = []
        for dfvl in default_value:
            if not isinstance(dfvl,str):
                raise TypeError("wrong type for default value in list option")
            if self.lookup_key(dfvl) < 0:
                raise KeyError("unknown key symbol for default value in list option: %s"%dfvl)
            self.default_value.append(dfvl)

        self.super_setter = self.setter
        self.setter = self.local_setter

        # the setter and getter seem to store in the Kvp database

        # 

        self.widget_changed_cb = option_widget_changed_cb

        self.strings_getter = self.list_strings

        #self.setter_function_called_cb = setter_function_called_cb

    def local_setter (self, x):
        # this is not right - in scheme the super_setter calls
        # the changed_callback after the setter_function_called_cb
        # here its called before
        if self.legal(x):
            self.super_setter(x)
            if callable(self.setter_function_called_cb):
                self.setter_function_called_cb(x)
        else:
            gnucash_log.gnc_error("Illegal List option set")

    def lookup_key (self, x):
        # return the index for a key string
        #for indx,itm in enumerate(self.option_data):
        #    if itm[0] == x:
        #        return indx
        if x in self.option_data_dict:
            return self.option_data_dict[x]
        return -1

    def lookup (self, x):
        # return whole sublist for a key as per scheme
        #for indx,itm in enumerate(self.option_data):
        #    if itm[0] == x:
        #        return itm
        if x in self.option_data_dict:
            return self.option_data[self.option_data_dict[x]]
        return None

    def legal (self, x):
        # this checks the key string (index 0) - not the displayed strings (index 1 or 2)
        #for itm in self.option_data:
        #    if itm[0] == x:
        #        return True
        for itm in x:
            if not itm in self.option_data_dict:
                return False
        return True

    def list_strings (self):
        # this returns the displayed strings - the option string and its tool tip
        if len(self.option_data) == 0:
           return []
        return [ (x[1],x[2]) for itm in self.option_data ]


    def get_option_value (self):
        # again this is a function for returning value in the python script
        # can we return multiple values or just one??
        optmrk = self.getter()
        #vallst = []
        #for mrk in optmrk:
        #   vallst.append(self.option_data[mrk][0])
        #return vallst
        return optmrk


class AccountListLimitedOption(OptionBase):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value=None,value_validator=None,multiple_selection=None,acct_type_list=[],option_widget_changed_cb=None):
        super(AccountListLimitedOption,self).__init__()
        self.section = section
        self.name = optname
        self.type = 'account-list'
        self.sort_tag = sort_tag
        self.documentation_string = tool_tip # AKA documentation_string
        self.option_data = [multiple_selection, acct_type_list]
        self.default_value = default_value

        self.getter = self.account_list_getter
        self.setter = self.account_list_setter
        self.default_getter = self.account_list_default_getter

        #self.strings_getter = self.multichoice_strings

        self.widget_changed_cb = option_widget_changed_cb

        # note this function must return a 2 tuple - True/False and a list
        # we need to save the passed validator function in python
        self.value_validator = self.local_validator
        self.save_value_validator = value_validator

        # this is a flag which is True of False depending if
        # account items are account pointers or guids
        self.option_set = None

        #self.option_value = map(self.convert_to_guid,self.default_getter())

    # in scheme the following functions apparently convert account lists
    # into guid lists for self.option_value using the functions convert_to_guid
    # and inverse convert_to_account
    # for the moment ignoring this

    def convert_to_guid (self, itm):
        if type(itm) != str:
            return itm.GetGUID()
        return itm

    def convert_to_account (self, itm):
        # not valid!!
        if type(itm) == str:
             account = gnucash.GUID.AccountLookup(acc_guid,curbook)
             account = xaccAccountLookup(gnc_get_current_book(),itm)
             return account
        return itm


    def account_list_getter (self):
        #pdb.set_trace()
        # re-define to deal with lambda definitions
        # this seems to be the code in scheme
        # 
        #if option_set:
        #    return map(self.convert_to_guid,self.account_list_default_getter())
        #    return self.option_value
        #else:
        #    return self.account_list_default_getter()

        if self.option_value == None:
            return self.account_list_default_getter()
        if callable(self.option_value):
            return self.option_value()
        else:
            return self.option_value

    def account_list_setter (self, account_list):
        pdb.set_trace()
        if account_list == None or len(account_list) == 0:
            account_list = self.default_getter()
        # the following maybe a translation of the scheme code
        # the usage of filter seems to be to apply the lambda code to each element
        # dont see how it actually filters anything
        newlst = []
        for x in account_list:
             if type(x) == str:
                 xacc = gnucash.GUID.AccountLookup(x,curbook)
                 xacc = xaccAccountLookup(gnc_get_current_book(),x)
             else:
                 xacc = x
             newlst.append(xacc)
        account_list = newlst
        # list should be validated
        (valid, value) = self.local_validator(account_list)
        if valid:
            #self.option_value = map(self.convert_to_guid,value)
            self.option_value = value
            self.option_set = True
        else:
            gnucash_log.gnc_error("Illegal account list value set")
            pdb.set_trace()
            pass

    def account_list_default_getter (self):
        #pdb.set_trace()
        if callable(self.default_value):
            defval = self.default_value()
        else:
            defval = self.default_value
        #return self.convert_to_account(defval)
        return defval

    def lookup_key (self, x):
        pdb.set_trace()
        # return the index for a key string
        for indx,itm in enumerate(self.option_data):
            if itm[0] == x:
                return indx
        return -1

    def lookup (self, x):
        pdb.set_trace()
        # return whole sublist for a key as per scheme
        for indx,itm in enumerate(self.option_data):
            if itm[0] == x:
                return itm
        return None

    def local_validator (self, account_list):
        pdb.set_trace()
        if self.save_value_validator == None:
            return [True, account_list]
        else:
            #account_list = map(self.convert_to_account,account_list)
            return self.save_value_validator(account_list)


    def get_option_value (self):
        # again this is a function for returning value in the python script
        #pdb.set_trace()
        acclst = self.getter()
        return acclst


class AccountListOption(AccountListLimitedOption):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value=None,value_validator=None,multiple_selection=None):
        super(AccountListOption,self).__init__(section, optname, sort_tag, tool_tip, default_value=default_value,value_validator=value_validator,multiple_selection=multiple_selection,acct_type_list=[])



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
        # I guess this can either be a callable (lambda in scheme) or plain value
        self.default_value = default_getter

        #self.generate_restore_form = ??.restore_form_generator(self.option_value)

        self.option_data = (subtype, show_time, relative_date_list)
        #self.option_data_fns = (lambda : len(relative_date_list),
        #                        lambda (x): relative_date_list[x],
        #                        lambda (x): self.get_relative_date_string(relative_date_list[x]),
        #                        lambda (x): self.get_relative_date_desc(relative_date_list[x]),
        #                        lambda (x): relative_date_list.index(x))
        self.option_data_fns = (lambda : len(self.option_data[2]),
                                lambda (x): self.option_data[2][x],
                                lambda (x): self.get_relative_date_string(self.option_data[2][x]),
                                lambda (x): self.get_relative_date_desc(self.option_data[2][x]),
                                lambda (x): self.option_data[2].index(x))
        # two False slots in addition
        self.strings_getter = None
        #self.widget_changed_cb = None

        # setup local setter
        self.super_setter = self.setter
        self.setter = self.local_setter

    def get_default_value (self):
        # re-define to deal with lambda definitions
        if callable(self.default_value):
            return self.default_value()
        else:
            return self.default_value


    def local_setter (self, date):
        #pdb.set_trace()
        if self.date_legal(date):
            self.super_setter(date)
        else:
            gnucash_log.gnc_error("Illegal date value set: %s"%date)

        # the setter and getter seem to store in the Kvp database

    def default_value_validator (self, date):
        if self.date_legal(date):
            return [True, date]
        else:
            return [False, "date-option: illegal date"]

    def date_legal (self, date):
        #pdb.set_trace()
        # something not sorted - an absolute date is a pair in scheme
        # maybe because date and time??
        # date[1] should be a symbol - whatever that is
        # punt with str for the moment
        if (((type(date) == tuple or type(date) == list)) and \
            len(date) == 2) or \
            ((date[0] == 'relative' and type(date[1]) == str) or \
               (date[0] == 'absolute' and type(date[1]) == datetime.datetime)):
            return True
        pdb.set_trace()
        return False

    def lookup_string (self, datestr):
        # somewhere in scheme the DateOption strings are looked up in the
        # databases defined in date-utilities.scm
        if datestr in date_utils.relative_date_values:
            return date_utils.relative_date_values[datestr]
        else:
            pdb.set_trace()
            print "junk"

    def lookup_key (self, x):
        # return the index for a key string
        for indx,itm in enumerate(self.option_data[2]):
            if itm == x:
                return indx
        return -1

    def lookup_index (self, x):
        # return the key string for an index
        datestr = self.option_data[2][x]
        return datestr

    def get_option_value (self):
        # this is a function for returning suitable python values 
        # not figured a good name yet
        # somehow in gnucash the date formats are selectable
        # based on region
        optval = self.getter()
        if self.option_data[0] == 'absolute':
            if optval[0] == 'absolute':
                return optval[1]
            elif optval[0] == 'relative':
                # is this ever possible??
                pdb.set_trace()
                rettpl = self.lookup_string(optval[1])
                fy_period = rettpl[2]()
                return fy_period
            else:
                pdb.set_trace()
                print optval
        elif self.option_data[0] == 'relative':
            if optval[0] == 'absolute':
                # is this ever possible??
                pdb.set_trace()
                return optval[1]
            elif optval[0] == 'relative':
                rettpl = self.lookup_string(optval[1])
                fy_period = rettpl[2]()
                return fy_period
            else:
                pdb.set_trace()
                print optval
        else:
            #pdb.set_trace()
            # still not sure how both version works
            # do we ignore self.option_data and just check optval?
            if self.option_data[1] != None:
                gnucash_log.dbglog("both - absolute defined")
            else:
                gnucash_log.dblgog("both - relative defined")
            if optval[0] == 'absolute':
                return optval[1]
            elif optval[0] == 'relative':
                rettpl = self.lookup_string(optval[1])
                fy_period = rettpl[2]()
                return fy_period
            else:
                pdb.set_trace()
                # is this ever possible??
                rettpl = self.lookup_string(optval[1])
                fy_period = rettpl[2]()
                return fy_period


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

    def value_validator (self, currency):
        pdb.set_trace()
        return [True, currency]


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

    def value_validator (self, commodity):
        pdb.set_trace()
        return [True, commodity]


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

    def get_option_value (self):
        # again this is a function for returning value in the python script
        return self.getter()


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

    def get_option_value (self):
        # again this is a function for returning value in the python script
        return self.getter()

    def get_value_as_html (self):
        # again this is a function for returning value in the python script
        # formatted as an html color string
        clrval = self.getter()
        clrval = [ x/float(255.0/self.option_data[0]) for x in clrval ]
        clrval = [ min(x,255.0) for x in clrval ]
        clrval = [ "%02x"%int(x) for x in clrval ]
        clrstr = "#"+"".join(clrval[0:3])
        return clrstr

class FontOption(OptionBase):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value):
        super(FontOption,self).__init__()
        self.section = section
        self.name = optname
        self.type = 'font'
        self.sort_tag = sort_tag
        self.documentation_string = tool_tip # AKA documentation_string

        # what to do about getters/setters

        self.default_value = default_value

    def value_validator (self, x):
        if type(x) == str:
            return [True, x]
        else:
            return [False, "font-option: not a string"]

    def get_option_value (self):
        # again this is a function for returning value in the python script
        return self.getter()

class PixmapOption(OptionBase):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value):
        super(PixmapOption,self).__init__()
        self.section = section
        self.name = optname
        self.type = 'pixmap'
        self.sort_tag = sort_tag
        self.documentation_string = tool_tip # AKA documentation_string

        # what to do about getters/setters

        self.default_value = default_value

    def value_validator (self, x):
        if type(x) == str:
            return [True, x]
        else:
            return [False, "pixmap-option: not a string"]

    def get_option_value (self):
        # again this is a function for returning value in the python script
        return self.getter()
