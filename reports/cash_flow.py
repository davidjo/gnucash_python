
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

# this is an attempt at replicating the Cash Flow scheme report

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

from gnucash import ACCT_TYPE_BANK, ACCT_TYPE_CASH, ACCT_TYPE_ASSET, ACCT_TYPE_STOCK, ACCT_TYPE_MUTUAL


class CashFlow(ReportTemplate):

    def __init__ (self):

        super(CashFlow,self).__init__()

        # need to set the  base variables
        self.version = 1
        self.name = N_("Cash Flow")
        self.report_guid = "f8748b813fab4220ba26e743aedf38da"
        self.menu_path = N_("_Income & Expense")

        self.money_in_alist = []
        self.money_in_accounts = []
        self.money_in_collector = CommodityCollector()

        self.money_out_alist = []
        self.money_out_accounts = []
        self.money_out_collector = CommodityCollector()


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
        retacc = filter_accountlist_type([ACCT_TYPE_BANK, ACCT_TYPE_CASH, ACCT_TYPE_ASSET, ACCT_TYPE_STOCK, ACCT_TYPE_MUTUAL],accnts)
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
            if CashFlow.same_account(acnt,acc):
                return True
        return False

    @staticmethod
    def account_in_alist (acnt,alst):
        for acpr in alst:
            # scheme uses caar to access the list
            # but this seems right - acpr[0] is an account
            # ah - caar - access first element of list then first element of that first element
            if CashFlow.same_account(acnt,acpr[0]):
                return acpr
        return None

    def calc_money_in_out (self, accounts, to_date_tp, from_date_tp, report_currency):

        # follow the scheme
        def split_in_list (split,splits):
            #pdb.set_trace()
            if len(splits) <= 0:
                return False
            for splt in splits:
                if CashFlow.same_split(splt,split):
                    return True
            return False

        def to_report_currency (curr, amnt, date):
            #pdb.set_trace()
            retval = self.time_exchange_fn.run(gnc_commodity_utilities.GncMonetary(curr, amnt), report_currency, date).amount
            return retval

        #pdb.set_trace()

        splits_to_do = accounts_count_splits(accounts)

        work_done = 0

        for acc in accounts:

            name = acc.GetName()
            curcmd = acc.GetCommodity()
            seen_split_list = []

            for splt in acc.GetSplitList():

                work_done += 1
                report_percent_done((work_done/float(splits_to_do))*85.0)

                prnt = splt.GetParent()
                prnt_date_posted = prnt.GetDatePostedGDate()

                # course scheme inverts things
                #if prnt_date_posted <= to_date_tp and prnt_date_posted >= from_date_tp:
                if prnt_date_posted >= from_date_tp.date() and prnt_date_posted <= to_date_tp.date():
                    #pdb.set_trace()
                    parent_currency = prnt.GetCurrency()
                    trnval = gnucash.GncNumeric(0)
                    spltval = splt.GetValue()

                    trnsplts = prnt.GetSplitList()

                    for trnsplt in trnsplts:
                        psv = trnsplt.GetValue()
                        if psv.positive_p():
                            trnval = trnval.add(psv,gnucash.GNC_DENOM_AUTO,gnucash.GNC_HOW_DENOM_LCD)

                    for trnsplt in trnsplts:

                        s_acc = trnsplt.GetAccount()
                        s_val = trnsplt.GetValue()
                        s_cmd = s_acc.GetCommodity()
                        #print "split acc",s_acc.GetName(),s_val.to_string()
                        #print "split acc in",CashFlow.account_in_list(s_acc,accounts)

                        if s_acc == None:
                            print "WARNING: s-account is NULL for split: %s",trnsplt.GetGUID() 

                        if s_acc != None and \
                           not CashFlow.account_in_list(s_acc,accounts) \
                            and s_val.mul(spltval,gnucash.GNC_DENOM_AUTO,gnucash.GNC_HOW_DENOM_REDUCE).negative_p():
                            if not split_in_list(trnsplt,seen_split_list):
                                if trnval.zero_p():
                                    split_trans_ratio = gnucash.GncNumeric(1,1)
                                else:
                                    split_trans_ratio = spltval.div(trnval,gnucash.GNC_DENOM_AUTO,gnucash.GNC_HOW_DENOM_REDUCE).abs()
                                #s_val = split_trans_ratio.mul(s_val,parent_currency.get_fraction)
                                pfrc = parent_currency.get_fraction()
                                s_upd = split_trans_ratio.mul(s_val,pfrc,gnucash.GNC_HOW_RND_ROUND)
                                s_val = s_upd

                                seen_split_list.append(trnsplt)

                                if s_val.negative_p():

                                    pair = CashFlow.account_in_alist(s_acc, self.money_in_alist)
                                    if pair == None:
                                        pair = [ s_acc, CommodityCollector() ]
                                        self.money_in_alist.append(pair)
                                        self.money_in_accounts.append(s_acc)
                                    s_acc_in_collector = pair[1]
                                    s_report_value = to_report_currency(parent_currency, s_val.neg(), prnt_date_posted)
                                    self.money_in_collector.add(report_currency, s_report_value)
                                    s_acc_in_collector.add(report_currency, s_report_value)

                                else:

                                    pair = CashFlow.account_in_alist(s_acc, self.money_out_alist)
                                    if pair == None:
                                        pair = [ s_acc, CommodityCollector() ]
                                        self.money_out_alist.append(pair)
                                        self.money_out_accounts.append(s_acc)
                                    s_acc_out_collector = pair[1]
                                    s_report_value = to_report_currency(parent_currency, s_val, prnt_date_posted)
                                    self.money_out_collector.add(report_currency, s_report_value)
                                    s_acc_out_collector.add(report_currency, s_report_value)

                                #print "add val",s_report_value.to_string()


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
        if shwopt:
            subacclst = get_all_subaccounts(accounts)
            for subacc in subacclst:
                if not CashFlow.account_in_list(subacc,accounts):
                    accounts.append(subacc)

        exchange_fn = gnc_commodity_utilities.case_exchange_fn(price_source, report_currency, to_date_tp)

        #pdb.set_trace()

        if len(accounts) > 0:

            if display_depth == 'all':
                tree_depth = self.accounts_get_children_depth(accounts)
            else:
                tree_depth = int(display_depth)

            account_disp_list = []

            money_diff_collector = CommodityCollector()

            commodity_list = []

            self.time_exchange_fn = gnc_commodity_utilities.case_exchange_time_fn(price_source, report_currency, commodity_list, to_date_tp, 0.0, 0.0)

            self.money_in_alist = []
            self.money_in_accounts = []
            self.money_in_collector = CommodityCollector()
            self.money_out_alist = []
            self.money_out_accounts = []
            self.money_out_collector = CommodityCollector()

            self.calc_money_in_out(accounts,to_date_tp,from_date_tp, report_currency)

            #pdb.set_trace()

            # in scheme there is a second argument generally False
            # I think this is because there are in general 2 arguments (collector, value)
            # to these functions but I think the merge function only uses the collector
            money_diff_collector.merge(self.money_in_collector)
            money_diff_collector.minusmerge(self.money_out_collector)

            # need to figure out how to sort by full name
            # well this is useless - we need the account name!!
            accounts.sort(key=operator.methodcaller('GetName'))
            self.money_in_accounts.sort(key=operator.methodcaller('GetName'))
            self.money_out_accounts.sort(key=operator.methodcaller('GetName'))

            base_text = document.StyleElement('body')
            base_text.text = N_("Selected Accounts")+"\n"
            base_text.tail = "\n"

            ultxt = document.doc.Element("ul")


            work_done = 0
            work_to_do = len(accounts)

            for acc in accounts:
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
            new_row.text = "\n"
            new_row.tail = "\n"
            new_col = document.doc.SubElement(new_row,"td")
            new_col.text = N_("Money into selected accounts comes from")
            new_col = document.doc.SubElement(new_row,"td")
            new_col.text = ""
            
            row_num = 0
            work_done = 0
            work_to_do = len(self.money_in_alist)

            for acc in self.money_in_accounts:
                row_num += 1
                work_done += 1
                report_percent_done((work_done/float(work_to_do))*5.0+90.0)
                accpr = CashFlow.account_in_alist(acc,self.money_in_alist)
                acnt = accpr[0]

                if (row_num % 2) == 0:
                    new_row = document.StyleSubElement(new_table,'normal-row')
                else:
                    new_row = document.StyleSubElement(new_table,'alternate-row')
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

                colval = accpr[1].sum(report_currency, exchange_fn)

                new_col = document.StyleSubElement(new_row,'number-cell')
                new_col.text = colval.to_currency_string()

            new_row = document.StyleSubElement(new_table,'grand-total')
            new_row.text = "\n"
            new_row.tail = "\n"
            new_col = document.StyleSubElement(new_row,'text-cell')
            new_col.text = N_("Money In")
            new_col = document.StyleSubElement(new_row,'total-number-cell')
            colval = self.money_in_collector.sum(report_currency, exchange_fn)
            new_col.text = colval.to_currency_string()

            new_row = document.doc.SubElement(new_table,"tr")
            new_row.text = "\n"
            new_row.tail = "\n"
            new_data = document.doc.SubElement(new_row,"td",attrib={'rowspan' : "1", 'colspan' : "2" })
            new_ruler = document.doc.SubElement(new_data,"hr")

            new_row = document.StyleSubElement(new_table,'primary-subheading')
            new_row.text = "\n"
            new_row.tail = "\n"
            new_col = document.doc.SubElement(new_row,"td")
            new_col.text = N_("Money out of selected accounts goes to")
            new_col = document.doc.SubElement(new_row,"td")
            new_col.text = ""

            row_num = 0
            work_done = 0
            work_to_do = len(self.money_out_alist)

            for acc in self.money_out_accounts:
                row_num += 1
                work_done += 1
                report_percent_done((work_done/float(work_to_do))*5.0+90.0)
                accpr = CashFlow.account_in_alist(acc,self.money_out_alist)
                acnt = accpr[0]

                if (row_num % 2) == 0:
                    new_row = document.StyleSubElement(new_table,'normal-row')
                else:
                    new_row = document.StyleSubElement(new_table,'alternate-row')
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

                colval = accpr[1].sum(report_currency, exchange_fn)

                new_col = document.StyleSubElement(new_row,'number-cell')
                new_col.text = colval.to_currency_string()

            new_row = document.StyleSubElement(new_table,'grand-total')
            new_row.text = "\n"
            new_row.tail = "\n"
            new_col = document.StyleSubElement(new_row,'text-cell')
            new_col.text = N_("Money Out")
            new_col = document.StyleSubElement(new_row,'total-number-cell')
            colval = self.money_out_collector.sum(report_currency, exchange_fn)
            new_col.text = colval.to_currency_string()

            new_row = document.doc.SubElement(new_table,"tr")
            new_row.text = "\n"
            new_row.tail = "\n"
            new_data = document.doc.SubElement(new_row,"td",attrib={'rowspan' : "1", 'colspan' : "2" })
            new_ruler = document.doc.SubElement(new_data,"hr")

            new_row = document.StyleSubElement(new_table,'grand-total')
            new_row.text = "\n"
            new_row.tail = "\n"
            new_col = document.StyleSubElement(new_row,'text-cell')
            new_col.text = N_("Difference")
            new_col = document.StyleSubElement(new_row,'total-number-cell')
            colval = money_diff_collector.sum(report_currency, exchange_fn)
            new_col.text = colval.to_currency_string()

        report_finished()

        return document

