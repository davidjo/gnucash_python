
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

# ah - so essentially what the Scheme is doing is using a DOM model
# so Im now thinking in python why re-invent the wheel - just use the
# python inbuilt xml dom models
# the suggestion is to use  ElementTree rather than minidom
# - although minidom might be closer to the Scheme implementation

# we do not use this directly in a report - this is included in the
# html document via mapping functions - currently same name as
# the ElementTree function names
#import xml.etree.ElementTree as ET

# this is an attempt at replicating the Hello, World scheme report

# this will be used to figure out ways to implement report writing in python

import sw_app_utils

# partial implementation mainly for URL handlers
import gnc_html_ctypes

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

        super(ReportTemplate,self).__init__()

        # need to set the  base variables
        self.version = 1
        self.name = N_("Hello, World")
        self.report_guid = "898d78ec92854402bf76e20a36d24ade"
        self.menu_name = N_("Sample Report with Examples")
        self.menu_tip = N_("A sample report with examples.")
        self.menu_path = N_("Sample & Custom")


    def options_generator (self):

        #pdb.set_trace()

        # need to instantiate the options database
        self.options = OptionsDB()

        # this is how we should add options I think
        self.options.register_option(SimpleBooleanOption(N_("Hello, World!"), N_("Boolean Option"),"a",
                                                           N_("This is a boolean option."), True))

        # should the list be a dict or not??
        self.options.register_option(MultiChoiceOption(N_("Hello, World!"), N_("Multi Choice Option"),"b",
                                                         N_("This is a multi choice option."),
                                                         'second',
                                                         [ \
                                                         [ 'first', N_("First Option"), N_("Help for first option.") ],
                                                         [ 'second', N_("Second Option"), N_("Help for second option.") ],
                                                         [ 'third', N_("Third Option"), N_("Help for third option.") ],
                                                         [ 'fourth', N_("Fourth Option"), N_("The fourth option rules!") ],
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

        self.options.register_option(ColorOption(N_("Hello, World!"), N_("Background Color"),"f",
                                                   N_("This is a color option."),
                                                   (0xf6, 0xff, 0xdb, 0), 255, False))

        self.options.register_option(ColorOption(N_("Hello, World!"), N_("Text Color"),"f",
                                                   N_("This is a color option."),
                                                   (0x00, 0x00, 0x00, 0), 255, False))

        self.options.register_option(AccountListOption(N_("Hello Again"), N_("An account list option"),"g",
                                                         N_("This is a account list option."),
                                                         [],
                                                         None, True))

        self.options.register_option(ListOption(N_("Hello Again"), N_("A list option"),"h",
                                                  N_("This is a list option."),
                                                  ['good'],
                                                  [ \
                                                  [ 'good', N_("The Good"), N_("Good option.") ],
                                                  [ 'bad', N_("The Bad"), N_("Bad option.") ],
                                                  [ 'ugly', N_("The Ugly"), N_("Ugly option.") ],
                                                  ]))

        # we need to set the default option section - the one selected
        # gnc:options-set-default-section options "Hello, World!"

        return self.options
                                             

    def renderer (self, report):

        # this actually implements the report look

        # lots of stuff about getting option values

        #pdb.set_trace()

        # now for html creation
        # where do we actually instantiate the Html object

        # in scheme created new scheme html doc
        # in python pass the report xml document 
        # does the possibility of having new HtmlDocument make sense??
        document = gnc_html_document.HtmlDocument(stylesheet=report.stylesheet())

        clropt = self.options.lookup_name('Hello, World!','Background Color')
        txtopt = self.options.lookup_name('Hello, World!','Text Color')

        # need to set a style
        # (gnc:html-document-set-style!
        #  document "body"
        #  'attribute (list "bgcolor" (gnc:color-option->html bg-color-op))
        #  'font-color (gnc:color-option->html txt-color-op))
        # do we make eg font close to html - so font has sub-attribute color
        # or use scheme style of specific item font-color??
        document.add_body_style({"body" : { 'attribute' : { "bgcolor" : clropt.get_value_as_html() }, 'font' : { 'color' : txtopt.get_value_as_html() }}})

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
        base_markup.tail = "\n"

        new_markup = document.doc.Element("p")
        new_markup.text = N_("The current time is ")
        new_markup.tail = "\n"

        new_time = document.doc.SubElement(new_markup,"b")
        new_time.text = datetime.datetime.now().strftime("%X")
        # annoying but this is where we add the remaining string for "The current time is "
        new_time.tail = N_(".")


        optobj = self.options.lookup_name('Hello, World!','Boolean Option')
        optval = optobj.getter()

        new_markup = document.doc.Element("p")
        new_markup.text = N_("The boolean option is ")
        new_markup.tail = "\n"

        new_opt = document.doc.SubElement(new_markup,"b")
        new_opt.text = N_("true") if optval else N_("false")
        # annoying but this is where we add the remaining string
        new_opt.tail = N_(".")


        optobj = self.options.lookup_name('Hello, World!','Multi Choice Option')
        optval = optobj.get_option_value()

        new_markup = document.doc.Element("p")
        new_markup.text = N_("The multi-choice option is ")
        new_markup.tail = "\n"

        new_opt = document.doc.SubElement(new_markup,"b")
        new_opt.text = optval
        # annoying but this is where we add the remaining string
        new_opt.tail = N_(".")


        optobj = self.options.lookup_name('Hello, World!','String Option')
        optval = optobj.get_option_value()

        new_markup = document.doc.Element("p")
        new_markup.text = N_("The string option is ")
        new_markup.tail = "\n"

        new_opt = document.doc.SubElement(new_markup,"b")
        new_opt.text = optval
        # annoying but this is where we add the remaining string
        new_opt.tail = N_(".")

        # interesting - the date formatting seems to be done in the report

        optobj = self.options.lookup_name('Hello, World!','Just a Date Option')
        optval = optobj.get_option_value()
        optval = optval.strftime("%x")

        new_markup = document.doc.Element("p")
        new_markup.text = N_("The date option is ")
        new_markup.tail = "\n"

        new_opt = document.doc.SubElement(new_markup,"b")
        new_opt.text = optval
        # annoying but this is where we add the remaining string
        new_opt.tail = N_(".")


        optobj = self.options.lookup_name('Hello, World!','Time and Date Option')
        optval = optobj.get_option_value()
        optval = optval.strftime("%x %X")

        new_markup = document.doc.Element("p")
        new_markup.text = N_("The date and time option is ")
        new_markup.tail = "\n"

        new_opt = document.doc.SubElement(new_markup,"b")
        new_opt.text = optval
        # annoying but this is where we add the remaining string
        new_opt.tail = N_(".")


        optobj = self.options.lookup_name('Hello, World!','Relative Date Option')
        optval = optobj.get_option_value()
        optval = optval.strftime("%x")

        new_markup = document.doc.Element("p")
        new_markup.text = N_("The relative date option is ")
        new_markup.tail = "\n"

        new_opt = document.doc.SubElement(new_markup,"b")
        new_opt.text = optval
        # annoying but this is where we add the remaining string
        new_opt.tail = N_(".")


        optobj = self.options.lookup_name('Hello, World!','Combo Date Option')
        optval = optobj.get_option_value()
        optval = optval.strftime("%x")

        new_markup = document.doc.Element("p")
        new_markup.text = N_("The combination date option is ")
        new_markup.tail = "\n"

        new_opt = document.doc.SubElement(new_markup,"b")
        new_opt.text = optval
        # annoying but this is where we add the remaining string
        new_opt.tail = N_(".")


        optobj = self.options.lookup_name('Hello, World!','Number Option')
        optval = optobj.get_option_value()

        new_markup = document.doc.Element("p")
        new_markup.text = N_("The number option is ")
        new_markup.tail = "\n"

        new_opt = document.doc.SubElement(new_markup,"b")
        new_opt.text = str(optval)
        # annoying but this is where we add the remaining string
        new_opt.tail = N_(".")


        new_markup = document.doc.Element("p")
        new_markup.text = N_("The number option formatted as currency is ")
        new_markup.tail = "\n"

        new_opt = document.doc.SubElement(new_markup,"b")
        # apparently we can only give 2 integers - for a float
        # need to give 1 argument
        new_val = gnucash.GncNumeric(optval)
        #new_val = gnucash.GncNumeric(int(optval), 1)
        new_opt.text = sw_app_utils.PrintAmount(new_val,sw_app_utils.DefaultPrintInfo(False))
        # annoying but this is where we add the remaining string
        new_opt.tail = N_(".")

        new_markup = document.doc.Element("p")
        new_markup.text = N_("Items you selected:")
        new_markup.tail = "\n"


        optobj = self.options.lookup_name('Hello Again','A list option')
        optval = optobj.get_option_value()
        print("list option value", optval)

        if len(optval) > 0:
            new_table = document.doc.Element("table")
            new_table.attrib['cellspacing'] = "0"
            new_table.attrib['border'] = "0"
            new_table.attrib['cellpadding'] = "4"
            new_cap = document.doc.SubElement(new_table,"caption")
            new_cap.text = "List items selected"
            new_row = document.doc.SubElement(new_table,"tr")
            for optitm in optval:
                new_col = document.doc.SubElement(new_row,"td")
                new_col.text = optitm
        else:
            new_markup = document.doc.Element("p")
            new_markup.text = N_("(You selected no list items.)")
            new_markup.tail = "\n"


        optobj = self.options.lookup_name('Hello Again','An account list option')
        optval = optobj.get_option_value()

        if len(optval) > 0:
            new_markup = document.doc.Element("ul")
            for acc in optval:
                new_li = document.doc.SubElement(new_markup,"li")
                new_link = document.doc.SubElement(new_li,"a")
                # we need to use get_full_name - which maps to gnc_account_get_full_name
                # as that gives full path to an account
                # amazing - by using build_url and the gnucash access to webkit these
                # links automagically work!!
                new_link.attrib['href'] = gnc_html_ctypes.build_url(gnc_html_ctypes.URLTypes.URL_TYPE_REGISTER, "account="+acc.get_full_name(),"")
                new_link.text = acc.GetName()
        else:
            new_markup = document.doc.Element("p")
            new_markup.text = N_("You have selected no accounts.")
            new_markup.tail = "\n"

        new_link = document.doc.Element("a")
        new_link.attrib['href'] = gnc_html_ctypes.build_url(gnc_html_ctypes.URLTypes.URL_TYPE_HELP, "gnucash-guide","")
        new_link.text = N_("Display help")

        new_markup = document.doc.Element("p")
        new_markup.text = N_("Have a nice day!")
        new_markup.tail = "\n"

        return document
