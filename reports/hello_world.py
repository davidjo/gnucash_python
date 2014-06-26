

# how to do internationalization in python
#import gettext
#gettext.bindtextdomain('myapplication', '/path/to/my/language/directory')
#gettext.textdomain('myapplication')
#_ = gettext.gettext
# dummy function for internationalization
def N_(msg):
    return msg

import datetime

# ah - so essentially what the Scheme is doing is using a DOM model
# so Im now thinking in python why re-invent the wheel - just use the
# python inbuilt xml dom models
# the suggestion is to use  ElementTree rather than minidom
# - although minidom might be closer to the Scheme implementation

import xml.etree.ElementTree as ET

# this is an attempt at replicating the Hello, World scheme report

# this will be used to figure out ways to implement report writing in python

# we need to subclass something - but what??
# Im thinking this is ReportTemplate

#import gnc_html_document_full
import gnc_html_document

from report_objects import ReportTemplate

# maybe store the class in ReportTemplate then dont need this import
# yes we need a better way to handle this so dont need all these includes
from report_objects import OptionsDB
#from report_options import BooleanOption
#from report_options import MultiChoiceOption
# lets try importing all
from report_options import *

class HelloWorld(ReportTemplate):

    def __init__ (self):

        # need to set the  base variables
        self.version = 1
        self.name = N_("Hello, World")
        self.report_guid = "898d78ec92854402bf76e20a36d24ade"
        self.menu_name = N_("Sample Report with Examples")
        self.menu_tip = N_("A sample report with examples.")
        self.menu_path = N_("Sample & Custom")


    def options_generator (self):

        # need to instantiate the options database
        self.options = OptionsDB()

        # this is how we should add options I think
        self.options.register_option(SimpleBooleanOption(N_("Hello, World!"), N_("Boolean Option"),"a",
                                                           N_("This is a boolean option."), True))

        # should the list be a dict or not??
        self.options.register_option(MultiChoiceOption(N_("Hello, World!"), N_("Multi Choice Option"),"b",
                                                         N_("This is a multi choice option."),
                                                         'Second Option',
                                                         [ \
                                                         [ N_("First Option"), N_("Help for first option.") ],
                                                         [ N_("Second Option"), N_("Help for second option.") ],
                                                         [ N_("Third Option"), N_("Help for third option.") ],
                                                         [ N_("Fourth Option"), N_("The fourth option rules!") ],
                                                         ]))

        self.options.register_option(StringOption(N_("Hello, World!"), N_("String Option"),"c",
                                                      N_("This is a string option."), N_("Hello, World")))

        self.options.register_option(DateOption(N_("Hello, World!"), N_("Just a Date Option"),"d",
                                                      N_("This is a date option."),
                                                      lambda : ('absolute', datetime.datetime.now()),
                                                      False, 'absolute', False))

        self.options.register_option(DateOption(N_("Hello, World!"), N_("Time and Date Option"),"e",
                                                      N_("This is a date option with time."),
                                                      lambda : ('absolute', datetime.datetime.now()),
                                                      True, 'absolute', False))

        self.options.register_option(DateOption(N_("Hello, World!"), N_("Combo Date Option"),"y",
                                                      N_("This is a combination date option."),
                                                      lambda : ('relative', 'start-cal-year'),
                                                      False, 'both', ('start-cal-year', 'start-prev-year', 'end-prev-year')))

        self.options.register_option(DateOption(N_("Hello, World!"), N_("Relative Date Option"),"x",
                                                      N_("This is a relative date option."),
                                                      lambda : ('relative', 'start-cal-year'),
                                                      False, 'relative', ('start-cal-year', 'start-prev-year', 'end-prev-year')))

        self.options.register_option(NumberRangeOption(N_("Hello, World!"), N_("Number Option"),"ee",
                                                         N_("This is a number option."),
                                                         1500.0,
                                                         0.0,
                                                         10000.0,
                                                         2.0,
                                                         0.01))

        self.options.register_option(ColorOption(N_("Hello, World!"), N_("Background Option"),"f",
                                                   N_("This is a color option."),
                                                   (0xf6, 0xff, 0xdb, 0), 255, False))

        self.options.register_option(ColorOption(N_("Hello, World!"), N_("Text Option"),"f",
                                                   N_("This is a color option."),
                                                   (0x00, 0x00, 0x00, 0), 255, False))

        dummystr = """
        self.options.register_option(AccountListOption(N_("Hello Again"), N_("An account list option"),"g",
                                                         N_("This is a account list option."),
                                                         [],
                                                         False, True))
        """

        self.options.register_option(ListOption(N_("Hello Again"), N_("A list option"),"h",
                                                  N_("This is a list option."),
                                                  [0],
                                                  # again is this a dict or simple list??
                                                  [ \
                                                  [ N_("The Good"), N_("Good option.") ],
                                                  [ N_("The Bad"), N_("Bad option.") ],
                                                  [ N_("The Ugly"), N_("Ugly option.") ],
                                                  ]))

        # we need to set the default option section - the one selected
        # gnc:options-set-default-section options "Hello, World!"

        return self.options
                                             

    def renderer (self):

        # this actually implements the report look

        # lots of stuff about getting option values

        # now for html creation
        # where do we actually instantiate the Html object

        # need to set a style
        # (gnc:html-document-set-style!
        #  document "body"
        #  'attribute (list "bgcolor" (gnc:color-option->html bg-color-op))
        #  'font-color (gnc:color-option->html txt-color-op))

        #document = gnc_html_document_full.HtmlDocument()
        document = gnc_html_document.HtmlDocument()

        document.title = N_("Hello, World")

        # Im seeing how this works in scheme report system
        # the scheme report system creates lists of entities to be added
        # Im thinking this is not the way to go in python
        # the only real issue is option replacement and links to
        # account pages
        # the various plotting options

        new_text = N_("""This is a sample GnuCash report in python.""")

        base_markup = document.doc.Element("p")
        base_markup.text = new_text

        new_markup = document.doc.Element("p")
        new_markup.text = N_("The current time is ")

        new_time = document.doc.SubElement(new_markup,"b")
        new_time.text = datetime.datetime.now().strftime("%X")
        # annoying but this is where we add the remaining string for "The current time is "
        new_time.tail = N_(".")

        optobj = self.options.lookup_name('Hello, World!','Boolean Option')
        optval = optobj.getter()

        new_markup = document.doc.Element("p")
        new_markup.text = N_("The boolean option is ")

        new_opt = document.doc.SubElement(new_markup,"b")
        new_opt.text = N_("true") if optval else N_("false")
        # annoying but this is where we add the remaining string
        new_opt.tail = N_(".")

        optobj = self.options.lookup_name('Hello, World!','Multi Choice Option')
        optval = optobj.get_option_value()

        new_markup = document.doc.Element("p")
        new_markup.text = N_("The multi-choice option is ")

        new_opt = document.doc.SubElement(new_markup,"b")
        new_opt.text = optval
        # annoying but this is where we add the remaining string
        new_opt.tail = N_(".")



        return document.get_xml()
