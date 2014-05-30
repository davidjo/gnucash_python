# finally we need to create a new class
# to run reports in python

import sys

import os

import pdb

import traceback


import gtk

import gobject


#pdb.set_trace()


# define a function equivalent to N_ for internationalization
def N_(msg):
    return msg



class OptionsDB(object):
    # note this is a scheme database in normal gnucash
    def __init__ (self,options=None):
        self.option_hash = {}
        self.changed_hash = {}
        self.callback_hash = {}
    def lookup_name (self, section, option_name):
        section_hash = self.option_hash[section]
        option = self.section_hash[option_name]
        # apparently options can be renamed in scheme
    def option_changed (self, section, option_name):
        pass
    def clear_changes (self):
        pass
    def register_callback (self, section, name, callback):
        pass
    def register_option (self, new_option):
        name = new_option.name
	section = new_option.section
        if section in self.option_hash:
            self.option_hash[section][name] = new_option
        else:
            self.option_hash[section]= {}
            self.option_hash[section][name] = new_option
        new_option.callback = self.option_changed
    def options_for_each (self):
        for section_hash in self.option_hash:
            option_hash = self.option_hash[section_hash]
            for name in option_hash:
                yield option_hash[name]


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
         # ;; This function should return a list of all the strings
         # ;; in the option other than the section, name, (define
         # ;; (list-lookup list item) and documentation-string that
         # ;; might be displayed to the user (and thus should be
         # ;; translated).
         self.strings_getter = None
         # weird this seems to be missing in scheme definition documentation
         # but does exist in code
         self.callback = None
         # ;; This function will be called when the GUI representation
         # ;; of the option is changed.  This will normally occur before
         # ;; the setter is called, because setters are only called when
         # ;; the user selects "OK" or "Apply".  Therefore, this
         # ;; callback shouldn't be used to make changes to the actual
         # ;; options database.
         self.widget_changed_proc = None

         # value storage for the moment
         self.option_value = None

         # make the getters/setters default to the functions defined in base?
         # not seen where actually define the getters/setters
         self.getter = self.get_value
         self.default_getter = self.get_default_value
         self.setter = self.set_value

    # havent seen where this is defined - probably in scheme somewhere
    def get_default_value (self):
        return self.default_value

    # havent seen where this is defined - probably in scheme somewhere
    def get_value (self):
        # I think gnucash is storing these in the Kvp database - hence
        # those functions
        # punting for the moment
        # this ought to be calling the setter/getter functions
        if self.option_value == None:
            return self.default_value
        return self.option_value

    # havent seen where this is defined - probably in scheme somewhere
    def set_value (self, value):
        # I think gnucash is storing these in the Kvp database - hence
        # those functions
        # punting for the moment
        # this ought to be calling the setter/getter functions
        # and the validator functions
        self.option_value = value
        

# these only fill partial values of above
# going with a subclass

class StringOption(OptionBase):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value=None):
        super(StringOption,self).__init__()
        self.section = section
        self.name = optname
        self.type = 'string'
        self.sort_tag = sort_tag
        self.documentation_string = tool_tip # AKA documentation_string
        self.default_value = default_value

class MultiChoiceOption(OptionBase):

    def __init__ (self, section, optname, sort_tag, tool_tip, default_value=None):
        super(MultiChoiceOption,self).__init__()
        self.section = section
        self.name = optname
        self.type = 'multichoice'
        self.sort_tag = sort_tag
        self.documentation_string = tool_tip # AKA documentation_string
        self.default_value = default_value



