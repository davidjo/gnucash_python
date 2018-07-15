

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

class MultiPriceScatter(ReportTemplate):

    def __init__ (self):

        # need to set the  base variables
        self.version = 1
        self.name = N_("MultiPrice")
        self.report_guid = "0C5629B16E374EE8A490213ABD8B6E86"
        self.menu_name = N_("Multi Price Scatterplot")
        # we have to define the tip
        self.menu_tip = N_("Multi Price Scatterplot")
        self.menu_path = N_("_Assets & Liabilities")

        # we cant do this because at the moment this object is a ReportTemplate
        # which is only instantiated once - different reports instantiate the Report
        # class multiple times but using the same ReportTemplate instance - the Report
        # class contains the specific options and call this ReportTemplate options_generator
        # and render functions
        #self.stocks = []
        #self.markers = []
        #self.markercolors = []


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
                                             

    def renderer (self, report):

        # this actually implements the report look

        #pdb.set_trace()

        # new idea - we store the plot data in the specific report object
        # - which fortunately we pass
        if report.report_data == None:
            class ReportData(object):
                pass
            report.report_data = ReportData()
            report.report_data.stocks = []
            report.report_data.markers = []
            report.report_data.markercolors = []

        stocks = report.report_data.stocks
        markers = report.report_data.markers
        markercolors = report.report_data.markercolors

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

        # this report does not set the title apparently deliberately
        #document.title = N_("Price Scatter")

        chart = gnc_html_scatter.HtmlMultiScatter()

        # Im seeing how this works in scheme report system
        # the scheme report system creates lists of entities to be added
        # now using one of the HTML/XML python modules to do this - why reinvent the wheel?
        # the only real issue is option replacement and links to
        # account pages

        # note that price-scatter.scm defines an option getting function
        # equivalent to the following python - we just split out the python
        #def get_option (section, name):
        #    optobj = self.options.lookup_name(section, name)
        #    return optobj.value()

        # the various plotting options

        #pdb.set_trace()

        optobj = self.options.lookup_name('General','Report name')
        chart.title = optobj.getter()

        optobj = self.options.lookup_name('Display','Plot Width')
        chart.width = optobj.getter()

        optobj = self.options.lookup_name('Display','Plot Height')
        chart.height = optobj.getter()

        optobj = self.options.lookup_name('General','Step Size')
        optstp = optobj.getter()
        mapinterval = { \
                      'DayDelta' : N_("Days"),
                      'WeekDelta' : N_("Weeks"),
                      'TwoWeekDelta' : N_("Double-Weeks"),
                      'MonthDelta' : N_("Months"),
                      'YearDelta' : N_("Years"),
                       }
        chart.x_axis_label = mapinterval[optstp]


        optobj = self.options.lookup_name('General','Start Date')
        strtdt = optobj.get_option_value()

        optobj = self.options.lookup_name('General','End Date')
        enddt = optobj.get_option_value()


        commod_table = sw_app_utils.get_current_commodities()

        cur = commod_table.lookup('CURRENCY', 'USD')

        optobj = self.options.lookup_name('Price','Price of Commodity')
        stock = optobj.getter()

        optobj = self.options.lookup_name('Price','Invert prices')
        optinv = optobj.getter()
        # disable this optinv option - dont really understand it
        #if optinv:
        #    chart.y_axis_label = stock.get_mnemonic()
        #else:
        #    chart.y_axis_label = cur.get_mnemonic()
        chart.y_axis_label = cur.get_mnemonic()


        optobj = self.options.lookup_name('Display','Marker')
        #chart.marker = optobj.get_option_value()
        marker = optobj.get_option_value()

        optobj = self.options.lookup_name('Display','Marker Color')
        optclr = optobj.getter()
        #chart.markercolor = "%2x%2x%2x"%(optclr[0],optclr[1],optclr[2])
        markercolor = "%2x%2x%2x"%(optclr[0],optclr[1],optclr[2])


        # update stock list if changed - otherwise assume plot options changing
        stock_updated = False
        if len(stocks) > 0 :

            pdb.set_trace()

            # ignore namespace for the moment??
            if stocks[-1].get_namespace() != stock.get_namespace() or \
                 stocks[-1].get_mnemonic() != stock.get_mnemonic():

                stocks.append(stock)
                markers.append(marker)
                markercolors.append(markercolor)
                stock_updated = True

        else:

            stocks.append(stock)
            markers.append(marker)
            markercolors.append(markercolor)
            stock_updated = True


        #chart.subtitle = "%s"%chart_sym + " - " + "%s to %s"%(strtdt.strftime("%m/%d/%Y"),enddt.strftime("%m/%d/%Y"))
        chart.subtitle = "%s to %s"%(strtdt.strftime("%m/%d/%Y"),enddt.strftime("%m/%d/%Y"))

        doplot = True

        if len(stocks) == 1:

            # this tests the same namespace and mnemonic same
            #if gnc_commodity_eqiv(stock,cur):
            if stocks[0].get_namespace() == cur.get_namespace() and \
                 stocks[0].get_mnemonic() == cur.get_mnemonic():

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

                document.doc.docobj.append(docelm)

                # need to reset any stored data!!
                report.report_data.stocks = []
                report.report_data.markers = []
                report.report_data.markercolors = []

                doplot = False

        if doplot:

            # this is junky emulation of the gnc:deltasym-to-delta scheme function
            # this just converts the deltas to seconds - so have a simple linear x time scale
            # gnc:deltasym-to-delta converts to actual date time structure - so should
            # probably use datetime here
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

            for istock,stock in enumerate(stocks):

                marker = markers[istock]
                markercolor = markercolors[istock]

                # disable this - dont really understand this option yet
                #if optinv:
                #    chart_sym = cur.get_mnemonic()
                #else:
                #    chart_sym = stock.get_mnemonic()
                chart_sym = stock.get_mnemonic()

                prclst = prcdb.get_prices(stock,cur)

                if len(prclst) <= 0:
                    print("Warning: no prices for stock",chart_sym)
                    chart.add_data([], marker, markercolor, label=chart_sym)
                    continue

                #pdb.set_trace()

                prcordr = []
                for prc in prclst:
                    prcdt = prc.get_time64().date()
                    if prcdt >= strtdt.date() and prcdt <= enddt.date():
                        prcordr.append((float(prcdt.strftime("%s")),prc))
                prcordr.sort()

                datalst = []

                if len(prcordr) > 0:

                    prclst0 = prcordr[0][1]
                    prcdt = prclst0.get_time64().date()
                    prcdt0 = float(prcdt.strftime("%s"))

                    for prctm,prc in prcordr:
                        prcobj = prc.get_value()
                        #rlprc = float(prcobj.num)/prcobj.denom
                        rlprc = prcobj.to_double()

                        # we need to convert the date to seconds
                        cnvdt = (prctm-prcdt0)/mapxscale[optstp]

                        #chart.add_datapoint((cnvdt,rlprc))
                        datalst.append((cnvdt,rlprc))

                else:

                    print("Warning: no prices for stock in date range",chart_sym)

                # for multi price scatter we add 
                chart.add_data(datalst, marker, markercolor, label=chart_sym)

            pdb.set_trace()

            docelm = chart.render()

            #document.doc.docobj = docelm
            document.doc.docobj.append(docelm)

            stdelm = ET.Element('p')
            stdelm.text = "Start Date %s"%str(strtdt)
            docelm.append(stdelm)

            endelm = ET.Element('p')
            endelm.text = "End Date %s"%str(enddt)
            docelm.append(endelm)

        return document
