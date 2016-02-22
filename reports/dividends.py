
import sys

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

from gnucash import ACCT_TYPE_INCOME

from gnucash import GNC_DENOM_AUTO, GNC_HOW_RND_ROUND, GNC_HOW_DENOM_REDUCE

from gnucash.gnucash_core_c import GNC_HOW_DENOM_SIGFIG

from gnucash import GncNumeric

import engine_ctypes

from qof_ctypes import gnc_print_date


class Dividends(ReportTemplate):

    def __init__ (self):

        super(Dividends,self).__init__()

        # need to set the  base variables
        self.version = 1
        self.name = N_("Dividends")
        self.report_guid = "f084309929f64d698f7c4155cd26a689"
        self.menu_path = N_("_Income & Expense")


    def options_generator (self):

        #pdb.set_trace()

        # need to instantiate the options database
        self.options = OptionsDB()

        self.options.add_date_interval('General', N_("Start Date"), N_("End Date"), "a")

        self.options.add_currency('General', N_("Report's currency"), "b")

        # should the list be a dict or not??
        self.options.add_price_source('General', N_("Price Source"), "c", 'pricedb-nearest')


        # this is how we should add options I think
        self.options.register_option(SimpleBooleanOption(N_("General"), N_("Show Exchange Rates"),"d",
                                                           N_("Show the exchange rates used."), False))

        self.options.register_option(SimpleBooleanOption(N_("General"), N_("Show Full Account Names"),"e",
                                                           N_("Show full account names (including parent accounts)."), True))

        self.options.add_account_selection('Accounts', N_("Account Display Depth"), N_("Always show sub-accounts"), N_("Account"), "a", '2', 
                      lambda : self.local_filter_accountlist_type(), False)

        self.options.set_default_section('General')

        return self.options

    @staticmethod
    def local_filter_accountlist_type ():
        #pdb.set_trace()
        accnts = sw_app_utils.get_current_root_account().get_descendants_sorted()
        #filter_accountlist_type([ACCT_TYPE_BANK, ACCT_TYPE_CASH, ACCT_TYPE_ASSET, ACCT_TYPE_STOCK, ACCT_TYPE_MUTUAL],get_descendants_sorted(sw_app_utils.get_current_root_account())), False)
        retacc = filter_accountlist_type([ACCT_TYPE_INCOME],accnts)
        return retacc

    @staticmethod
    def same_account (a1,a2):
        return (a1.GetGUID().compare(a2.GetGUID()) == 0)

    @staticmethod
    def same_split (s1,s2):
        return (s1.GetGUID().compare(s2.GetGUID()) == 0)

    @staticmethod
    def account_in_list (acnt,acclst):
        for acc in acclst:
            if Dividends.same_account(acnt,acc):
                return True
        return False

    @staticmethod
    def account_in_alist (acnt,alst):
        for acpr in alst:
            # scheme uses caar to access the list
            # but this seems right - acpr[0] is an account
            # ah - caar - access first element of list then first element of that first element
            if Dividends.same_account(acnt,acpr[0]):
                return acpr
        return None


    def renderer (self, report):

        # this actually implements the report look

        # for some reason if do this if any error occurs in report GUI is locked
        #report_starting(self.name)

        # lots of stuff about getting option values

        optobj = self.options.lookup_name('General','Start Date')
        from_date_tp = optobj.get_option_value()
        optobj = self.options.lookup_name('General','End Date')
        to_date_tp = optobj.get_option_value()

        #pdb.set_trace()

        # now for html creation
        # where do we actually instantiate the Html object

        # in scheme created new scheme html doc
        # in python probably should pass the report xml document 
        # does the possibility of having new HtmlDocument make sense??
        document = gnc_html_document.HtmlDocument(stylesheet=report.stylesheet())

        # temporary measure - set the document style
        # some this should be done auto by the stylesheet set
        # but the StyleTable is not currently stored in the stylesheet
        # or at least not the right one
        document.style = report.style

        optobj = self.options.lookup_name('General',"Report's currency")
        report_currency = optobj.get_value()
        optobj = self.options.lookup_name('General','Price Source')
        price_source = optobj.get_option_value()

        optobj = self.options.lookup_name('General','Show Full Account Names')
        show_full_names = optobj.get_value()

        optobj = self.options.lookup_name('Accounts','Account Display Depth')
        display_depth = optobj.get_option_value()

        rptopt = self.options.lookup_name('General','Report name')
        rptttl = rptopt.get_value() + " - " + N_("%s to %s"%(gnc_print_date(from_date_tp),gnc_print_date(to_date_tp)))
        document.title = rptttl

        accobj = self.options.lookup_name('Accounts','Account')
        accounts = accobj.get_option_value()

        shwobj = self.options.lookup_name('Accounts','Always show sub-accounts')
        shwopt = shwobj.get_value()

        print >> sys.stderr, "shwobj",shwobj,shwopt

        if shwopt:
            subacclst = get_all_subaccounts(accounts)
            for subacc in subacclst:
                if not Dividends.account_in_list(subacc,accounts):
                    accounts.append(subacc)

        #exchange_fn = gnc_commodity_utilities.case_exchange_fn(price_source, report_currency, to_date_tp)

        #pdb.set_trace()

        if len(accounts) > 0:

            if display_depth == 'all':
                tree_depth = self.accounts_get_children_depth(accounts)
            else:
                tree_depth = int(display_depth)

            #self.time_exchange_fn = gnc_commodity_utilities.case_exchange_time_fn(price_source, report_currency, commodity_list, to_date_tp, 0.0, 0.0)

            #pdb.set_trace()

            # need to figure out how to sort by full name
            # well this is useless - we need the account name!!
            accounts.sort(key=operator.methodcaller('GetName'))
            #self.money_in_accounts.sort(key=operator.methodcaller('GetName'))
            #self.money_out_accounts.sort(key=operator.methodcaller('GetName'))


            # find dividend accounts - junkily just look for name
            # - they have already been filtered for ACCT_TYPE_INCOME by default
            # - do we check again here??

            dividend_accounts = []

            for acc in accounts:
                if acc.get_current_depth() <= tree_depth:
                    accnm = acc.GetName()
                    if accnm.find('Dividend') >= 0 or accnm.find('dividend') >= 0:
                        if not Dividends.account_in_list(acc,dividend_accounts):
                            dividend_accounts.append(acc)
                            subacclst = get_all_subaccounts([acc])
                            for subacc in subacclst:
                                if not Dividends.account_in_list(subacc,dividend_accounts):
                                    dividend_accounts.append(subacc)
                    else:
                        parent = acc.get_parent()
                        prntnm = parent.GetName()
                        if prntnm.find('Dividend') >= 0 or prntnm.find('dividend') >= 0:
                            if not Dividends.account_in_list(acc,dividend_accounts):
                                dividend_accounts.append(acc)
                                subacclst = get_all_subaccounts([acc])
                                for subacc in subacclst:
                                    if not Dividends.account_in_list(subacc,dividend_accounts):
                                        dividend_accounts.append(subacc)


            base_text = document.StyleElement('body')
            base_text.text = N_("Selected Accounts")+"\n"
            base_text.tail = "\n"

            ultxt = document.doc.Element("ul")

            work_done = 0
            work_to_do = len(dividend_accounts)

            for acc in dividend_accounts:
                work_done += 1
                report_percent_done((work_done/float(work_to_do))*85.0)

                if acc.get_current_depth() <= tree_depth:

                    if show_full_names:
                        #accnm = acc.GetFullName()
                        accnm = acc.get_full_name()
                    else:
                        accnm = acc.GetName()
                    if acc.get_current_depth() == tree_depth and \
                        not len(acc.get_children()) == 0:
                        if shwopt:
                            acctxt = N_(" and subaccounts")
                        else:
                            acctxt = N_(" and selected subaccounts")
                    else:
                        acctxt = ""
                    accurl = gnc_html_utilities.account_anchor_text(acc)

                    anchor_li = document.doc.SubElement(ultxt,"li")

                    anchor_markup = document.doc.SubElement(anchor_li,"a")
                    anchor_markup.attrib['href'] = accurl
                    anchor_markup.text = N_(accnm) + "\n"
                    anchor_markup.tail = acctxt + "\n"


            do_accounts = []
            for acc in dividend_accounts:
                doacc = False
                for split in acc.GetSplitList():
                    parent = split.GetParent()
                    txn_date = parent.RetDatePostedTS()
                    if (txn_date >= from_date_tp.date() and txn_date <= to_date_tp.date()):
                        doacc = True
                if doacc:
                    do_accounts.append(acc)


            # Scheme uses a whole subclass of functions for dealing with
            # tables - indirectly creating all table elements
            # ignoring all this for now - just using CSS styles
            new_table = document.StyleElement('table')
            new_table.text = "\n"

            new_row = document.doc.SubElement(new_table,"tr")
            new_row.tail = "\n"
	    new_data = document.doc.SubElement(new_row,"td",attrib={'rowspan' : "1", 'colspan' : "2" })
            new_ruler = document.doc.SubElement(new_data,"hr")

            new_row = document.StyleSubElement(new_table,'primary-subheading')
            new_row.text = ""
            new_row.tail = "\n"

            #new_col = document.doc.SubElement(new_row,"td",attrib={'rowspan' : "1", 'colspan' : "1"})
            new_col = document.doc.SubElement(new_row,"td")
            new_col.text = N_("Dividend Account")

            new_col = document.doc.SubElement(new_row,"td")
            new_col.text = N_("Payment Date")

            new_col = document.doc.SubElement(new_row,"td")
            new_col.text = N_("Dividend Income")

            new_col = document.doc.SubElement(new_row,"td")
            new_col.text = N_("Exchange Rate")

            new_col = document.doc.SubElement(new_row,"td")
            new_col.text = N_("Report Currency")
            
            row_num = 0
            work_done = 0
            work_to_do = len(dividend_accounts)

            #pdb.set_trace()

            total_coll = CommodityCollector()
            total_rpt_coll = CommodityCollector()

            # this is bad - this assumes all dividends in single currency
            total_commod = None

            #for acc in dividend_accounts:
            for acc in do_accounts:

                row_num += 1
                work_done += 1
                report_percent_done((work_done/float(work_to_do))*5.0+90.0)

                if (row_num % 2) == 0:
                    new_row = document.StyleSubElement(new_table,'normal-row')
                else:
                    new_row = document.StyleSubElement(new_table,'alternate-row')

                new_row = document.StyleSubElement(new_table,'normal-row')
                new_row.text = "\n"
                new_row.tail = "\n"

                if show_full_names:
                    #accnm = acc.GetFullName()
                    accnm = acc.get_full_name()
                else:
                    accnm = acc.GetName()
                accurl = gnc_html_utilities.account_anchor_text(acc)

                new_col = document.doc.SubElement(new_row,"td")

                anchor_markup = document.doc.SubElement(new_col,"a")
                anchor_markup.attrib['href'] = accurl
                anchor_markup.text = accnm + "\n"

                acc_coll = CommodityCollector()
                acc_rpt_coll = CommodityCollector()

                for split in acc.GetSplitList():

                    parent = split.GetParent()
                    txn_date = parent.RetDatePostedTS()
                    commod_currency = parent.GetCurrency()
                    commod_currency_frac = commod_currency.get_fraction()

                    try:
                        other_split = split.GetOtherSplit()
                    except Exception, errexc:
                        other_split = None
                    print "other split for", other_split

                    #if other_split != None:
                    #    other_accnt = 

                    corr_accnm = split.GetCorrAccountName()
                    print "corr account", corr_accnm

                    # what do the functions eg GetCorrAccountName() do??
                    #

                    #if splt.GetAccount()

                    if (txn_date >= from_date_tp.date() and txn_date <= to_date_tp.date()):

                        row_num += 1

                        if (row_num % 2) == 0:
                            new_row = document.StyleSubElement(new_table,'normal-row')
                        else:
                            new_row = document.StyleSubElement(new_table,'alternate-row')

                        new_col = document.StyleSubElement(new_row,'text-cell')
                        new_col.text = N_(parent.GetDescription())

                        new_col = document.StyleSubElement(new_row,'text-cell')
                        new_col.text = N_(gnc_print_date(txn_date))

                        split_val = split.GetValue()

                        # we need to change the sign
                        split_val = split_val.neg()
 
                        # which is currency acc or other_acct??
                        #pdb.set_trace()

                        colval = gnc_commodity_utilities.GncMonetary(commod_currency,split_val)

                        new_col = document.StyleSubElement(new_row,'number-cell')
                        new_col.text = colval.to_currency_string()

                        # no easy way to get exchange rate
                        # - even in scheme do it by transforming an amount of 1
                        # actually uses 1000 to get the sig figs
                        # if no price we get none - make it 1
                        if not engine_ctypes.CommodityEquiv(commod_currency,report_currency):
                            prcval = GncNumeric(1000,1000)
                            prcmny = gnc_commodity_utilities.GncMonetary(commod_currency,prcval)
                            prcxch = gnc_commodity_utilities.exchange_by_pricedb_nearest(prcmny,report_currency,txn_date)
                            if prcxch == None:
                                prcxch = gnc_commodity_utilities.exchange_by_pricedb_latest(prcmny,report_currency)
                                if prcxch == None:
                                    prcxch = gnc_commodity_utilities.GncMonetary(report_currency,GncNumeric(1000,1000))
                            sclval = GncNumeric(1000,1000)
                            prcxch.amount = sclval.div(prcxch.amount,GNC_DENOM_AUTO,GNC_HOW_DENOM_SIGFIG | 6*256 | GNC_HOW_RND_ROUND)
                            #exch_rate = gnc_commodity_utilities.GncMonetary(report_currency,prcxch)
                            exch_rate = prcxch.amount
                        else:
                            #exch_rate = gnc_commodity_utilities.GncMonetary(report_currency,GncNumeric(1000,1000))
                            exch_rate = GncNumeric(1000,1000)


                        new_col = document.StyleSubElement(new_row,'number-cell')
                        #new_col.text = exch_rate.to_currency_string()
                        new_col.text = str(exch_rate.to_double())


                        if not engine_ctypes.CommodityEquiv(commod_currency,report_currency):
                            split_mny = gnc_commodity_utilities.GncMonetary(commod_currency,split_val)
                            splt_rpt = gnc_commodity_utilities.exchange_by_pricedb_nearest(split_mny,report_currency,txn_date)
                            if splt_rpt == None:
                                splt_rpt = gnc_commodity_utilities.exchange_by_pricedb_latest(split_mny,report_currency)
                                if splt_rpt == None:
                                    splt_rpt = gnc_commodity_utilities.GncMonetary(report_currency,GncNumeric(1000,1000))
                        else:
                            splt_rpt = gnc_commodity_utilities.GncMonetary(report_currency,split_val)

                        acc_coll.add(commod_currency, split_val)
                        total_coll.add(commod_currency, split_val)
                        acc_rpt_coll.add(splt_rpt.commodity, splt_rpt.amount)
                        total_rpt_coll.add(splt_rpt.commodity, splt_rpt.amount)

                        total_commod = commod_currency

                        colval = splt_rpt

                        new_col = document.StyleSubElement(new_row,'number-cell')
                        new_col.text = colval.to_currency_string()

                new_row = document.StyleSubElement(new_table,'normal-row')

                new_col = document.StyleSubElement(new_row,'text-cell')
                new_col.text = "Balance"

                new_col = document.StyleSubElement(new_row,'text-cell')
                new_col.text = ""

                #colval = gnc_commodity_utilities.GncMonetary(acc.GetCommodity(),acc.GetBalance().neg())
                colval = acc_coll.getmonetary(acc.GetCommodity())

                new_col = document.StyleSubElement(new_row,'number-cell')
                new_col.text = colval.to_currency_string()

                new_col = document.StyleSubElement(new_row,'text-cell')
                new_col.text = ""

                colval = acc_rpt_coll.getmonetary(report_currency)

                new_col = document.StyleSubElement(new_row,'number-cell')
                new_col.text = colval.to_currency_string()


                new_row = document.StyleSubElement(new_table,'normal-row')

                new_col = document.StyleSubElement(new_row,'text-cell')
                new_col.text = "Joint contribution"

                new_col = document.StyleSubElement(new_row,'text-cell')
                new_col.text = ""

                #colval = gnc_commodity_utilities.GncMonetary(acc.GetCommodity(),acc.GetBalance().neg())
                colval = acc_coll.getmonetary(acc.GetCommodity())
                colval.amount = colval.amount.div(GncNumeric(2,1),GNC_DENOM_AUTO,GNC_HOW_DENOM_SIGFIG | 5*256 | GNC_HOW_RND_ROUND)

                new_col = document.StyleSubElement(new_row,'number-cell')
                new_col.text = colval.to_currency_string()

                new_col = document.StyleSubElement(new_row,'text-cell')
                new_col.text = ""

                colval = acc_rpt_coll.getmonetary(report_currency)
                colval.amount = colval.amount.div(GncNumeric(2,1),GNC_DENOM_AUTO,GNC_HOW_DENOM_SIGFIG | 5*256 | GNC_HOW_RND_ROUND)

                new_col = document.StyleSubElement(new_row,'number-cell')
                new_col.text = colval.to_currency_string()


            if len(do_accounts) > 0:

                new_row = document.StyleSubElement(new_table,'normal-row')
                new_row.text = "\n"
                new_row.tail = "\n"

                new_data = document.doc.SubElement(new_row,"td",attrib={'rowspan' : "1", 'colspan' : "100%" })
                new_ruler = document.doc.SubElement(new_data,"hr")

                new_row = document.StyleSubElement(new_table,'grand-total')
                new_row.text = "\n"
                new_row.tail = "\n"

                new_col = document.StyleSubElement(new_row,'text-cell')
                new_col.text = N_("Total")

                new_col = document.StyleSubElement(new_row,'text-cell')
                new_col.text = " "

                colval = total_coll.getmonetary(total_commod)

                new_col = document.StyleSubElement(new_row,'total-number-cell')
                new_col.text = colval.to_currency_string()

                new_col = document.StyleSubElement(new_row,'text-cell')
                new_col.text = " "

                colval = total_rpt_coll.getmonetary(report_currency)

                new_col = document.StyleSubElement(new_row,'total-number-cell')
                new_col.text = colval.to_currency_string()


                new_row = document.StyleSubElement(new_table,'grand-total')
                new_row.text = "\n"
                new_row.tail = "\n"

                new_col = document.StyleSubElement(new_row,'text-cell')
                new_col.text = N_("Joint Contribution Total")

                new_col = document.StyleSubElement(new_row,'text-cell')
                new_col.text = " "

                colval = total_coll.getmonetary(total_commod)
                colval.amount = colval.amount.div(GncNumeric(2,1),GNC_DENOM_AUTO,GNC_HOW_DENOM_SIGFIG | 5*256 | GNC_HOW_RND_ROUND)

                new_col = document.StyleSubElement(new_row,'total-number-cell')
                new_col.text = colval.to_currency_string()

                new_col = document.StyleSubElement(new_row,'text-cell')
                new_col.text = " "

                colval = total_rpt_coll.getmonetary(report_currency)
                colval.amount = colval.amount.div(GncNumeric(2,1),GNC_DENOM_AUTO,GNC_HOW_DENOM_SIGFIG | 5*256 | GNC_HOW_RND_ROUND)

                new_col = document.StyleSubElement(new_row,'total-number-cell')
                new_col.text = colval.to_currency_string()



            #new_col = document.StyleSubElement(new_row,'text-cell')
            #new_col.text = N_("Money In")
            #new_col = document.StyleSubElement(new_row,'total-number-cell')
            #colval = self.money_in_collector.sum(report_currency, exchange_fn)
            #new_col.text = colval.to_currency_string()


        report_finished()

        return document

