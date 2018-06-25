 
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
from gnc_report_utilities import get_commodities
from gnc_report_utilities import account_get_comm_balance_at_date

import gnc_commodity_utilities

import gnc_html_utilities

from qof_ctypes import gnc_print_date

import engine_ctypes

# maybe store the class in ReportTemplate then dont need this import
# yes we need a better way to handle this so dont need all these includes
from report_objects import OptionsDB
#from report_options import BooleanOption
#from report_options import MultiChoiceOption
# lets try importing all
from report_options import *


import gnucash

from gnucash import ACCT_TYPE_STOCK, ACCT_TYPE_MUTUAL, ACCT_TYPE_ASSET, ACCT_TYPE_EXPENSE, ACCT_TYPE_INCOME, ACCT_TYPE_BANK

from gnucash import GNC_DENOM_AUTO, GNC_HOW_RND_ROUND, GNC_HOW_DENOM_REDUCE
from gnucash.gnucash_core_c import GNC_HOW_DENOM_SIGFIG

from gnucash import GncNumeric


units_denom = 100000000
price_denom = 100000000


class CapitalGains(ReportTemplate):

    def __init__ (self):

        super(CapitalGains,self).__init__()

        # need to set the  base variables
        self.version = 1
        self.name = N_("Capital Gains")
        self.report_guid = "c9c3dd7052a8470e8757297a1d7a11c2"
        self.menu_path = N_("_Assets & Liabilities")


    def options_generator (self):

        #pdb.set_trace()

        # need to instantiate the options database
        self.options = OptionsDB()

        #self.options.add_report_date('General', N_("Date"), "a")

        self.options.add_date_interval('General', N_("Start Date"), N_("End Date"), "a")

        self.options.add_currency('General', N_("Report's currency"), "c")

        # explicit version used with just 2 options - latest or nearest
        # should the list be a dict or not??
        #self.options.add_price_source('General', N_("Price Source"), "d", 'pricedb-latest')
        self.options.register_option(MultiChoiceOption('General', N_("Price Source"),"d",
                                                         N_("The source of price information."),
                                                         'pricedb-nearest',
                                                         [ \
                                                         [ 'pricedb-latest', N_("Most recent"), N_("The most recent recorded price.") ],
                                                         [ 'pricedb-nearest', N_("Nearest in time"), N_("The price recorded nearest in time to the report date.") ],
                                                         ]))

        self.options.register_option(MultiChoiceOption('General', N_("Basis calculation method"),"e",
                                                         N_("Basis calculation method."),
                                                         'average-basis',
                                                         [ \
                                                         [ 'average-basis', N_("Average"), N_("Use average cost of all shares for basis.") ],
                                                         [ 'fifo-basis', N_("FIFO"), N_("Use first-in first-out method for basis.") ],
                                                         [ 'lifo-basis', N_("LIFO"), N_("Use last-in first-out method for basis.") ],
                                                         ]))


        self.options.register_option(SimpleBooleanOption(N_("General"), N_("Set preference for price list data"),"e",
                                                           N_("Prefer use of price editor pricing over transactions, where applicable."), True))

        self.options.register_option(MultiChoiceOption('General', N_("How to report brokerage fees"),"e",
                                                         N_("How to report commissions and other brokerage fees."),
                                                         'include-in-basis',
                                                         [ \
                                                         [ 'include-in-basis', N_("Include in basis"), N_("Include brokerage fees in the basis for the asset.") ],
                                                         [ 'include-in-gain', N_("Include in gain"), N_("Include brokerage fees in the gain and loss but not in the basis.") ],
                                                         [ 'ignore-brokerage', N_("Ignore"), N_("Ignore brokerage fees entirely.") ],
                                                         ]))


        self.options.register_option(SimpleBooleanOption(N_("Display"), N_("Show ticker symbols"),"a",
                                                           N_("Display the ticker symbols."), True))

        self.options.register_option(SimpleBooleanOption(N_("Display"), N_("Show listings"),"b",
                                                           N_("Display exchange listings."), True))

        self.options.register_option(SimpleBooleanOption(N_("Display"), N_("Show number of shares"),"c",
                                                           N_("Display numbers of shares in accounts."), True))

        self.options.register_option(NumberRangeOption(N_("Display"), N_("Share decimal places"),"d",
                                                           N_("The number of decimal places to use for share numbers."), 2, 0, 6, 0, 1))

        self.options.register_option(SimpleBooleanOption(N_("Display"), N_("Show prices"),"e",
                                                           N_("Display share prices."), True))

        self.options.register_option(SimpleBooleanOption(N_("Display"), N_("Show all transactions"),"f",
                                                           N_("Display all transactions."), False))

        self.options.register_option(SimpleBooleanOption(N_("Display"), N_("Convert currency all"),"f",
                                                           N_("Convert currency for all values"), False))


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
        #pdb.set_trace()
        retacc = filter_accountlist_type([ACCT_TYPE_STOCK, ACCT_TYPE_MUTUAL],accounts)
        return [True, retacc]


    @staticmethod
    def is_split_account_type (split,type):
        return split.GetAccount().GetType() == type

    @staticmethod
    def is_same_account (a1,a2):
        return (a1.GetGUID().compare(a2.GetGUID()) == 0)

    @staticmethod
    def is_same_split (s1,s2):
        return (s1.GetGUID().compare(s2.GetGUID()) == 0)


    @staticmethod
    def account_in_list (acnt,acclst):
        for acc in acclst:
            if AdvancedPortfolio.is_same_account(acnt,acc):
                return True
        return False

    @staticmethod
    def account_in_alist (acnt,alst):
        for acpr in alst:
            # scheme uses caar to access the list
            # but this seems right - acpr[0] is an account
            # ah - caar - access first element of list then first element of that first element
            if AdvancedPortfolio.is_same_account(acnt,acpr[0]):
                return acpr
        return None

    @staticmethod
    def sum_basis (blist,currency_frac):
        # ;; sum up the contents of the b-list built by basis-builder below
        # ah - for blist element index 0 is number of units, index 1 is price/value
        #pdb.set_trace()
        bsum = GncNumeric(0,1)
        for bitm in blist:
            bsum = bsum.add(bitm[0].mul(bitm[1],currency_frac,GNC_HOW_RND_ROUND),currency_frac,GNC_HOW_RND_ROUND)
        return bsum

    @staticmethod
    def units_basis (blist):
        # ;; sum up the total number of units in the b-list built by basis-builder below
        #pdb.set_trace()
        bsum = GncNumeric(0,1)
        for bitm in blist:
            bsum = bsum.add(bitm[0],units_denom,GNC_HOW_RND_ROUND)
        return bsum

    @staticmethod
    def apply_basis_ratio (blist, units_ratio, value_ratio):
        # ;; apply a ratio to an existing basis-list, useful for splits/mergers and spinoffs
        # ;; I need to get a brain and use (map) for this.
        #pdb.set_trace()
        print "Applying ratio",units_ratio.to_string()
        bsum = GncNumeric(0,1)
        newlst = []
        for bitm in blist:
            urt = units_ratio.mul(bitm[0],units_denom,GNC_HOW_RND_ROUND)
            vrt = value_ratio.mul(bitm[1],units_denom,GNC_HOW_RND_ROUND)
            newlst.append((urt,vrt))
        return newlst


    def basis_builder (self, blist, bunits, bvalue, bmethod, currency_frac):
        # ;; this builds a list for basis calculation and handles average, fifo and lifo methods
        # ;; the list is cons cells of (units-of-stock . price-per-unit)... average method produces only one
        # ;; cell that mutates to the new average. Need to add a date checker so that we allow for prices
        # ;; coming in out of order, such as a transfer with a price adjusted to carryover the basis.
        #pdb.set_trace()

        print "actually in basis-builder"
        print "b-list is", blist
        print "b-units is", bunits
        print "b-value is", bvalue
        print "b-method is", bmethod

        # unlike scheme blist must be a list on entry - even if empty

        # looks like this returns a blist

        # ;; if there is no b-value, then this is a split/merger and needs special handling

        # scheme cond

        # ;; we have value and positive units, add units to basis
        if  not bvalue.zero_p() and bunits.positive_p():

            if bmethod == 'average-basis':

                if len(blist) > 0:

                    # what if blist has more than 1 element??
                    # maybe not possible if doing average??
                    if len(blist) > 1:
                        print "average basis and blist > 1!!"
                        pdb.set_trace()
                        print "average basis and blist > 1!!"

                    #pdb.set_trace()

                    vl1 = bunits.add(blist[0][0],units_denom,GNC_HOW_RND_ROUND)
                    tvl1 = bvalue.add(blist[0][0].mul(blist[0][1],GNC_DENOM_AUTO,GNC_HOW_DENOM_REDUCE),GNC_DENOM_AUTO,GNC_HOW_DENOM_REDUCE)
                    tvl2 = bunits.add(blist[0][0],GNC_DENOM_AUTO,GNC_HOW_DENOM_REDUCE)
                    vl2 = tvl1.div(tvl2,price_denom,GNC_HOW_RND_ROUND)

                    nwvl = (vl1,vl2)
                    return [nwvl]

                else:

                    vl2 = bvalue.div(bunits,price_denom,GNC_HOW_RND_ROUND)
                    nwvl = (bunits,vl2)
                    blist.append(nwvl)

            else:

                vl2 = bvalue.div(bunits,price_denom,GNC_HOW_RND_ROUND)
                nwvl = (bunits,vl2)
                blist.append(nwvl)

            return blist

        # ;; we have value and negative units, remove units from basis
        elif not bvalue.zero_p() and bunits.negative_p():

            if len(blist) > 0:

                #pdb.set_trace()

                if bmethod == 'fifo-basis':

                    cmpval = bunits.abs().compare(blist[0][0])

                    if cmpval == -1:

                        # ;; Sold less than the first lot, create a new first lot from the remainder
                        # ah - by definition sell means negative units so the add actually is a subtract!!
                        new_units = bunits.add(blist[0][0],units_denom,GNC_HOW_RND_ROUND)
                        nwvl = (new_units, blist[0][1])
                        #blist = nwvl + blist[1:]
                        blist[0] = nwvl

                    elif cmpval == 0:

                        # ;; Sold all of the first lot
                        blist.pop(0)

                    elif cmpval == 1:

                        # ;; Sold more than the first lot, delete it and recurse
                        #pdb.set_trace()
                        newblst = blist[1:]
                        blist = self.basis_builder(newblst, bunits.add(blist[0][0],units_denom,GNC_HOW_RND_ROUND), 
                                     bvalue, # ;; Only the sign of b-value matters since the new b-units is negative
                                       bmethod, currency_frac)


                elif bmethod == 'lifo-basis':

                    # this reverses in place
                    pdb.set_trace()
                    blist.reverse()

                    cmpval = bunits.abs().compare(blist[0][0])

                    if cmpval == -1:
                        # ;; Sold less than the last lot
                        new_units = bunits.add(blist[0][0],units_denom,GNC_HOW_RND_ROUND)
                        nwvl = (new_units, blist[0][1])
                        blist[0] = nwvl
                        blist.reverse()
                    elif cmpval == 0:
                        # ;; Sold all of the last lot
                        blist = blist[1:]
                        blist.reverse()
                    elif cmpval == 1:
                        # ;; Sold more than the last lot
                        pdb.set_trace()
                        tmpblst = blist[1:]
                        tmpblst.reverse()
                        blist = self.basis_builder(tmpblst, bunits.add(blist[0][0],units_denom,GNC_HOW_RND_ROUND), 
                               bvalue, bmethod, currency_frac)


                elif bmethod == 'average-basis':

                    vl1 = blist[0][0].add(bunits,units_denom,GNC_HOW_RND_ROUND)
                    vl2 = blist[0][1]
                    blist = [(vl1,vl2)]

            return blist

        # ;; no value, just units, this is a split/merge...
        elif bvalue.zero_p() and not bunits.zero_p():

            print "Split/Merging"

            current_units = self.units_basis(blist)

            #pdb.set_trace()

            advl = bunits.add(current_units, GNC_DENOM_AUTO, GNC_HOW_DENOM_REDUCE)
            units_ratio = advl.div(current_units,GNC_DENOM_AUTO, GNC_HOW_DENOM_REDUCE)
            # ;; If the units ratio is zero the stock is worthless and the value should be zero too
            if units_ratio.zero_p():
                value_ratio = GncNumeric(0,1)
            else:
                value_ratio = GncNumeric(1,1).div(units_ratio,GNC_DENOM_AUTO,GNC_HOW_DENOM_REDUCE)

            newblst = self.apply_basis_ratio(blist, units_ratio, value_ratio)

            return newblst

        # ;; If there are no units, just a value, then its a spin-off,
        # ;; calculate a ratio for the values, but leave the units alone
        # ;; with a ratio of 1
        elif bunits.zero_p() and not bvalue.zero_p():

            print "Spinoff"

            current_value = self.sum_basis(blist,GNC_DENOM_AUTO)

            advl = bvalue.add(current_value, GNC_DENOM_AUTO, GNC_HOW_DENOM_REDUCE)
            value_ratio = advl.div(current_value,GNC_DENOM_AUTO, GNC_HOW_DENOM_REDUCE)

            newblst = self.apply_basis_ratio(blist, GncNumeric(1,1), value_ratio)

            return newblst

        # ;; when all else fails, just send the b-list back
        else:

            return blist

    def find_price (self, price_list, currency):

        # ;; Given a price list and a currency find the price for that currency on the list.
        # ;; If there is none for the requested currency, return the first one.
        # ;; The price list is released but the price returned is ref counted.

        # note according to me if there are multiple prices for a currency the last one
        # is returned - not sure about this though

        if len(price_list) == 0: return None

        price = None
        for prcitm in price_list:
            if engine_ctypes.CommodityEquiv(prcitm.get_currency(),currency):
                price = prcitm

        if price == None:
            price = price_list[0]

        return price


    @staticmethod
    def is_parent_or_sibling (a1,a2):
        a1parent = a1.get_parent()
        a2parent = a2.get_parent()
        if self.is_same_account(a2parent,a1) or self.is_same_account(a1parent,a2) or self.is_same_account(a1parent,a2parent):
            return True
        return False

    def is_spin_off (self, split, current):
        # ;; Test whether the given split is the source of a spin off transaction
        # ;; This will be a no-units split with only one other split.
        # ;; xaccSplitGetOtherSplit only returns on a two-split txn.  It's not a spinoff
        # ;; is the other split is in an income or expense account.
        # need exception wrap for python
        try:
            other_split = split.GetOtherSplit()
        except Exception, errexc:
            other_split = None

        if split.GetAmount().zero_p() and \
             self.is_same_account(current, split.GetAccount()) and \
             other_split != None and \
             self.is_split_account_type(other_split, ACCT_TYPE_EXPENSE) and \
             self.is_split_account_type(other_split, ACCT_TYPE_INCOME):
            return True

        return False


    def table_add_gain_row (self, row, curacc, to_date_tp, from_date_tp, report_currency,
         price_source, show_symbol, show_listing, show_shares, show_price, show_all, convert_all,
         basis_method, prefer_pricelist, handle_brokerage_fees,
         use_txn, pricing_txn, share_print_info, currency_frac,
         basis_amt,
         ticker_symbol, listing, txn_date, units, price, value, moneyin, moneyout, income, brokerage, gain, gain_report):

        # note that this function does not apply any currency conversions
        # I dont think I want this - I want to see the gain in native currency
        # plus a final conversion at transaction date to report currency

        if (row % 2) == 0:
            new_row = self.document.StyleSubElement(self.new_table,'normal-row')
        else:
            new_row = self.document.StyleSubElement(self.new_table,'alternate-row')
        new_row.text = "\n"
        new_row.tail = "\n"


        # need to figure new way to do this
        # original created a list
        # not clear how to do this
        # could try makeing elements then adding them later?
        # still dont know if can change/add parent to ET elements
        # do I need to - essentially the ET document is creating the
        # equivalent of the activecols list

        # the following does gnc:html-account-anchor
        accurl = gnc_html_utilities.account_anchor_text(curacc)

        new_col = self.document.doc.SubElement(new_row,"td")

        anchor_markup = self.document.doc.SubElement(new_col,"a")
        anchor_markup.attrib['href'] = accurl
        anchor_markup.text = N_(curacc.GetName()) + "\n"
        anchor_markup.tail = "\n"

        #activecols = [anchor_markup]

        # ;; build a list for the row  based on user selections

        if show_symbol:
            new_col = self.document.StyleSubElement(new_row,'text-cell')
            new_col.text = ticker_symbol
            new_col.tail = "\n"
            #activecols.append(new_col)

        if show_listing:
            new_col = self.document.StyleSubElement(new_row,'text-cell')
            new_col.text = listing
            new_col.tail = "\n"
            #activecols.append(new_col)

        new_col = self.document.StyleSubElement(new_row,'text-cell')
        new_col.text = str(txn_date)
        new_col.tail = "\n"
        #activecols.append(new_col)

        if show_shares:
            new_col = self.document.StyleSubElement(new_row,'number-cell')
            new_col.text = sw_app_utils.PrintAmount(units,share_print_info)
            new_col.tail = "\n"
            #activecols.append(new_col)
        if show_price:
            new_col = self.document.StyleSubElement(new_row,'number-cell')
            new_col.tail = "\n"

            #pdb.set_trace()

            if use_txn:
                if pricing_txn:
                    # this does gnc:html-transaction-anchor
                    prcurl = gnc_html_utilities.transaction_anchor_text(pricing_txn)
                    #pdb.set_trace()
                    # is this always going to be a GncMonetary??
                    # yes!!
                    prcstr = price.to_currency_string()
                else:
                    #pdb.set_trace()
                    # what type is this??
                    print "price type is",price
                    prcurl = None
                    if isinstance(price,gnc_commodity_utilities.GncMonetary):
                        prcstr = price.to_currency_string()
                    else:
                        prcstr = price.to_string()
            else:
                # this does gnc:html-price-anchor
                # note price here MUST be a GncPrice
                prcurl = gnc_html_utilities.price_anchor_text(price)
                prcstr = gnc_commodity_utilities.GncMonetary(price.get_currency(), price.get_value()).to_currency_string()

            if prcurl != None:
                anchor_markup = self.document.doc.SubElement(new_col,"a")
                anchor_markup.attrib['href'] = prcurl
                anchor_markup.text = prcstr
                anchor_markup.tail = "\n"
            else:
                # this appears to be what code says
                new_col.text = prcstr

            #activecols.append(new_col)


        # now add lots more
        if use_txn:
            if pricing_txn:
               txtstr = "*"
            else:
               txtstr = "**"
        else:
           txtstr = " "

        new_col = self.document.StyleSubElement(new_row,'text-cell')
        new_col.text = txtstr
        new_col.tail = "\n"

        new_col = self.document.StyleSubElement(new_row,'number-cell')
        new_col.text = basis_amt.to_currency_string()
        new_col.tail = "\n"

        new_col = self.document.StyleSubElement(new_row,'number-cell')
        new_col.text = value.to_currency_string()
        new_col.tail = "\n"

        new_col = self.document.StyleSubElement(new_row,'number-cell')
        new_col.text = moneyin.to_currency_string()
        new_col.tail = "\n"

        new_col = self.document.StyleSubElement(new_row,'number-cell')
        new_col.text = moneyout.to_currency_string()
        new_col.tail = "\n"

        new_col = self.document.StyleSubElement(new_row,'number-cell')
        new_col.text = income.to_currency_string()
        new_col.tail = "\n"

        if handle_brokerage_fees != 'ignore-brokerage':

            new_col = self.document.StyleSubElement(new_row,'number-cell')
            new_col.text = brokerage.to_currency_string()
            new_col.tail = "\n"

        new_col = self.document.StyleSubElement(new_row,'number-cell')
        new_col.text = gain.to_currency_string()
        new_col.tail = "\n"

        new_col = self.document.StyleSubElement(new_row,'number-cell')
        new_col.text = gain_report.to_currency_string()
        new_col.tail = "\n"


    def table_add_stock_rows (self, accounts, to_date_tp, from_date_tp, report_currency, exchange_fn, price_fn,
         price_source, include_empty, show_symbol, show_listing, show_shares, show_price, show_all, convert_all,
         basis_method, prefer_pricelist, handle_brokerage_fees,
         total_basis, total_value, total_moneyin, total_moneyout, total_income, total_gain, total_ugain, total_brokerage, total_gain_report):

        optobj = self.options.lookup_name('Display','Share decimal places')
        num_places = optobj.get_option_value()
        share_print_info = sw_app_utils.SharePrintInfoPlaces(num_places)

        work_to_do = len(accounts)
        work_done = 0

        for row,curacc in enumerate(accounts):

            # I dont see any reason to process any account which does not
            # have sale in required period

            # to date limit gains need a pre-scan of splits to find sales within
            # the date range - if no sales within date range we dont list all transactions
            # I hope a sale must involve negative units
            # this is going to FAIL for short selling where the the sale is first
            # and the buy is where we need to compute the gain
            check_do_all = False
            can_skip_account = True
            for split_acc in curacc.GetSplitList():
                parent = split_acc.GetParent()
                txn_date = parent.RetDatePostedTS()
                if txn_date >= from_date_tp.date() and txn_date < to_date_tp.date():
                    for split in parent.GetSplitList():
                        if self.is_same_account(curacc,split.GetAccount()):
                            split_units = split.GetAmount()
                            if split_units.negative_p():
                                can_skip_account = False
                                if show_all:
                                    check_do_all = True

            if can_skip_account:
                continue

            print "account",curacc.GetName(),curacc

            commod = curacc.GetCommodity()

            #pdb.set_trace()
            ticker_symbol = commod.get_mnemonic()
            listing = commod.get_namespace()

            unit_collector = account_get_comm_balance_at_date(curacc, to_date_tp)

            units = unit_collector.getpair(commod)[1]

            print "units",units.to_string()

            # ;; Counter to keep track of stuff
            brokeragecoll = CommodityCollector()
            dividendcoll  = CommodityCollector()
            moneyincoll   = CommodityCollector()
            moneyoutcoll  = CommodityCollector()
            gaincoll      = CommodityCollector()
            gaincoll_report = CommodityCollector()


            # ;; the price of the commodity at the time of the report
            # for placeholder stock accounts we get an empty list
            #pdb.set_trace()
            price_list = price_fn(commod,report_currency,to_date_tp)
            if len(price_list) > 0:
                price = price_list[0]
            else:
                price = None

            # ;; the value of the commodity, expressed in terms of
            # ;; the report's currency.
            value = gnc_commodity_utilities.GncMonetary(report_currency,GncNumeric(0,1))   # ;; Set later
            currency_frac = report_currency.get_fraction()

            pricing_txn = False
            use_txn = False
            basis_list = []
            # ;; setup an alist for the splits we've already seen.
            # - in python make a dict - we look up entries by guid key
            seen_trans = {}
            # ;; Account used to hold remainders from income reinvestments and
            # ;; running total of amount moved there
            drp_holding_account = False
            drp_holding_amount = GncNumeric(0,1)

            def my_exchange_fn (fromunits, tocurrency):

                #pdb.set_trace()

                if engine_ctypes.CommodityEquiv(report_currency,tocurrency) and \
                    engine_ctypes.CommodityEquiv(fromunits.commodity,commod):
                    # ;; Have a price for this commodity, but not necessarily in the report's
                    # ;; currency.  Get the value in the commodity's currency and convert it to
                    # ;; report currency.
                    prccmd = price.commodity if use_txn else price.get_currency()
                    prcamt = price.amount if use_txn else price.get_value()
                    prcval = fromunits.amount.mul(prcamt, currency_frac, GNC_HOW_RND_ROUND)
                    new_val = gnc_commodity_utilities.GncMonetary(prccmd, prcval)
                    runval = exchange_fn.run(new_val, tocurrency)
                else:
                    runval = exchange_fn.run(fromunits, tocurrency)
                return runval

            print "Starting account ", curacc.GetName(), ", initial price: ", 
            if price != None:
                print gnc_commodity_utilities.GncMonetary(price.get_currency(),price.get_value()).to_currency_string()
            else:
                print
                        
            # ;; If we have a price that can't be converted to the report currency
            # ;; don't use it
            if price != None:
                tmpprc = exchange_fn.run(gnc_commodity_utilities.GncMonetary(price.get_currency(),GncNumeric(100,1)), report_currency)
                if tmpprc.amount.zero_p():
                    price = None


            # ;; If we are told to use a pricing transaction, or if we don't have a price
            # ;; from the price DB, find a good transaction to use.
            if not use_txn and (price == None or not prefer_pricelist):
                #pdb.set_trace()
                if price_source == 'pricedb-latest':
                    prctim = datetime.now().date()
                elif price_source == 'pricedb-nearest':
                    prctim = to_date_tp
                else:
                    prctim = datetime.now().date()   # ;; error, but don't crash
                # yes - curacc is current single account - need list for match_commodity_splits_sorted
                split_list = gnc_commodity_utilities.match_commodity_splits_sorted([curacc],prctim)

                # so we sort early to late then reverse
                split_list.reverse()

                # ;; Find the first (most recent) one that can be converted to report currency
                spltindx = 0
                while not use_txn and spltindx < len(split_list):

                    split =  split_list[spltindx]

                    if not split.GetAmount().zero_p() and not split.GetValue().zero_p():

                        trans = split.GetParent()
                        trans_currency = trans.GetCurrency()
                        trans_price = exchange_fn.run(gnc_commodity_utilities.GncMonetary(trans_currency,split.GetSharePrice()),report_currency)
                        if not trans_price.amount.zero_p():

                            # ;; We can exchange the price from this transaction into the report currency
                            pricing_txn = trans
                            price = trans_price
                            use_txn = True

                    spltindx += 1

                #pdb.set_trace()
                if price != None:
                    print "Using non-transaction price",price.to_currency_string()


            # ;; If we still don't have a price, use a price of 1 and complain later
            #pdb.set_trace()
            if price == None:
                price = gnc_commodity_utilities.GncMonetary(report_currency, GncNumeric(1,1))
                # ;; If use-txn is set, but pricing-txn isn't set, it's a bogus price
                use_txn = True
                pricing_txn = False

            # ;; Now that we have a pricing transaction if needed, set the value of the asset
            value = my_exchange_fn(gnc_commodity_utilities.GncMonetary(commod,units), report_currency)

            # this may not be useful - if units is 0 there is no value and if we have sold all shares
            # then at this point we have 0 units so value is 0

            print "Value ", value.to_currency_string()
            print " from ", gnc_commodity_utilities.GncMonetary(commod, units).to_currency_string()


            # ;; we're looking at each split we find in the account. these splits
            # ;; could refer to the same transaction, so we have to examine each
            # ;; split, determine what kind of split it is and then act accordingly.
            for split_acc in curacc.GetSplitList():

                work_done += 1

                report_percent_done((work_done/float(work_to_do))*100.0)

                #pdb.set_trace()
                parent = split_acc.GetParent()
                txn_date = parent.RetDatePostedTS()
                commod_currency = parent.GetCurrency()
                commod_currency_frac = commod_currency.get_fraction()

                print "Analyzing transaction for stock", ticker_symbol, "on date", str(txn_date)

                if txn_date <= to_date_tp.date() and \
                     not parent.GetGUID() in seen_trans:

                    trans_income = GncNumeric(0,1)
                    trans_brokerage = GncNumeric(0,1)
                    trans_shares = GncNumeric(0,1)
                    shares_bought = GncNumeric(0,1)
                    shares_sold = GncNumeric(0,1)
                    trans_sold = GncNumeric(0,1)
                    trans_bought = GncNumeric(0,1)
                    trans_spinoff = GncNumeric(0,1)
                    trans_drp_residual = GncNumeric(0,1)
                    trans_drp_account = None

                    gain = GncNumeric(0,1)

                    # ;; Add this transaction to the list of processed transactions so we don't
                    # ;; do it again if there is another split in it for this account
                    seen_trans[parent.GetGUID()] = 1

                    #pdb.set_trace()

                    check_sale = False
                    check_buy = False

                    # ;; Go through all the splits in the transaction to get an overall idea of
                    # ;; what it does in terms of income, money in or out, shares bought or sold, etc.
                    for split in parent.GetSplitList():

                        print "split for", split.GetAccount().GetName(),split.GetValue().to_string()

                        split_units = split.GetAmount()
                        split_value = split.GetValue()

                        # even basic call fails
                        # - so wrap with try then test
                        try:
                            other_split = split.GetOtherSplit()
                        except Exception, errexc:
                            other_split = None
                        print "other split for", other_split

                        if self.is_split_account_type(split, ACCT_TYPE_EXPENSE):
                            # ;; Brokerage expense unless a two split transaction with other split
                            # ;; in the stock account in which case it's a stock donation to charity.
                            # why does this work in Scheme - GetOtherSplit returns None - or null list in scheme
                            # if more than 2 splits in a transaction
                            #
                            #other_split = split.GetOtherSplit()
                            try:
                                other_split = split.GetOtherSplit()
                            except Exception, errexc:
                                other_split = None
                            if other_split == None or \
                               not self.is_same_account(curacc,split.GetOtherSplit().GetAccount()):
                                trans_brokerage = trans_brokerage.add(split_value,commod_currency_frac,GNC_HOW_RND_ROUND) 
                        elif self.is_split_account_type(split, ACCT_TYPE_INCOME):
                            trans_income = trans_income.sub(split_value,commod_currency_frac,GNC_HOW_RND_ROUND) 
                        elif self.is_same_account(curacc,split.GetAccount()):
                            trans_shares = trans_shares.add(split_units.abs(),units_denom,GNC_HOW_RND_ROUND) 
                            if split_units.zero_p():
                                if self.is_spin_off(split,curacc):
                                    # ;; Count money used in a spin off as money out
                                    if split_value.negative_p():
                                        trans_spinoff = trans_spinoff.sub(split_value,commod_currency_frac, GNC_HOW_RND_ROUND)
                                else:
                                    if split_value.zero_p():
                                        # ;; Gain/loss split (amount zero, value non-zero, and not spinoff).  There will be
                                        # ;; a corresponding income split that will incorrectly be added to trans- income
                                        # ;; Fix that by subtracting it here
                                        trans_income = trans_income.sub(split_value,commod_currency_frac, GNC_HOW_RND_ROUND)
                            else:
                                # ;; Non-zero amount, add the value to the sale or purchase total.
                                if split_value.positive_p():
                                    trans_bought = trans_bought.add(split_value,commod_currency_frac, GNC_HOW_RND_ROUND)
                                    shares_bought = shares_bought.add(split_units,units_denom, GNC_HOW_RND_ROUND)
                                    check_buy = True
                                else:
                                    # for sale we have negative value
                                    trans_sold = trans_sold.sub(split_value,commod_currency_frac, GNC_HOW_RND_ROUND)
                                    shares_sold = shares_sold.add(split_units,units_denom, GNC_HOW_RND_ROUND)
                                    check_sale = True
                        elif self.is_split_account_type(split, ACCT_TYPE_ASSET):
                            # ;; If all the asset accounts mentioned in the transaction are siblings of each other
                            # ;; keep track of the money transfered to them if it is in the correct currency
                            if trans_drp_account == None:
                                trans_drp_account = split.GetAccount()
                                if engine_ctypes.CommodityEquiv(commod_currency, trans_drp_account.GetCommodity()):
                                    trans_drp_residual = split_value
                                else:
                                    trans_drp_account = None
                            else:
                                if trans_drp_account != None:
                                   if self.is_parent_or_sibling(trans_drp_account, split.GetAccount()):
                                       trans_drp_residual = trans_drp_residual.add(split_value, commod_currency_frac, GNC_HOW_RND_ROUND)
                                   else:
                                       trans_drp_account = None

                    print "Income: ", trans_income.to_string()
                    print " Brokerage: ", trans_brokerage.to_string()
                    print " Shares traded: ", trans_shares.to_string()
                    print " Shares bought: ", shares_bought.to_string()
                    print " Shares sold: ", shares_sold.to_string()
                    print " Value sold: ", trans_sold.to_string()
                    print " Value purchased: ", trans_bought.to_string()
                    print " Spinoff value ", trans_spinoff.to_string()
                    print " Trans DRP residual: ", trans_drp_residual.to_string()

                    # ;; We need to calculate several things for this transaction:
                    # ;; 1. Total income: this is already in trans-income
                    # ;; 2. Change in basis: calculated by loop below that looks at every
                    # ;;    that acquires or disposes of shares
                    # ;; 3. Realized gain: also calculated below while calculating basis
                    # ;; 4. Money in to the account: this is the value of shares bought
                    # ;;    except those purchased with reinvested income
                    # ;; 5. Money out: the money received by disposing of shares.   This
                    # ;;    is in trans-sold plus trans-spinoff
                    # ;; 6. Brokerage fees: this is in trans-brokerage

                    # ;; Income
                    dividendcoll.add(commod_currency, trans_income)

                    # ;; Brokerage fees.  May be either ignored or part of basis, but that
                    # ;; will be dealt with elsewhere.
                    brokeragecoll.add(commod_currency, trans_brokerage)

                    # ;; Add brokerage fees to trans-bought if not ignoring them and there are any
                    if handle_brokerage_fees != 'ignore-brokerage' and \
                        trans_brokerage.positive_p() and trans_shares.positive_p():
                        fee_frac = shares_bought.div(trans_shares,GNC_DENOM_AUTO,GNC_HOW_DENOM_REDUCE)
                        fees = trans_brokerage.mul(fee_frac, commod_currency_frac, GNC_HOW_RND_ROUND)
                        trans_bought = trans_bought.add(fees, commod_currency_frac, GNC_HOW_RND_ROUND)

                    # ;; Update the running total of the money in the DRP residual account.  This is relevant
                    # ;; if this is a reinvestment transaction (both income and purchase) and there seems to
                    # ;; asset accounts used to hold excess income.
                    if trans_drp_account != None and trans_income.positive_p() and trans_bought.positive_p():

                        if drp_holding_account == None:

                            drp_holding_account = trans_drp_account
                            drp_holding_amount = trans_drp_residual

                        else:

                            if drp_holding_account != None and self.is_parent_or_sibling(trans_drp_account,drp_holding_account):
                                drp_holding_amount = drp_holding_amount.add(trans_drp_residual,commod_curency_frac,GNC_HOW_RND_ROUND)
                            else:
                                # ;; Wrong account (or no account), assume there isn't a DRP holding account
                                drp_holding_account = None
                                trans_drp_residual = GncNumeric(0,1)
                                drp_holding_amount = GncNumeric(0,1)


                    # ;; Set trans-bought to the amount of money moved in to the account which was used to
                    # ;; purchase more shares.  If this is not a DRP transaction then all money used to purchase
                    # ;; shares is money in.
                    if trans_income.positive_p() and trans_bought.positive_p():

                        trans_bought = trans_bought.sub(trans_income,commod_currency_frac, GNC_HOW_RND_ROUND)
                        trans_bought = trans_bought.add(trans_drp_residual,commod_currency_frac, GNC_HOW_RND_ROUND)
                        trans_bought = trans_bought.sub(drp_holding_amount,commod_currency_frac, GNC_HOW_RND_ROUND)

                        # ;; If the DRP holding account balance is negative, adjust it by the amount
                        # ;; used in this transaction
                        if drp_holding_amount.negative_p() and trans_bought.positive_p():
                            drp_holding_amount = drp_holding_amount.add(trans_bought,commod_currency_frac,GNC_HOW_RND_ROUND)

                        # ;; Money in is never more than amount spent to purchase shares
                        if trans_bought.negative_p():
                            trans_bought = GncNumeric(0,1)

                    print "Adjusted trans-bought ", trans_bought.to_string()
                    print " DRP holding account ", drp_holding_amount.to_string()

                    moneyincoll.add(commod_currency, trans_bought)
                    moneyoutcoll.add(commod_currency, trans_sold)
                    moneyoutcoll.add(commod_currency, trans_spinoff)

                    # when we sell the basis is reduced - we need to save
                    # the basis amount before the basis is updated
                    orig_basis = GncNumeric(0,1)
                    new_basis = GncNumeric(0,1)

                    # ;; Look at splits again to handle changes in basis and realized gains

                    for split in parent.GetSplitList():

                        # ;; get the split's units and value
                        split_units = split.GetAmount()
                        split_value = split.GetValue()

                        print "Pass 2: split units ", split_units.to_string(), " split-value ", \
                            split_value.to_string(), " commod-currency ", \
                            commod_currency.get_printname()

                        if not split_units.zero_p() and self.is_same_account(curacc,split.GetAccount()):
                            # ;; Split into subject account with non-zero amount.  This is a purchase
                            # ;; or a sale, adjust the basis
                            # why is this converting to report_currency here??
                            # why not just do it at end??
                            # maybe we bought with differing currencies??
                            # and the basis needs to be done in a single currency
                            # and I think this is wrong - as far as I can tell its converting using the
                            # price at to_date_tp - surely it should be using the transaction date exchange rate
                            split_value_currency = my_exchange_fn(gnc_commodity_utilities.GncMonetary(commod_currency, split_value), report_currency).amount
                            orig_basis = self.sum_basis(basis_list, currency_frac)
                            # ;; proportion of the fees attributable to this split
                            fee_ratio = split_units.abs().div(trans_shares, GNC_DENOM_AUTO, GNC_HOW_DENOM_REDUCE)
                            # ;; Fees for this split in report currency
                            fees_currency = my_exchange_fn(gnc_commodity_utilities.GncMonetary(commod_currency, fee_ratio.mul(trans_brokerage, commod_currency_frac, GNC_HOW_RND_ROUND)), report_currency).amount
                            if handle_brokerage_fees == 'include-in-basis':
                                # ;; Include brokerage fees in basis
                                split_value_with_fees = split_value.add(trans_brokerage, currency_frac, GNC_HOW_RND_ROUND)
                                split_value_with_fees_currency = split_value_currency.add(fees_currency, currency_frac, GNC_HOW_RND_ROUND)
                            else:
                                split_value_with_fees = split_value
                                split_value_with_fees_currency = split_value_currency

                            print "going in to basis list ", basis_list, " ", split_units.to_string(), " "
                            print "                       ", split_value_with_fees.to_string()
                            print "                       ", split_value_with_fees_currency.to_string()

                            # ;; adjust the basis
                            basis_list = self.basis_builder(basis_list, split_units, split_value_with_fees, basis_method, currency_frac)

                            print "coming out of basis list ", basis_list

                            # ;; If it's a sale or the stock is worthless, calculate the gain
                            if not split_value.positive_p():
                                # ;; Split value is zero or negative.  If it's zero it's either a stock split/merge
                                # ;; or the stock has become worthless (which looks like a merge where the number
                                # ;; of shares goes to zero).  If the value is negative then it's a disposal of some sort.
                                new_basis = self.sum_basis(basis_list, currency_frac)
                                if new_basis.zero_p() or split_value.negative_p():
                                    # ;; Split value is negative or new basis is zero (stock is worthless),
                                    # ;; Capital gain is money out minus change in basis
                                    gain = split_value_with_fees.abs().sub(orig_basis.sub(new_basis,currency_frac,GNC_HOW_RND_ROUND),currency_frac,GNC_HOW_RND_ROUND)
                                    print "Old basis=", orig_basis.to_string()
                                    print " New basis=", new_basis.to_string()
                                    print " Gain=", gain.to_string()
                                    #gaincoll.add(report_currency,gain)
                                    gaincoll.add(commod_currency,gain)

                        # ;; here is where we handle a spin-off txn. This will be a no-units
                        # ;; split with only one other split. xaccSplitGetOtherSplit only
                        # ;; returns on a two-split txn.  It's not a spinoff is the other split is
                        # ;; in an income or expense account.
                        elif self.is_spin_off(split,curacc):
                            print "before spin-off basis list ", basis_list
                            basis_list = self.basis_builder(basis_list, split_units,
                                                   my_exchange_fn(gnc_commodity_utilities.GncMonetary(commod_currency, split_value),report_currency).amount,
                                                   basis_method, currency_frac)
                            print "after spin-off basis list ", basis_list


                    # WE HAVE A BIG PROBLEM
                    # THIS SCRIPT DOES NOT HANDLE short selling
                    # - where the gain is not at the sale but at the buy!!

                    # interesting - for exercised call options (when your shares are sold)
                    # Schwab combines the share gain and option gain into single share gain
                    # - maybe because was short term for both??


                    # we have seen a sale
                    # now check within the bounds
                    #if check_sale and \
                    #    (txn_date >= from_date_tp.date() and txn_date < to_date_tp.date()):
                    #if not trans_shares.zero_p() and txn_date < to_date_tp.date():
                    if check_do_all or (check_sale and \
                        (txn_date >= from_date_tp.date() and txn_date < to_date_tp.date())):

                        #pdb.set_trace()

                        #if ticker_symbol == 'JNJ': pdb.set_trace()

                        moneyin = gnc_commodity_utilities.GncMonetary(commod_currency, trans_bought)
                        moneyout = gnc_commodity_utilities.GncMonetary(commod_currency, trans_sold)
                        capgain = gnc_commodity_utilities.GncMonetary(commod_currency, gain)
                        curincome = gnc_commodity_utilities.GncMonetary(commod_currency, trans_income)
                        curfees = gnc_commodity_utilities.GncMonetary(commod_currency, trans_brokerage)

                        # we need a price for the transaction
                        # I dont get this - the anchor function for price seems to require a GncPrice object
                        # NOT a GncMonetary object
                        # ah - now get it - the price of the commodity can either be from the database (GncPrice)
                        # or computed from the transaction when it is a GncMonetary
                        # my_exchange_fn handles this assuming use_txn and pricing_txn
                        # so need to set use_txn and pricing_txn here
                        if check_sale or check_buy:
                            if check_buy:
                                trans_value = trans_bought.sub(trans_brokerage,currency_frac,GNC_HOW_RND_ROUND)
                                shares_change = shares_bought
                            else:
                                moneyout = trans_sold.sub(trans_brokerage,currency_frac,GNC_HOW_RND_ROUND)
                                moneyout = gnc_commodity_utilities.GncMonetary(commod_currency, moneyout)
                                trans_value = trans_sold
                                shares_change = shares_sold
                            # apparently trans_shares is always positive - Im confused
                            trans_price = trans_value.div(trans_shares.abs(),currency_frac,GNC_HOW_RND_ROUND)
                            trans_value = gnc_commodity_utilities.GncMonetary(commod_currency, trans_value)
                            trans_price = gnc_commodity_utilities.GncMonetary(commod_currency, trans_price)
                            new_use_txn = True
                            new_pricing_txn = parent
                        else:
                            trans_value = GncNumeric(0,1)
                            trans_price = GncNumeric(0,1)
                            trans_value = gnc_commodity_utilities.GncMonetary(commod_currency, trans_value)
                            trans_price = gnc_commodity_utilities.GncMonetary(commod_currency, trans_price)
                            new_use_txn = True
                            new_pricing_txn = False

                        print "price", type(price)
                        #pdb.set_trace()

                        if check_sale:
                            basis_amt = gnc_commodity_utilities.GncMonetary(commod_currency, orig_basis.sub(new_basis, currency_frac,GNC_HOW_RND_ROUND))
                        elif check_buy:
                            # - no for a buy the basis doesnt change - basis only affects sales
                            # well it does change the basis for the sale - leave for now
                            # this is wrong - we need the basis component for this transaction
                            # - which should simply be the value of the buy!!
                            basis_amt = gnc_commodity_utilities.GncMonetary(commod_currency, trans_bought)
                            #basis_amt = GncNumeric(0,1)
                        else:
                            # these are likely gain/loss splits so far
                            print "junk"
                            #pdb.set_trace()
                            basis_amt = gnc_commodity_utilities.GncMonetary(commod_currency, GncNumeric(0,1))

                        # finally convert gain to report currency
                        if engine_ctypes.CommodityEquiv(capgain.commodity,report_currency):
                            capgain_report = capgain
                        else:
                            # this relies on having a price database for the currencies involved!!!
                            # if not it seems to return a 0 value
                            capgain_report = gnc_commodity_utilities.exchange_by_pricedb_nearest(capgain,report_currency,txn_date)
                            if capgain_report.amount.zero_p():
                                if not capgain.amount.zero_p():
                                    capgain_report = capgain
                                else:
                                    capgain_report = gnc_commodity_utilities.GncMonetary(report_currency, GncNumeric(0,1))
                        gaincoll_report.add(report_currency,capgain_report.amount)

                        # convert all values to report currency if requested
                        # note we cheat here by using single final currency conversion factor
                        # ie we do not include currency conversion gains
                        if convert_all:

                            def convcurr (preval):
                                if engine_ctypes.CommodityEquiv(preval.commodity,report_currency):
                                    postval = preval
                                else:
                                    # this relies on having a price database for the currencies involved!!!
                                    # if not it seems to return a 0 value
                                    postval = gnc_commodity_utilities.exchange_by_pricedb_nearest(preval,report_currency,txn_date)
                                    if postval.amount.zero_p():
                                        if not preval.amount.zero_p():
                                            postval = preval
                                        else:
                                            postval = gnc_commodity_utilities.GncMonetary(report_currency, GncNumeric(0,1))
                                return postval

                            report_basis_amt = convcurr(basis_amt)
                            report_trans_price = convcurr(trans_price)
                            report_trans_value = convcurr(trans_value)
                            report_moneyin = convcurr(moneyin)
                            report_moneyout = convcurr(moneyout)
                            report_curincome = convcurr(curincome)
                            report_curfees = convcurr(curfees)
                            report_capgain = convcurr(capgain)

                            self.table_add_gain_row(row, curacc, to_date_tp, from_date_tp, report_currency,
                                    price_source, show_symbol, show_listing, show_shares, show_price, show_all, convert_all,
                                    basis_method, prefer_pricelist, handle_brokerage_fees,
                                    new_use_txn, new_pricing_txn, share_print_info, currency_frac,
                                    report_basis_amt,
                                    ticker_symbol, listing, txn_date, shares_change, report_trans_price, report_trans_value, report_moneyin, report_moneyout, report_curincome, report_curfees, report_capgain, capgain_report)

                        else:

                            self.table_add_gain_row(row, curacc, to_date_tp, from_date_tp, report_currency,
                                    price_source, show_symbol, show_listing, show_shares, show_price, show_all, convert_all,
                                    basis_method, prefer_pricelist, handle_brokerage_fees,
                                    new_use_txn, new_pricing_txn, share_print_info, currency_frac,
                                    basis_amt,
                                    ticker_symbol, listing, txn_date, shares_change, trans_price, trans_value, moneyin, moneyout, curincome, curfees, capgain, capgain_report)


            # ;; Look for income and expense transactions that don't have a split in the
            # ;; the account we're processing.  We do this as follow
            # ;; 1. Make sure the parent account is a currency-valued asset or bank account
            # ;; 2. If so go through all the splits in that account
            # ;; 3. If a split is part of a two split transaction where the other split is
            # ;;    to an income or expense account and the leaf name of that account is the
            # ;;    same as the leaf name of the account we're processing, add it to the
            # ;;    income or expense accumulator
            # ;;
            # ;; In other words with an account structure like
            # ;;
            # ;;   Assets (type ASSET)
            # ;;     Broker (type ASSET)
            # ;;       Widget Stock (type STOCK)
            # ;;   Income (type INCOME)
            # ;;     Dividends (type INCOME)
            # ;;       Widget Stock (type INCOME)
            # ;;
            # ;; If you are producing a report on "Assets:Broker:Widget Stock" a
            # ;; transaction that debits the Assets:Broker account and credits the
            # ;; "Income:Dividends:Widget Stock" account will count as income in
            # ;; the report even though it doesn't have a split in the account
            # ;; being reported on.

            #pdb.set_trace()
            parent_account = curacc.get_parent()
            account_name = curacc.GetName()

            if parent_account != None and \
                parent_account.GetType() in [ACCT_TYPE_ASSET, ACCT_TYPE_BANK] and \
                  engine_ctypes.CommodityIsCurrency(parent_account.GetCommodity()):

                for split in parent_account.GetSplitList():

                    other_split = split.GetOtherSplit()
                    # ;; This is safe because xaccSplitGetAccount returns null for a null split
                    other_acct = other_split.GetAccount()
                    parent = split.GetParent()
                    txn_date = parent.RetDatePostedTS()

                    if other_acct != None and \
                        txn_date <= to_date_tp.date() and \
                           other_acct.GetName() == account_name and \
                             engine_ctypes.CommodityIsCurrency(other_acct.GetCommodity()):
                        # ;; This is a two split transaction where the other split is to an
                        # ;; account with the same name as the current account.  If it's an
                        # ;; income or expense account accumulate the value of the transaction
                        val = split.GetValue()
                        curr = other_acct.GetCommodity()
                        if self.is_split_account_type(other_split, ACCT_TYPE_INCOME):
                            print "More income ", val.to_string()
                            dividendcoll.add(curr, val)
                        elif self.is_split_account_type(other_split, ACCT_TYPE_EXPENSE):
                            print "More expense ", val.neg().to_string()
                            brokeragecoll.add(curr, val.neg())

            print "pricing txn is ", pricing_txn
            print "use txn is ", use_txn
            print "prefer-pricelist is ", prefer_pricelist
            print "price is ", price

            print "basis we're using to build rows is ", self.sum_basis(basis_list,currency_frac).to_string()
            print "but the actual basis list is ", basis_list

            # wierd - I think this is removing the brokerage fees???
            if handle_brokerage_fees == 'include-in-gain':
                gaincoll.minusmerge(brokeragecoll, False)

            # was in middle of table row creation
            # - this is more reasonable

            # not so fast - need to check what currency conversion factors are being used
            # yes - that doesnt seem to be included in the CommodityCollector
            # the sum function takes an exchange function with a preset date
            # (unless Im wrong which I could easily be - my scheme translation is not good)
            # I want to convert with exchange rate of date of each transaction
            # relatively simple addition - include date parameter on add

            moneyin = moneyincoll.sum(report_currency, my_exchange_fn)
            moneyout = moneyoutcoll.sum(report_currency, my_exchange_fn)
            brokerage = brokeragecoll.sum(report_currency, my_exchange_fn)
            income = dividendcoll.sum(report_currency, my_exchange_fn)
            # ;; just so you know, gain == realized gain, ugain == un-realized gain, bothgain, well..
            gain = gaincoll.sum(report_currency, my_exchange_fn)
            ugain = gnc_commodity_utilities.GncMonetary(report_currency,
                      my_exchange_fn(value, report_currency).amount.sub(self.sum_basis(basis_list,report_currency.get_fraction()),currency_frac, GNC_HOW_RND_ROUND))
            bothgain = gnc_commodity_utilities.GncMonetary(report_currency, gain.amount.add(ugain.amount,currency_frac,GNC_HOW_RND_ROUND))

            total_value.add(value.commodity, value.amount)
            total_moneyin.merge(moneyincoll)
            total_moneyout.merge(moneyoutcoll)
            total_brokerage.merge(brokeragecoll)
            total_income.merge(dividendcoll)
            total_gain.merge(gaincoll)
            total_gain_report.merge(gaincoll_report)
            total_ugain.add(ugain.commodity, ugain.amount)


            # maybe this is why basis is done in report currency
            # - but why not just sum and convert here??
            # ah - I think when we sell a stock the basis is reduced by the stock sold
            # - so if we sell all a stock the final basis is 0
            curbasissum = self.sum_basis(basis_list, currency_frac)
            prccmd = price.commodity if use_txn else price.get_currency()
            curbasissum = gnc_commodity_utilities.GncMonetary(prccmd,curbasissum)
            curbasissum_report = gnc_commodity_utilities.exchange_by_pricedb_nearest(curbasissum,report_currency,txn_date)
            total_basis.add(report_currency,  curbasissum_report.amount)


            # this is total gain line - as per original
            # ie if sold multiple times in date range we sum those here
            # to get total gain for a stock in the date range

            dont_include = True

            if not dont_include and (include_empty or not units.zero_p()):

                pdb.set_trace()

                # moved to here - must be after the individual split rows

                if (row % 2) == 0:
                    new_row = self.document.StyleSubElement(self.new_table,'normal-row')
                else:
                    new_row = self.document.StyleSubElement(self.new_table,'alternate-row')
                new_row.text = "\n"
                new_row.tail = "\n"

                # the following does gnc:html-account-anchor
                accurl = gnc_html_utilities.account_anchor_text(curacc)

                # need to figure new way to do this
                # original created a list
                # not clear how to do this
                # could try making elements then adding them later?
                # still dont know if can change/add parent to ET elements
                # do I need to - essentially the ET document is creating the
                # equivalent of the activecols list

                new_col = self.document.doc.SubElement(new_row,"td")

                anchor_markup = self.document.doc.SubElement(new_col,"a")
                anchor_markup.attrib['href'] = accurl
                anchor_markup.text = N_(curacc.GetName()) + "\n"
                anchor_markup.tail = "\n"

                #activecols = [anchor_markup]

                # ;; If we're using the txn, warn the user
                if use_txn:
                    if pricing_txn:
                        self.warn_price_dirty = True
                    else:
                        self.warn_no_price = True

                # ;; build a list for the row  based on user selections

                if show_symbol:
                    new_col = self.document.StyleSubElement(new_row,'text-cell')
                    new_col.text = ticker_symbol
                    new_col.tail = "\n"
                    #activecols.append(new_col)

                if show_listing:
                    new_col = self.document.StyleSubElement(new_row,'text-cell')
                    new_col.text = listing
                    new_col.tail = "\n"
                    #activecols.append(new_col)

                new_col = self.document.StyleSubElement(new_row,'text-cell')
                new_col.text = str(txn_date)
                new_col.tail = "\n"
                #activecols.append(new_col)

                if show_shares:
                    new_col = self.document.StyleSubElement(new_row,'number-cell')
                    new_col.text = sw_app_utils.PrintAmount(units,share_print_info)
                    new_col.tail = "\n"
                    #activecols.append(new_col)
                if show_price:
                    new_col = self.document.StyleSubElement(new_row,'number-cell')
                    new_col.tail = "\n"

                    #pdb.set_trace()

                    if use_txn:
                        if pricing_txn:
                            # this does gnc:html-transaction-anchor
                            prcurl = gnc_html_utilities.transaction_anchor_text(pricing_txn)
                            prcstr = price.to_string()
                        else:
                            prcurl = None
                            prcstr = price.to_string()
                    else:
                        # this does gnc:html-price-anchor
                        prcurl = gnc_html_utilities.price_anchor_text(price)
                        prcstr = gnc_commodity_utilities.GncMonetary(price.get_currency(), price.get_value()).to_currency_string()

                    if prcurl != None:
                        anchor_markup = self.document.doc.SubElement(new_col,"a")
                        anchor_markup.attrib['href'] = prcurl
                        anchor_markup.text = prcstr
                        anchor_markup.tail = "\n"
                    else:
                        # this appears to be what code says
                        new_col.text = prcstr

                    #activecols.append(new_col)


                # now add lots more
                if use_txn:
                    if pricing_txn:
                       txtstr = "*"
                    else:
                       txtstr = "**"
                else:
                   txtstr = " "

                new_col = self.document.StyleSubElement(new_row,'text-cell')
                new_col.text = txtstr
                new_col.tail = "\n"

                new_col = self.document.StyleSubElement(new_row,'number-cell')
                new_col.text = gnc_commodity_utilities.GncMonetary(report_currency, self.sum_basis(basis_list,currency_frac)).to_currency_string()
                new_col.tail = "\n"

                new_col = self.document.StyleSubElement(new_row,'number-cell')
                new_col.text = value.to_currency_string()
                new_col.tail = "\n"

                new_col = self.document.StyleSubElement(new_row,'number-cell')
                new_col.text = moneyin.to_currency_string()
                new_col.tail = "\n"

                new_col = self.document.StyleSubElement(new_row,'number-cell')
                new_col.text = moneyout.to_currency_string()
                new_col.tail = "\n"

                new_col = self.document.StyleSubElement(new_row,'number-cell')
                new_col.text = income.to_currency_string()
                new_col.tail = "\n"

                if handle_brokerage_fees != 'ignore-brokerage':

                    new_col = self.document.StyleSubElement(new_row,'number-cell')
                    new_col.text = brokerage.to_currency_string()
                    new_col.tail = "\n"

                new_col = self.document.StyleSubElement(new_row,'number-cell')
                new_col.text = gain.to_currency_string()
                new_col.tail = "\n"

                new_col = self.document.StyleSubElement(new_row,'number-cell')
                new_col.text = gain.to_currency_string()
                new_col.tail = "\n"

            #pdb.set_trace()


        #pdb.set_trace()
        # well scheme clearly returns total-value - because not passed??
        #return total_value
        return


    # these functions are local to renderer function in scheme

    def price_db_latest_fn (self, foreign, domestic, date):

        #pdb.set_trace()

        find_price = self.pricedb.lookup_latest_any_currency(foreign)

        return find_price

    def price_db_nearest_fn (self, foreign, domestic, date):

        #pdb.set_trace()

        #find_price = self.pricedb.lookup_nearest_in_time_any_currency(foreign,timespecCanonicalDayTime(date))
        find_price = self.pricedb.lookup_nearest_in_time_any_currency(foreign,date)

        return find_price


    def renderer (self, report):

        # this actually implements the report look

        # for some reason if do this if any error occurs in report GUI is locked
        #report_starting(self.name)

        #pdb.set_trace()

        # get local values for options

        #optobj = self.options.lookup_name('General','Date')
        #to_date_tp = optobj.get_option_value()

        from_date_tp = None

        optobj = self.options.lookup_name('General','Start Date')
        from_date_tp = optobj.get_option_value()
        optobj = self.options.lookup_name('General','End Date')
        to_date_tp = optobj.get_option_value()

        accobj = self.options.lookup_name('Accounts','Accounts')
        accounts = accobj.get_option_value()

        optobj = self.options.lookup_name('General',"Report's currency")
        report_currency = optobj.get_value()

        optobj = self.options.lookup_name('General','Price Source')
        price_source = optobj.get_option_value()

        rptopt = self.options.lookup_name('General','Report name')
        rptttl = rptopt.get_value()

        optobj = self.options.lookup_name('Accounts','Include accounts with no shares')
        include_empty = optobj.get_value()

        optobj = self.options.lookup_name('Display','Show ticker symbols')
        show_symbol = optobj.get_value()

        optobj = self.options.lookup_name('Display','Show listings')
        show_listing = optobj.get_value()

        optobj = self.options.lookup_name('Display','Show number of shares')
        show_shares = optobj.get_value()

        optobj = self.options.lookup_name('Display','Show prices')
        show_price = optobj.get_value()

        optobj = self.options.lookup_name('Display','Show all transactions')
        show_all = optobj.get_value()

        optobj = self.options.lookup_name('Display','Convert currency all')
        convert_all = optobj.get_value()

        optobj = self.options.lookup_name('General','Basis calculation method')
        basis_method = optobj.get_value()

        optobj = self.options.lookup_name('General','Set preference for price list data')
        prefer_pricelist = optobj.get_value()

        optobj = self.options.lookup_name('General','How to report brokerage fees')
        handle_brokerage_fees = optobj.get_value()


        #optobj = self.options.lookup_name('General','Show Full Account Names')
        #show_full_names = optobj.get_value()

        #optobj = self.options.lookup_name('Accounts','Account Display Depth')
        #display_depth = optobj.get_option_value()

        #shwobj = self.options.lookup_name('Accounts','Always show sub-accounts')
        #shwopt = shwobj.get_value()
        #if shwopt:
        #    subacclst = get_all_subaccounts(accounts)
        #    for subacc in subacclst:
        #        if not AdvancedPortfolio.account_in_list(subacc,accounts):
        #            accounts.append(subacc)


        total_basis    = CommodityCollector()
        total_value    = CommodityCollector()
        total_moneyin  = CommodityCollector()
        total_moneyout = CommodityCollector()
        total_income   = CommodityCollector()
        total_gain     = CommodityCollector() # ;; realized gain
        total_gain_report = CommodityCollector() # ;; realized gain - in report currency
        total_ugain    = CommodityCollector() # ;; unrealized gain
        total_brokerage = CommodityCollector()


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

        self.document.title = rptttl + " - " + N_("%s to %s"%(gnc_print_date(from_date_tp),gnc_print_date(to_date_tp)))


        self.warn_price_dirty = False
        self.warn_no_price = False


        # Scheme uses a whole subclass of functions for dealing with
        # tables - indirectly creating all table elements
        # ignoring all this for now - just using CSS styles
        #self.table = HtmlTable()
        self.new_table = self.document.StyleElement('table')
        self.new_table.text = "\n"

        if len(accounts) > 0:

            # ; at least 1 account selected

            book = sw_app_utils.get_current_book()

            # the primary purpose of this is to store the to_date_tp so when called
            # it converts at exchange rate of to_date_tp - well thats my current analysis
            # not really what we want
            self.exchange_fn = gnc_commodity_utilities.case_exchange_fn(price_source, report_currency, to_date_tp)
            self.pricedb = book.get_price_db()

            if price_source == 'pricedb-latest':
                price_fn = self.price_db_latest_fn
            elif price_source == 'pricedb-nearest':
                price_fn = self.price_db_nearest_fn

            # have to deal with these laters
            headercols = [N_("Account")]

            # this has markup in the scheme
            # we will start - but have to remember to add markup later
            # we could plausibly use ET appending to add an ET list to the document later
            # actually we can because thats hows its programmed in gnc_html_document
            # - problem is we need to update interface to create isolated elements
            totalscols = [N_("Total")]
            #totalscols = [self.document.StyleElementNew('total-label-cell',text=N_("Total"),tail="\n")]

            sum_total_moneyin = GncNumeric(0,1)
            sum_total_income = GncNumeric(0,1)
            sum_total_both_gains = GncNumeric(0,1)
            sum_total_gain = GncNumeric(0,1)
            sum_total_gain_report = GncNumeric(0,1)
            sum_total_ugain = GncNumeric(0,1)
            sum_total_brokerage = GncNumeric(0,1)

            # ;;begin building lists for which columns to display
            if show_symbol:
                headercols.append(N_("Symbol"))
                totalscols.append(N_(" "))

            if show_listing:
                headercols.append(N_("Listing"))
                totalscols.append(N_(" "))

            # add a transaction date column
            headercols.append(N_("Date"))
            totalscols.append(N_(" "))

            if show_shares:
                headercols.append(N_("Shares"))
                totalscols.append(N_(" "))

            if show_price:
                headercols.append(N_("Price"))
                totalscols.append(N_(" "))

            headercols.extend([ " ",
                               N_("Basis"),
                               N_("Value"),
                               N_("Money In"),
                               N_("Money Out"),
                               N_("Income"),
                              ])

            if handle_brokerage_fees != 'ignore-brokerage':
                headercols.append(N_("Brokerage Fees"))

            headercols.append(N_("Realized Gain"))

            headercols.append(N_("Gain Report Currency"))

            totalscols.append(N_(" "))


            new_row = self.document.doc.SubElement(self.new_table,"tr")
            new_row.tail = "\n"

            # this is essentially doing gnc:html-table-set-col-headers
            for colhdr in headercols:
                new_hdr = self.document.doc.SubElement(new_row,"th",attrib={'rowspan' : "1", 'colspan' : "1" })
                new_hdr.text = colhdr
                new_hdr.tail = "\n"

            #pdb.set_trace()


            self.table_add_stock_rows(accounts, to_date_tp, from_date_tp, report_currency, self.exchange_fn, price_fn,
                 price_source, include_empty, show_symbol, show_listing, show_shares, show_price, show_all, convert_all,
                 basis_method, prefer_pricelist, handle_brokerage_fees,
                 total_basis, total_value, total_moneyin, total_moneyout, total_income, total_gain, total_ugain, total_brokerage, total_gain_report)

            #pdb.set_trace()

            sum_total_moneyin = total_moneyin.sum(report_currency, self.exchange_fn.run)
            sum_total_income = total_income.sum(report_currency, self.exchange_fn.run)
            sum_total_gain = total_gain.sum(report_currency, self.exchange_fn.run)
            sum_total_gain_report = total_gain_report.sum(report_currency, self.exchange_fn.run)
            sum_total_brokerage = total_brokerage.sum(report_currency, self.exchange_fn.run)


            #(gnc:make-html-table-cell/size 1 17 (gnc:make-html-text (gnc:html-markup-hr)))
            # this is labelled grand-total for some reason - just draws a line
            new_row = self.document.doc.SubElement(self.new_table,"tr")
            new_row.tail = "\n"
            new_data = self.document.doc.SubElement(new_row,"td",attrib={'rowspan' : "1", 'colspan' : "17" })
            new_ruler = self.document.doc.SubElement(new_data,"hr")


            #pdb.set_trace()

            # do the totals row explicitly

            new_row = self.document.doc.SubElement(self.new_table,"tr")
            new_row.text = "\n"
            new_row.tail = "\n"

            new_col = self.document.StyleSubElement(new_row,'total-label-cell')
            new_col.text = N_("Total")

            for itm in totalscols[1:]:
                new_col = self.document.StyleSubElement(new_row,'total-label-cell')
                new_col.text = itm

            #pdb.set_trace()

            new_col = self.document.StyleSubElement(new_row,'total-number-cell')
            new_col.text = total_basis.sum(report_currency, self.exchange_fn.run).to_currency_string()
            new_col.tail = "\n"

            new_col = self.document.StyleSubElement(new_row,'total-number-cell')
            new_col.text = total_value.sum(report_currency, self.exchange_fn.run).to_currency_string()
            new_col.tail = "\n"

            new_col = self.document.StyleSubElement(new_row,'total-number-cell')
            new_col.text = sum_total_moneyin.to_currency_string()
            new_col.tail = "\n"

            new_col = self.document.StyleSubElement(new_row,'total-number-cell')
            new_col.text = total_moneyout.sum(report_currency, self.exchange_fn.run).to_currency_string()
            new_col.tail = "\n"

            new_col = self.document.StyleSubElement(new_row,'total-number-cell')
            new_col.text = sum_total_income.to_currency_string()
            new_col.tail = "\n"

            if handle_brokerage_fees != 'ignore-brokerage':

               new_col = self.document.StyleSubElement(new_row,'total-number-cell')
               new_col.text = sum_total_brokerage.to_currency_string()
               new_col.tail = "\n"

            new_col = self.document.StyleSubElement(new_row,'total-number-cell')
            new_col.text = sum_total_gain.to_currency_string()
            new_col.tail = "\n"

            new_col = self.document.StyleSubElement(new_row,'total-number-cell')
            new_col.text = sum_total_gain_report.to_currency_string()
            new_col.tail = "\n"


            # add row for the joint contribution

            new_row = self.document.doc.SubElement(self.new_table,"tr")
            new_row.text = "\n"
            new_row.tail = "\n"

            new_col = self.document.StyleSubElement(new_row,'total-label-cell')
            new_col.text = N_("Joint Contribution")

            for itm in totalscols[1:]:
                new_col = self.document.StyleSubElement(new_row,'total-label-cell')
                new_col.text = itm

            pdb.set_trace()

            new_col = self.document.StyleSubElement(new_row,'total-number-cell')
            new_num = total_basis.sum(report_currency, self.exchange_fn.run)
            new_num.amount = new_num.amount.div(GncNumeric(2,1),GNC_DENOM_AUTO,GNC_HOW_DENOM_SIGFIG | 5*256 | GNC_HOW_RND_ROUND)
            new_col.text = new_num.to_currency_string()
            new_col.tail = "\n"

            new_col = self.document.StyleSubElement(new_row,'total-number-cell')
            new_num = total_value.sum(report_currency, self.exchange_fn.run)
            new_num.amount = new_num.amount.div(GncNumeric(2,1),GNC_DENOM_AUTO,GNC_HOW_DENOM_SIGFIG | 5*256 | GNC_HOW_RND_ROUND)
            new_col.text = new_num.to_currency_string()
            new_col.tail = "\n"

            new_col = self.document.StyleSubElement(new_row,'total-number-cell')
            new_num.amount = sum_total_moneyin.amount.div(GncNumeric(2,1),GNC_DENOM_AUTO,GNC_HOW_DENOM_SIGFIG | 5*256 | GNC_HOW_RND_ROUND)
            new_col.text = new_num.to_currency_string()
            new_col.tail = "\n"

            new_col = self.document.StyleSubElement(new_row,'total-number-cell')
            new_num = total_moneyout.sum(report_currency, self.exchange_fn.run)
            new_num.amount = new_num.amount.div(GncNumeric(2,1),GNC_DENOM_AUTO,GNC_HOW_DENOM_SIGFIG | 5*256 | GNC_HOW_RND_ROUND)
            new_col.text = new_num.to_currency_string()
            new_col.tail = "\n"

            new_col = self.document.StyleSubElement(new_row,'total-number-cell')
            new_num.amount = sum_total_income.amount.div(GncNumeric(2,1),GNC_DENOM_AUTO,GNC_HOW_DENOM_SIGFIG | 5*256 | GNC_HOW_RND_ROUND)
            new_col.text = new_num.to_currency_string()
            new_col.tail = "\n"

            if handle_brokerage_fees != 'ignore-brokerage':

               new_col = self.document.StyleSubElement(new_row,'total-number-cell')
               new_num.amount = sum_total_brokerage.amount.div(GncNumeric(2,1),GNC_DENOM_AUTO,GNC_HOW_DENOM_SIGFIG | 5*256 | GNC_HOW_RND_ROUND)
               new_col.text = new_num.to_currency_string()
               new_col.tail = "\n"

            new_col = self.document.StyleSubElement(new_row,'total-number-cell')
            new_num.amount = sum_total_gain.amount.div(GncNumeric(2,1),GNC_DENOM_AUTO,GNC_HOW_DENOM_SIGFIG | 5*256 | GNC_HOW_RND_ROUND)
            new_col.text = new_num.to_currency_string()
            new_col.tail = "\n"

            new_col = self.document.StyleSubElement(new_row,'total-number-cell')
            new_num.amount = sum_total_gain_report.amount.div(GncNumeric(2,1),GNC_DENOM_AUTO,GNC_HOW_DENOM_SIGFIG | 5*256 | GNC_HOW_RND_ROUND)
            new_col.text = new_num.to_currency_string()
            new_col.tail = "\n"


            if self.warn_price_dirty:

                new_col = self.document.doc.SubElement("")
                new_col.text = N_("* this commodity data was built using transaction pricing instead of the price list.")
                new_col.tail = "\n"

                new_col = self.document.doc.SubElement("br")
                new_col.text = ""
                new_col.tail = "\n"

                new_col = self.document.doc.SubElement("")
                new_col.text = N_("If you are in a multi-currency situation, the exchanges may not be correct.")
                new_col.tail = "\n"


            if self.warn_price_dirty:

                new_col = self.document.doc.SubElement("")
                new_col.text = N_("* this commodity data was built using transaction pricing instead of the price list.")
                new_col.tail = "\n"

                new_col = self.document.doc.SubElement("br")
                new_col.text = ""
                new_col.tail = "\n"

                new_col = self.document.doc.SubElement("")
                new_col.text = N_("If you are in a multi-currency situation, the exchanges may not be correct.")
                new_col.tail = "\n"

            if self.warn_no_price:

                new_col = self.document.doc.SubElement("br")
                new_col.text = ""
                new_col.tail = "\n"

                new_col = self.document.doc.SubElement("")
                new_col.text = N_("** this commodity has no price and a price of 1 has been used.")
                new_col.tail = "\n"


        else:

            pdb.set_trace()

            self.make_no_account_warning(rptttl, self.report_guid)


        report_finished()

        return self.document


    def make_no_account_warning (self, report_title_string, report_id):

        self.make_generic_warning(report_title_string, report_id, 
                         N_("No accounts selected"),N_("This report requires accounts to be selected in the report options."))


    def make_generic_warning (self, report_title_string, report_id, warning_title_string, warning_string):

        new_elm = self.document.doc.SubElement("h2")
        new_elm.text = N_(report_title_string) + ":"
        new_elm.tail = "\n"

        new_elm = self.document.doc.SubElement("h2")
        new_elm.text = N_(warning_title_string)
        new_elm.tail = "\n"

        new_elm = self.document.doc.SubElement("p")
        new_elm.text = N_(warning_string)
        new_elm.tail = "\n"

        # this is makes a link
        # the url not correctly implemented yet
        new_elm = self.document.doc.SubElement("a")
        new_elm.attrib['href'] = "report-id=%s"%report_id
        new_elm.text = N_("Edit report options")
        new_elm.tail = "\n"

        

