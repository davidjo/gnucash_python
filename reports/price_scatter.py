

# how to do internationalization in python
#import gettext
#gettext.bindtextdomain('myapplication', '/path/to/my/language/directory')
#gettext.textdomain('myapplication')
#_ = gettext.gettext

# dummy function for internationalization
def N_(msg):
    return msg


import xml.etree.ElementTree as ET


import sw_app_utils
import sw_core_utils

import gnc_html_scatter

import gnc_html_document


# this is an attempt at replicating the Price Scatter scheme report

from report_objects import ReportTemplate

# maybe store the class in ReportTemplate then dont need this import
# yes we need a better way to handle this so dont need all these includes
from report_objects import OptionsDB
#from report_options import BooleanOption
#from report_options import MultiChoiceOption
# lets try importing all
from report_options import *

class PriceScatter(ReportTemplate):

    def __init__ (self):

        # need to set the  base variables
        self.version = 1
        self.name = N_("Price")
        self.report_guid = "F087F0A8BC4F4FA785403BA761714043"
        self.menu_name = N_("Price Scatterplot")
        # we have to define the tip
        self.menu_tip = N_("Price Scatterplot")
	self.menu_path = N_("_Assets & Liabilities")


    def options_generator (self):

        # need to instantiate the options database
        self.options = OptionsDB()

        self.options.add_date_interval('General', N_("Start Date"), N_("End Date"), "a")

        self.options.add_interval_choice('General', N_("Step Size"), "b", 'MonthDelta')

        self.options.add_currency('Price', N_("Report's currency"), "d")

        self.options.register_option(CommodityOption('Price', N_("Price of Commodity"),"e",
                                         N_("Calculate the price of this commodity."),
                                            sw_core_utils.gnc_locale_default_iso_currency_code()))

        # should the list be a dict or not??
        self.options.register_option(MultiChoiceOption('Price', N_("Price Source"),"f",
                                                         N_("The source of price information."),
                                                         'actual-transactions',
                                                         [ \
                                                         [ 'weighted-average', N_("Weighted Average."), N_("The weighted average of all currency transactions of the past.") ],
                                                         [ 'actual-transactions', N_("Actual Transactions"), N_("The instantaneous price of actual currency transactions in the past.") ],
                                                         [ 'pricedb', N_("Price Database"), N_("The recorded prices.") ],
                                                         ]))

        self.options.register_option(SimpleBooleanOption('Price', N_("Invert prices"),"g",
                                                           N_("Plot commodity per currency rather than currency per commodity."), False))

        self.options.add_plot_size('Display', N_("Plot Width"), N_("Plot Height"), "c", 500, 400)

        self.options.add_marker_choice('Display', N_("Marker"), "a", 'filledsquare')

        self.options.register_option(ColorOption('Display', N_("Marker Color"), "b", N_("Color of the marker."),
                                                   (0xb2, 0x22, 0x22, 0), 255, False))


        # we need to set the default option section - the one selected
        # gnc:options-set-default-section options "General"

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

        document.title = N_("Price Scatter")

        chart = gnc_html_scatter.HtmlScatter()

        # Im seeing how this works in scheme report system
        # the scheme report system creates lists of entities to be added
        # now using one of the HTML/XML python modules to do this - why reinvent the wheel?
        # the only real issue is option replacement and links to
        # account pages

        # the various plotting options

        #pdb.set_trace()

        optobj = self.options.lookup_name('General','Report name')
        chart.title = optobj.getter()

        optobj = self.options.lookup_name('Display','Plot Width')
        chart.width = optobj.getter()

        optobj = self.options.lookup_name('Display','Plot Height')
        chart.height = optobj.getter()

        optobj = self.options.lookup_name('General','Step Size')
        optstp = optobj.option_data[optobj.getter()][0]
        mapinterval = { \
                      'DayDelta' : N_("Days"),
                      'WeekDelta' : N_("Weeks"),
                      'TwoWeekDelta' : N_("Double-Weeks"),
                      'MonthDelta' : N_("Months"),
                      'YearDelta' : N_("Years"),
                       }
        chart.x_axis_label = mapinterval[optstp]

        optobj = self.options.lookup_name('Display','Marker')
        chart.marker = optobj.get_option_value()

        optobj = self.options.lookup_name('Display','Marker Color')
        optclr = optobj.getter()
        chart.markercolor = "%2x%2x%2x"%(optclr[0],optclr[1],optclr[2])


        commod_table = sw_app_utils.get_current_commodities()

        cur = commod_table.lookup('CURRENCY', 'USD')

        optobj = self.options.lookup_name('Price','Price of Commodity')
        stock = optobj.getter()

        optobj = self.options.lookup_name('Price','Invert prices')
        optinv = optobj.getter()
        if optinv:
            chart.y_axis_label = stock.get_mnemonic()
        else:
            chart.y_axis_label = cur.get_mnemonic()

        optobj = self.options.lookup_name('General','Start Date')
        strtdt = optobj.get_option_value()

        optobj = self.options.lookup_name('General','End Date')
        enddt = optobj.get_option_value()


        # this tests the same namespace and mnemonic same
        #if gnc_commodity_eqiv(stock,cur):
        if stock.get_namespace() != cur.get_namespace() or \
             stock.get_mnemonic() != cur.get_mnemonic():

            mapxscale = { \
                        'DayDelta' : 86400.0,
                        'WeekDelta' : 604800.0,
                        'TwoWeekDelta' : 1209600.0,
                        'MonthDelta' : 2628000.0,
                        'YearDelta' : 31536000.0,
                        }

            #
            book = sw_app_utils.get_current_book()
            prcdb = book.get_price_db()
            prclst = prcdb.get_prices(stock,cur)

            #pdb.set_trace()

            prcordr = []
            for prc in prclst:
                prcdt = prc.get_time()
                if prcdt >= strtdt.date() and prcdt <= enddt.date():
                    prcordr.append((float(prcdt.strftime("%s")),prc))
            prcordr.sort()

            prclst0 = prcordr[0][1]
            prcdt = prclst0.get_time()
            prcdt0 = float(prcdt.strftime("%s"))

            for prctm,prc in prcordr:
                prcobj = prc.get_value()
                rlprc = float(prcobj.num)/prcobj.denom

                # we need to convert the date to seconds
                cnvdt = (prctm-prcdt0)/mapxscale[optstp]

                chart.add_datapoint((cnvdt,rlprc))

            docelm = chart.render()

            stdelm = ET.Element('p')
            stdelm.text = "Start Date %s"%str(strtdt)
            docelm.append(stdelm)

            endelm = ET.Element('p')
            endelm.text = "End Date %s"%str(enddt)
            docelm.append(endelm)

        else:

            #docstr = "<h2>"+N_("Identical commodities")+"</h2>"
            #docstr += "<p>"+N_("Your selected commodity and the currency of the report \
#are identical. It doesn't make sense to show prices for identical \
#commodities.")+"</p>"
            #doclst = [docstr]
            docelm = ET.Element('div',attrib={'id' : 'scatter1'})
            docobj = ET.SubElement(docelm,'h2')
            docobj.text = N_("Identical commodities")
            newelm = ET.SubElement(docelm,'p')
            newelm.text = N_("Your selected commodity and the currency of the report \
are identical. It doesn't make sense to show prices for identical \
commodities.")

        return docelm
