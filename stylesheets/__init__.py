
import collections

import xml.etree.ElementTree as ET


import pdb


import gnc_report_system_ctypes

import gnc_html_document

from report_options import OptionsDB

from report_options import FontOption,SimpleBooleanOption


# define a function equivalent to N_ for internationalization
def N_(msg):
    return msg


# the comments in html-style-info.scm say that originally style tables
# were scheme hash tables - python equivalent is the dict
# theres something very complicated going on with "compiled" style tables
# - ignore for the moment - just use effectively plain dict

class StyleTable(collections.defaultdict):

    def __init__ (self, *args, **kwargs):
        # need to figure correct dict style arguments
        super(StyleTable,self).__init__(*args, **kwargs)
        self.cached = {}

    def __setitem__ (self, key, value):
        if key in self.cached:
            self.cached[key] = None
        super(StyleTable,self).__setitem__(key, value)

    def make_html (self, key):
        #pdb.set_trace()
        # not sure about caching now - we always need a new element
        #if key in self.cached:
        #    elm = ET.Element(tg,attrib=attrs)
        #else:
        if True:
            if key in self:
                val = self[key]
            else:
                pdb.set_trace()
            tg = key
            attrs = {}
            (subtg, subattrs) = self.update_attrs(val)
            if subtg != None: tg = subtg
            if subattrs != None: attrs = subattrs
            elm = ET.Element(tg,attrib=attrs)
        return elm

    def update_attrs (self, val):
        if isinstance(val, collections.Mapping):
            tg = None
            attrs = {}
            for ky,vl in val.items():
                if ky == 'tag':
                    tg = val['tag']
                    # need semi-recursive system - if tag exists then update
                    # attributes
                    # think this works right - find lowest tag first then as
                    # unwind the attributes with same name are overwritten with
                    # the higher and higher tag name attributes
                    if tg in self:
                        #pdb.set_trace()
                        subval = self[tg]
                        (subtg, subattrs) = self.update_attrs(subval)
                        attrs.update(subattrs)
                elif ky == 'attribute':
                    attrs = val['attribute']
                else:
                    # what to do about extras
                    print val
                    pdb.set_trace()
                    print val
            return (tg, attrs)
        else:
            return (None, None)

# not quite what I thought - this is a standalone function
def update(orig_dict, new_dict):
    for key, val in new_dict.iteritems():
        if isinstance(val, collections.Mapping):
            tmp = update(orig_dict.get(key, StyleTable()), val)
            orig_dict[key] = tmp
        elif isinstance(val, list):
            orig_dict[key] = (orig_dict[key] + val)
        else:
            orig_dict[key] = new_dict[key]
    return orig_dict

# oh great - in scheme there is a StylesheetTemplate object
# and a Stylesheet object
# I guess this follows the reports - with the Report object
# and the ReportTemplate object

# the following is mainly from html-style-sheet.scm

class Stylesheet(object):

    def __init__ (self, name, template):
        # in python we make the template the class of the stylesheet
        # save in separate variable
        self.name = name
        self.style_type_class = template
        self.style_type = None
        self.options = None
        self.renderer = None
        # this is defined but is separate from the document style table
        # stores some default styles - but not sure where copied to
        # document style table yet
        self.style = StyleTable()

    # we call this from HtmlDocument so
    # we need report as argument - now also need the doc
    def render (self, report, doc, headers=None):

        #pdb.set_trace()

        # we need to instantiate the style somewhere
        # not sure this is right place
        # why did I think this should not be done in the init
        if self.style_type == None: self.style_type = self.style_type_class()

        self.style_type.options_generator()

        # newdoc is new document
        # yes a new document is created which does NOT have
        # a style sheet defined - only has the style object defined
        # which I think is the "compiled" style sheet
        # note the new document creation is done in the specific
        # stylesheet renderer
        # we need to pass the incoming document as well
        # to deal with headline setting
        newdoc = self.style_type.renderer(doc)

        #;; push the style sheet's default styles
        #(gnc:html-document-push-style newdoc (gnc:html-style-sheet-style sheet))

        # some messing with swapping styles
        # and compiling ?? styles
        # somehow the style is not the same as the stylesheet??
        # maybe something to do with compiling the style
        # we might want to merge the styles here - NOT assign
        # which version should override??
        #update(newdoc.style,doc.style)

        # this is the sneak!!
        # newdoc does NOT have a stylesheet defined
        # so the following render call does the trivial render

        #pdb.set_trace()

        return newdoc.render(report,headers)


