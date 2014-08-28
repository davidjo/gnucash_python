

import xml.etree.ElementTree as ET


import pdb


import gnc_html_document

from report_options import *

from stylesheets import StylesheetTemplate
from stylesheets import update


# apparently stylesheets are like mini-reports with options
#


class Plain(StylesheetTemplate):

    def __init__ (self):
        super(Plain,self).__init__()
        self.version = 1
        self.name = "Plain"
        #self.options_generator = self.options_generator
        #self.renderer = self.renderer

    def options_generator (self):

        # need to instantiate the options database
        self.options = self.new_options()

        # this is how we should add options I think
        self.options.register_option(ColorOption(N_("General"), N_("Background Color"),"a",
                                                           N_("Background color for reports."),
                                                   (0xff, 0xff, 0xff, 0), 255, False))
        #self.options.register_option(PixmapOption(N_("General"), N_("Background Pixmap"),"b",
        #                                                   N_("Background tile for reports."), ""))
        self.options.register_option(SimpleBooleanOption('General', N_("Enable Links"),"c",
                                                           N_("Enable hyperlinks in reports."), True))
        self.options.register_option(ColorOption(N_("Colors"), N_("Alternate Table Cell Color"),"a",
                                                           N_("Background color for alternate lines."),
                                                   (0xff, 0xff, 0xff, 0), 255, False))
        self.options.register_option(NumberRangeOption(N_("Tables"), N_("Table cell spacing"),"a",
                                                         N_("Space between table cells."),
                                                         0.0, 0.0, 20.0, 0.0, 1.0))
        self.options.register_option(NumberRangeOption(N_("Tables"), N_("Table cell padding"),"b",
                                                         N_("Space between table cell edge and content."),
							 4.0, 0.0, 20.0, 0.0, 1.0))
        self.options.register_option(NumberRangeOption(N_("Tables"), N_("Table border width"),"c",
                                                         N_("Bevel depth on tables."),
                                                         0.0, 0.0, 20.0, 0.0, 1.0))

        # something about font options
        #(register-font-options options)
        self.register_font_options()


    def renderer (self, doc):

        # beginning to understand the style tables
        # essentially lookup tables which have html attributes
        # note these are essentially named lookups which can have a non-html tag name
        # which are replaced by html tags/attributes/text when seen in a report

        pdb.set_trace()

        #ssdoc = gnc_html_document_full.HtmlDocument()
        ssdoc = gnc_html_document.HtmlDocument()

        # scheme loads options here

        #ssdoc.style_sheet = None

        # create a style table - scheme seems to store them globally
        # for the moment store with document
        #ssdoc.style = StyleTable()

        clropt = self.options.lookup_name('General','Background Color')

        # what we need is a special dict so will apply update to all the sub-dicts
        # found this update function online which works with normal dicts to do the same

        update(ssdoc.style,{"body" : { 'attribute' : { "bgcolor" : clropt.get_value_as_html() } } })
        update(ssdoc.style,{"body" : { 'attribute' : { "bgcolor" : clropt.get_value_as_html() } } })

        bdropt = self.options.lookup_name('Tables','Table border width')
        padopt = self.options.lookup_name('Tables','Table cell padding')
        spcopt = self.options.lookup_name('Tables','Table cell spacing')
        update(ssdoc.style,{"table" : \
                   { 'attribute' : { "border" : str(bdropt.get_value()),
                                     "cellspacing" : str(spcopt.get_value()),
                                     "cellpadding" : str(padopt.get_value()),
                   } } })

        # new feature - setup default td styles
        update(ssdoc.style,{"td" : { "attribute" : { "rowspan" : "1", "colspan" : "1" }}})

        if ssdoc.doc.engine_supports_css:

            # for the moment this means webkit
            # this sets up the name column-heading-left to be replaced
            # with the html text when this name is seen in a report
            # note we define the key tag if the HTML tag name is different from the
            # style key name
            update(ssdoc.style,{"column-heading-left" : { "tag" : "th", "attribute" : { "class" : "column-heading-left" }}})
            update(ssdoc.style,{"column-heading-center" : { "tag" : "th", "attribute" : { "class" : "column-heading-center" }}})
            update(ssdoc.style,{"column-heading-right" : { "tag" : "th", "attribute" : { "class" : "column-heading-right" }}})
            update(ssdoc.style,{"date-cell" : { "tag" : "td", "attribute" : { "class" : "date-cell" }}})
            update(ssdoc.style,{"anchor-cell" : { "tag" : "td", "attribute" : { "class" : "anchor-cell" }}})
            update(ssdoc.style,{"number-cell" : { "tag" : "td", "attribute" : { "class" : "number-cell" }}})
            update(ssdoc.style,{"number-cell-neg" : { "tag" : "td", "attribute" : { "class" : "number-cell neg" }}})
            update(ssdoc.style,{"number-header" : { "tag" : "th", "attribute" : { "class" : "number-header" }}})
            update(ssdoc.style,{"text-cell" : { "tag" : "td", "attribute" : { "class" : "text-cell" }}})
            update(ssdoc.style,{"total-number-cell" : { "tag" : "td", "attribute" : { "class" : "total-number-cell" }}})
            update(ssdoc.style,{"total-number-cell-neg" : { "tag" : "td", "attribute" : { "class" : "total-number-cell neg" }}})
            update(ssdoc.style,{"total-label-cell" : { "tag" : "td", "attribute" : { "class" : "total-label-cell" }}})
            update(ssdoc.style,{"centered-label-cell" : { "tag" : "td", "attribute" : { "class" : "centered-label-cell" }}})

        else:
            # and this is the old gtkhtml
            pass

        update(ssdoc.style,{"normal-row" : { "tag" : "tr" } })

        altopt = self.options.lookup_name('Colors','Alternate Table Cell Color')
        update(ssdoc.style,{"alternate-row" : { "tag" : "tr" , "attribute" : { "bgcolor" : altopt.get_value_as_html() } } })

        update(ssdoc.style,{"primary-subheading" : { "tag" : "tr" , "attribute" : { "bgcolor" : clropt.get_value_as_html() } } })
        update(ssdoc.style,{"secondary-subheading" : { "tag" : "tr" , "attribute" : { "bgcolor" : clropt.get_value_as_html() } } })
        update(ssdoc.style,{"grand-total" : { "tag" : "tr" , "attribute" : { "bgcolor" : clropt.get_value_as_html() } } })

        # interesting - this shows how can use the scheme styles to totally ignore
        # an html tag
        # note that in this case the scheme style name is same as html tag name
        lnkopt = self.options.lookup_name('General','Enable Links')
        dolinks = lnkopt.get_value()
        if not dolinks:
            update(ssdoc.style,{"a" : { "tag" : "" }})

        # currently I think that the scheme styles were created before html had style sheets
        # eg css - now I think a lot of what the scheme style sheets used to do can be done 
        # with css styles
        # here we setup css styles for the style sheet

        self.add_css_information_to_doc(ssdoc)

        # in scheme the title and objects are copied from 
        # the passed document
        # cant do this here as dont have title in python implmentation
        #title = doc.title
        #headline = doc.headline
        #if not headline:
        #    headline = title

        # so have to add a dummy entry
        # - other stylesheets do much more complicated headers
        # MUST add to ssdoc as not added anything to doc
        # use special name to identify as header
        hdr = ssdoc.doc.HeaderElement("h3")

        return ssdoc
