 
import operator

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

# this is an attempt at replicating the Investment Portfolio scheme report

import sw_app_utils

# partial implementation mainly for URL handlers
import gnc_html_ctypes

# we need to subclass something - but what??
# Im thinking this is ReportTemplate

#import gnc_html_document_full
import gnc_html_document

from report_objects import ReportTemplate

from gnc_report_utilities import CommodityCollector
from gnc_report_utilities import filter_accountlist_type
from gnc_report_utilities import accounts_count_splits
from gnc_report_utilities import report_starting,report_percent_done,report_finished
from gnc_report_utilities import get_all_subaccounts
from gnc_report_utilities import get_commodities
from gnc_report_utilities import account_get_comm_balance_at_date

import gnc_commodity_utilities

import gnc_html_utilities

from qof_ctypes import gnc_print_date

# maybe store the class in ReportTemplate then dont need this import
# yes we need a better way to handle this so dont need all these includes
from report_objects import OptionsDB
#from report_options import BooleanOption
#from report_options import MultiChoiceOption
# lets try importing all
from report_options import *


import gnucash

from gnucash import ACCT_TYPE_STOCK, ACCT_TYPE_MUTUAL


class Portfolio(ReportTemplate):

    def __init__ (self):

        super(Portfolio,self).__init__()

        # need to set the  base variables
        self.version = 1
        self.name = N_("Investment Portfolio")
        self.report_guid = "dfd1064ef84a4572b56d7bc1ee3f3c78"
        self.menu_path = N_("_Assets & Liabilities")


    def options_generator (self):

        #pdb.set_trace()

        # need to instantiate the options database
        self.options = OptionsDB()

        self.options.add_report_date('General', N_("Date"), "a")

        self.options.add_currency('General', N_("Report's currency"), "c")

        # should the list be a dict or not??
        self.options.add_price_source('General', N_("Price Source"), "d", 'pricedb-latest')


        # this is how we should add options I think
        self.options.register_option(NumberRangeOption(N_("General"), N_("Share decimal places"),"e",
                                                           N_("The number of decimal places to use for share numbers."), 2, 0, 6, 0, 1))


        self.options.register_option(AccountListOption(N_("Accounts"), N_("Accounts"), "b",
                                                N_("Stock Accounts to report on."), lambda : self.local_filter_accountlist_type(), lambda accounts: self.local_account_validator(accounts), True))

        #self.options.add_account_selection('Accounts', N_("Account Display Depth"), N_("Always show sub-accounts"), N_("Account"), "a", '2', 
        #              lambda : self.local_filter_accountlist_type(), False)


        self.options.register_option(SimpleBooleanOption(N_("Accounts"), N_("Include accounts with no shares"),"e",
                                                           N_("Include accounts that have a zero share balances."), False))

        #self.options.register_option(SimpleBooleanOption(N_("General"), N_("Show Exchange Rates"),"d",
        #                                                   N_("Show the exchange rates used."), False))

        #self.options.register_option(SimpleBooleanOption(N_("General"), N_("Show Full Account Names"),"e",
        #                                                   N_("Show full account names (including parent accounts)."), True))


        self.options.set_default_section('General')

        return self.options

    @staticmethod
    def local_filter_accountlist_type ():
        #pdb.set_trace()
        accnts = sw_app_utils.get_current_root_account().get_descendants_sorted()
        retacc = filter_accountlist_type([ACCT_TYPE_STOCK, ACCT_TYPE_MUTUAL],accnts)
        return retacc

    @staticmethod
    def local_account_validator (accounts):
        pdb.set_trace()
        retacc = filter_accountlist_type([ACCT_TYPE_STOCK, ACCT_TYPE_MUTUAL],accounts)
        return (True, retacc)


    @staticmethod
    def account_in_list (acnt,acclst):
        for acc in acclst:
            if Portfolio.same_account(acnt,acc):
                return True
        return False

    @staticmethod
    def account_in_alist (acnt,alst):
        for acpr in alst:
            # scheme uses caar to access the list
            # but this seems right - acpr[0] is an account
            # ah - caar - access first element of list then first element of that first element
            if Portfolio.same_account(acnt,acpr[0]):
                return acpr
        return None

    def table_add_stock_rows (self, accounts, to_date_tp, from_date_tp, report_currency, exchange_fn, price_fn, include_empty, collector):

        optobj = self.options.lookup_name('General','Share decimal places')
        num_places = optobj.get_option_value()
        share_print_info = sw_app_utils.SharePrintInfoPlaces(num_places)

        work_to_do = len(accounts)
        work_done = 0

        for row,curacc in enumerate(accounts):

            print "account",curacc.GetName(),curacc

            if (row % 2) == 0:
                new_row = self.document.StyleSubElement(self.new_table,'normal-row')
            else:
                new_row = self.document.StyleSubElement(self.new_table,'alternate-row')
            new_row.text = "\n"
            new_row.tail = "\n"

            commod = curacc.GetCommodity()

            #pdb.set_trace()
            ticker_symbol = commod.get_mnemonic()
            listing = commod.get_namespace()

            unit_collector = account_get_comm_balance_at_date(curacc, to_date_tp)

            units = unit_collector.getpair(commod)[1]

            print "units",units.to_string()

            price_info = price_fn(commod,to_date_tp)

            price = price_info[0]

            if price:
                price_monetary = gnc_commodity_utilities.GncMonetary(price.get_currency(),price.get_value())
            else:
                price_monetary = gnc_commodity_utilities.GncMonetary(report_currency,price_info[1])

            value = exchange_fn.run(gnc_commodity_utilities.GncMonetary(commod,units),report_currency)


            work_done += 1

            report_percent_done((work_done/float(work_to_do))*100.0)

            #def to_report_currency (curr, amnt, date):
            #    #pdb.set_trace()
            #    retval = self.time_exchange_fn.run(gnc_commodity_utilities.GncMonetary(curr, amnt), report_currency, date).amount
            #    return retval

            #pdb.set_trace()


            # how to do test against 0 for GncNumeric??
            if include_empty or not units.zero_p():

                collector.add(report_currency,value.amount)

                # scheme appends row here
                #self.table.append_row(row_style,[list of columns])

                new_col = self.document.doc.SubElement(new_row,"td")

                # the following does gnc:html-account-anchor
                accurl = gnc_html_utilities.account_anchor_text(curacc)

                anchor_markup = self.document.doc.SubElement(new_col,"a")
                anchor_markup.attrib['href'] = accurl
                anchor_markup.text = N_(curacc.GetName()) + "\n"
                anchor_markup.tail = "\n"


                new_col = self.document.StyleSubElement(new_row,'text-cell')
                new_col.text = ticker_symbol
                new_col.tail = "\n"

                new_col = self.document.StyleSubElement(new_row,'text-cell')
                new_col.text = listing
                new_col.tail = "\n"

                new_col = self.document.StyleSubElement(new_row,'number-cell')
                new_col.text = sw_app_utils.PrintAmount(units,share_print_info)
                new_col.tail = "\n"

                new_col = self.document.StyleSubElement(new_row,'number-cell')
                new_col.tail = "\n"

                # this does gnc:html-price-anchor
                prcurl = gnc_html_utilities.price_anchor_text(price)

                anchor_markup = self.document.doc.SubElement(new_col,"a")
                anchor_markup.attrib['href'] = prcurl
                anchor_markup.text = price_monetary.to_currency_string()
                anchor_markup.tail = "\n"


                new_col = self.document.StyleSubElement(new_row,'number-cell')
                new_col.text = value.to_currency_string()
                new_col.tail = "\n"



    # these functions are local to renderer function in scheme

    def average_fn (self, foreign, date):

        #pdb.set_trace()
        # exchange_fn and currency are globals in scheme

        tmpval = self.exchange_fn(gnc_commodity_utilities.GncMonetary(foreign,gnucash.GncNumeric(10000,1)),report_currency).amount

        tmpval.div(gnucash.GncNumeric(10000,1),GNC_DENOM_AUTO,GNC_HOW_DENOM_SIGFIG | 5*256 | GNC_HOW_RND_ROUND)

        return (None,tmpval)

    def price_db_latest_fn (self, foreign, date):

        #pdb.set_trace()

        price = self.pricedb.lookup_latest_any_currency(foreign)

        if len(price) > 0:
            v = price[0].get_value()
            return (price[0],v)
        else:
            return (None,gnucash.GncNumeric(0))

    def price_db_nearest_fn (self, foreign, date):

        #pdb.set_trace()

        #price = self.pricedb.lookup_nearest_in_time_any_currency(foreign,timespecCanonicalDayTime(date))
        price = self.pricedb.lookup_nearest_in_time_any_currency(foreign,date)

        if len(price) > 0:
            v = price[0].get_value()
            return (price[0],v)
        else:
            return (None,gnucash.GncNumeric(0))


    def renderer (self, report):

        # this actually implements the report look

        # for some reason if do this if any error occurs in report GUI is locked
        #report_starting(self.name)

        #pdb.set_trace()

        # get local values for options

        optobj = self.options.lookup_name('General','Date')
        to_date_tp = optobj.get_option_value()

        #optobj = self.options.lookup_name('General','Start Date')
        #from_date_tp = optobj.get_option_value()
        #optobj = self.options.lookup_name('General','End Date')
        #to_date_tp = optobj.get_option_value()

        from_date_tp = None

        accobj = self.options.lookup_name('Accounts','Accounts')
        accounts = accobj.get_option_value()

        optobj = self.options.lookup_name('General',"Report's currency")
        report_currency = optobj.get_value()

        rptopt = self.options.lookup_name('General','Report name')
        rptttl = rptopt.get_value()

        optobj = self.options.lookup_name('General','Price Source')
        price_source = optobj.get_option_value()

        incobj = self.options.lookup_name('Accounts','Include accounts with no shares')
        include_empty = incobj.get_value()


        #optobj = self.options.lookup_name('General','Show Full Account Names')
        #show_full_names = optobj.get_value()

        #optobj = self.options.lookup_name('Accounts','Account Display Depth')
        #display_depth = optobj.get_option_value()

        #shwobj = self.options.lookup_name('Accounts','Always show sub-accounts')
        #shwopt = shwobj.get_value()
        #if shwopt:
        #    subacclst = get_all_subaccounts(accounts)
        #    for subacc in subacclst:
        #        if not Portfolio.account_in_list(subacc,accounts):
        #            accounts.append(subacc)


        #self.money_in_alist = []
        #self.money_in_accounts = []
        self.collector = CommodityCollector()


        # now for html creation
        # where do we actually instantiate the Html object

        # in scheme created new scheme html doc
        # in python probably should pass the report xml document 
        # does the possibility of having new HtmlDocument make sense??
        self.document = gnc_html_document.HtmlDocument(stylesheet=report.stylesheet())

        # temporary measure - set the document style
        # some this should be done auto by the stylesheet set
        # but the StyleTable is not currently stored in the stylesheet
        # or at least not the right one
        self.document.style = report.style

        #document.title = rptttl + " - " + N_("%s to %s"%(gnc_print_date(from_date_tp),gnc_print_date(to_date_tp)))
        self.document.title = rptttl + " " + N_("%s"%(gnc_print_date(to_date_tp)))

        # Scheme uses a whole subclass of functions for dealing with
        # tables - indirectly creating all table elements
        # ignoring all this for now - just using CSS styles
        #self.table = HtmlTable()
        self.new_table = self.document.StyleElement('table')
        self.new_table.text = "\n"

        colhdrlst = [N_("Account"),N_("Symbol"),N_("Listing"),N_("Units"),N_("Price"),N_("Value")]
        #self.table.set_col_headers(colhdrlst)

        new_row = self.document.doc.SubElement(self.new_table,"tr")
        new_row.tail = "\n"
        for colhdr in colhdrlst:
	    new_hdr = self.document.doc.SubElement(new_row,"th",attrib={'rowspan' : "1", 'colspan' : "1" })
            new_hdr.text = colhdr
            new_hdr.tail = "\n"

        #pdb.set_trace()

        if len(accounts) > 0:

            # the following 2 lines seem to have no use
            # - commodity_list does not appear to be used anywhere??
            subacclst = get_all_subaccounts(accounts)

            # remove report currency from list
            commodity_list = get_commodities(accounts+subacclst,report_currency)

            book = sw_app_utils.get_current_book()
            self.pricedb = book.get_price_db()

            self.exchange_fn = gnc_commodity_utilities.case_exchange_fn(price_source, report_currency, to_date_tp)

            if price_source == 'average-cost':
                price_fn = self.average_fn
            elif price_source == 'weighted-average':
                price_fn = self.average_fn
            elif price_source == 'pricedb-latest':
                price_fn = self.price_db_latest_fn
            elif price_source == 'pricedb-nearest':
                price_fn = self.price_db_nearest_fn

            self.table_add_stock_rows(accounts, to_date_tp, from_date_tp, report_currency, self.exchange_fn, price_fn, include_empty, self.collector)


            #(gnc:make-html-table-cell/size 1 6 (gnc:make-html-text (gnc:html-markup-hr)))
            # this is labelled grand-total for some reason - just draws a line
            new_row = self.document.doc.SubElement(self.new_table,"tr")
            new_row.tail = "\n"
	    new_data = self.document.doc.SubElement(new_row,"td",attrib={'rowspan' : "1", 'colspan' : "6" })
            new_ruler = self.document.doc.SubElement(new_data,"hr")

            def total_func (currency, amount):
                #pdb.set_trace()
                new_row = self.document.doc.SubElement(self.new_table,"tr")
                new_row.text = "\n"
                new_row.tail = "\n"
                new_col = self.document.StyleSubElement(new_row,'total-label-cell')
                new_col.text = N_("Total")
                new_col = self.document.StyleSubElement(new_row,'total-number-cell',attrib={'rowspan' : "1", 'colspan' : "5"})
                new_col.text = gnc_commodity_utilities.GncMonetary(currency,amount).to_currency_string()
                new_col.tail = "\n"

            self.collector.format(total_func)

        report_finished()

        return self.document