def get_html_style_sheets():
    #newmod = __import__(modnam, globals(), locals(), [subclsnam], -1)
    #return [ [ 'dummy', 'Dummy', 'A Dummy style sheet.' ] ]
    styllst = []
    for shtnam in stylesheets:
        styllst.append( [ shtnam.lower(), shtnam, shtnam + " " + N_("stylesheet.") ] )
    return styllst



class StylesheetTemplate(object):

    def __init__ (self):
        self.version = None
        self.name = None
        # if these are functions in the subclass then defining them here
        # makes them variables not functions
        #self.options_generator = None
        #self.renderer = None
        self.options = None

    def options_generator (self):
        raise NotimplementedError("options_generator function not implemented")

    def renderer (self):
        raise NotimplementedError("renderer function not implemented")

    def new_options (self):
        # this emulates to some extent the scheme
        options = OptionsDB()
        return options


    # the following functions taken from html-fonts.scm

    def register_font_options (self):

        font_family = gnc_report_system_ctypes.libgnc_reportsystem.gnc_get_default_report_font_family()

        self.options.register_option(FontOption(N_("Fonts"), N_("Title"),"a",
                                                         N_("Font info for the report title."),
                                                         font_family+" Bold 15"))
        self.options.register_option(FontOption(N_("Fonts"), N_("Account link"),"b",
                                                         N_("Font info for account name."),
                                                         font_family+" Italic 10"))
        self.options.register_option(FontOption(N_("Fonts"), N_("Number cell"),"c",
                                                         N_("Font info for regular number cells."),
                                                         font_family+" 10"))
        self.options.register_option(SimpleBooleanOption('Fonts', N_("Negative Values in Red"),"d",
                                                           N_("Display negative values in red."), True))
        self.options.register_option(FontOption(N_("Fonts"), N_("Number header"),"e",
                                                         N_("Font info for number headers."),
                                                         font_family+" 10"))
        self.options.register_option(FontOption(N_("Fonts"), N_("Text cell"),"f",
                                                         N_("Font info for regular text cells."),
                                                         font_family+" 10"))
        self.options.register_option(FontOption(N_("Fonts"), N_("Total number cell"),"g",
                                                         N_("Font info for number cells containing a total."),
                                                         font_family+" Bold 12"))
        self.options.register_option(FontOption(N_("Fonts"), N_("Total label cell"),"h",
                                                         N_("Font info for number cells containing total labels."),
                                                         font_family+" Bold 12"))
        self.options.register_option(FontOption(N_("Fonts"), N_("Centered label cell"),"i",
                                                         N_("Font info for centered label cells."),
                                                         font_family+" Bold 12"))


    def font_name_to_style_info (self, font_name_arg):

        #pdb.set_trace()

        font_family = "Arial"
        font_size = "20"
        font_style = None
        font_style_idx = 0
        font_weight = None
        font_weight_idx = 0
        result = ""
        font_len = len(font_name_arg)
        font_idx = 0

        font_idx = font_name_arg.rfind(' ')
        font_size = font_name_arg[font_idx+1:]
        font_name = font_name_arg[:font_idx]
        font_weight_idx = font_name.lower().find('bold')
        if font_weight_idx >= 0:
            font_weight = "bold"
            font_name = font_name[:font_weight_idx] + font_name[font_weight_idx+5:]
        font_style_idx = font_name.lower().find(' italic')
        if font_style_idx >= 0:
            font_style = "italic"
            font_name = font_name[:font_style_idx] + font_name[font_style_idx+7:]
            font_style_idx = font_name.lower().find(' oblique')
            if font_style_idx >= 0:
                font_style = "oblique"
                font_name = font_name[:font_style_idx] + font_name[font_style_idx+8:]

        font_family = font_name
        result = "font-family: " + font_family + "; " + "font-size: " + font_size + "pt; "
        if font_style:
            result += "font-style: " + font_style + "; "
        if font_weight:
            result += "font-weight: " + font_weight + "; "
        return result

    def add_css_information_to_doc (self, doc):

        # but need to figure what is right options variable

        optobj = self.options.lookup_name('Fonts', "Negative Values in Red")
        negative_red = optobj.get_value()

        optobj = self.options.lookup_name("Colors", "Alternate Table Cell Color")
        alternate_row_color = optobj.get_value_as_html()

        optobj = self.options.lookup_name("Fonts", "Title")
        font_name = optobj.get_option_value()
        title_font_info = self.font_name_to_style_info(font_name)

        optobj = self.options.lookup_name("Fonts", "Account link")
        font_name = optobj.get_option_value()
        account_link_font_info = self.font_name_to_style_info(font_name)

        optobj = self.options.lookup_name("Fonts", "Number cell")
        font_name = optobj.get_option_value()
        number_cell_font_info = self.font_name_to_style_info(font_name)

        optobj = self.options.lookup_name("Fonts", "Number header")
        font_name = optobj.get_option_value()
        number_header_font_info = self.font_name_to_style_info(font_name)

        optobj = self.options.lookup_name("Fonts", "Text cell")
        font_name = optobj.get_option_value()
        text_cell_font_info = self.font_name_to_style_info(font_name)

        optobj = self.options.lookup_name("Fonts", "Total number cell")
        font_name = optobj.get_option_value()
        total_number_cell_font_info = self.font_name_to_style_info(font_name)

        optobj = self.options.lookup_name("Fonts", "Total label cell")
        font_name = optobj.get_option_value()
        total_label_cell_font_info = self.font_name_to_style_info(font_name)

        optobj = self.options.lookup_name("Fonts", "Centered label cell")
        font_name = optobj.get_option_value()
        centered_label_cell_font_info = self.font_name_to_style_info(font_name)

        if negative_red:
            negative_red_text = "color: red; "
        else:
            negative_red_text = ""

        style_text = "\n" +\
            "h3 { " + title_font_info + " }\n" +\
            "a { " + account_link_font_info + " }\n" +\
            "body, p, table, tr, td { text-align: left; " + text_cell_font_info + " }\n" +\
            "tr.alternate-row { background: " + alternate_row_color + " }\n" +\
            "th.column-heading-left { text-align: left; " + number_header_font_info + " }\n" +\
            "th.column-heading-center { text-align: center; " + number_header_font_info + " }\n" +\
            "th.column-heading-right { text-align: right; " + number_header_font_info + " }\n" +\
            "td.neg { " + negative_red_text + " }\n" +\
            "td.number-cell, td.total-number-cell { text-align: right; white-space: nowrap; }\n" +\
            "td.date-cell { white-space: nowrap; }\n" +\
            "td.anchor-cell { white-space: nowrap; " + text_cell_font_info + " }\n" +\
            "td.number-cell { " + number_cell_font_info + " }\n" +\
            "td.number-header { text-align: right; " + number_header_font_info + " }\n" +\
            "td.text-cell { " + text_cell_font_info + " }\n" +\
            "td.total-number-cell { " + total_number_cell_font_info + " }\n" +\
            "td.total-label-cell { " + total_label_cell_font_info + " }\n" +\
            "td.centered-label-cell { text-align: center; " + centered_label_cell_font_info + " }\n"

        doc.style_text = style_text


# as noted stylesheets have a template and an "instance" in scheme
# Im still not sure if need to maintain this difference in python
# I think Im coming to the conclusion we dont need this difference

stylesheets = {}

from stylesheets.plain import Plain
stylesheets['default'] = Stylesheet('Default',Plain)

## for the moment instantiate 
## the style as a simple instance - should be instance of StyleTable
#for shtnam in stylesheets:
#    stylesheets[shtnam].style_type = stylesheets[shtnam].style_type_class()
