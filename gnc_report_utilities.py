

# this is implementations of functions in report-utilities.scm


import pdb


import gnucash

from gnucash import GncNumeric

# we need to import this so that various classes are extended
# still not sure I need this here - as long as done once isnt this OK? 
import gnucash_ext 

import sw_app_utils


import gnome_utils_ctypes

import gnucash_log

import gnc_commodity_utilities

import engine_ctypes


# define a function equivalent to N_ for internationalization
def N_(msg):
    return msg


def report_starting (report_name):
  gnome_utils_ctypes.libgnc_gnomeutils.gnc_window_show_progress(N_("Building '%s' report ..."%report_name), 0.0)

def report_render_starting (report_name):
  if report_name == None or report_name == "":
      rptnam = "Untitled"
  else:
      rptnam = report_name
  gnome_utils_ctypes.libgnc_gnomeutils.gnc_window_show_progress(N_("Rendering '%s' report ..."%rptnam), 0)

def report_percent_done (percent):
  if percent > 100.0:
      #(gnc:warn "report more than 100% finished. " percent))
      pass
  gnome_utils_ctypes.libgnc_gnomeutils.gnc_window_show_progress("", percent)

def report_finished():
  gnome_utils_ctypes.libgnc_gnomeutils.gnc_window_show_progress("", -1.0)



def accounts_count_splits (accounts):
    cntsplt = 0
    for acc in accounts:
        lngth = len(acc.GetSplitList())
        cntsplt += lngth
    return cntsplt


def account_get_balance_at_date (account, date, include_children=False):
    collector = account_get_comm_balance_at_date(account, date, include_children)

def account_get_comm_balance_at_date (account, date, include_children=False):

    #pdb.set_trace()

    balance_collector = CommodityCollector()

    if include_children:
        # gnc:account-map-descendants
        for chld in account.GetDescendants():
            balval = account_get_comm_balance_at_date(chld,date,False)
            balance_collector.merge(balval)

    curbook = sw_app_utils.get_current_book()
    tmpqry = gnucash.Query.CreateFor(curbook.GNC_ID_SPLIT)
    tmpqry.set_book(curbook)
    #tmpqry.AddSingleAccountMatch(account,gnucash.QOF_QUERY_AND)
    #tmpqry.AddDateMatchTS(False,date,True,date,gnucash.QOF_QUERY_AND)
    engine_ctypes.AddSingleAccountMatch(tmpqry,account,gnucash.QOF_QUERY_AND)
    engine_ctypes.AddDateMatchTS(tmpqry,False,date,True,date,gnucash.QOF_QUERY_AND)
    #query.merge_in_place(invqry,gnucash.QOF_QUERY_AND)
    tmpqry.set_sort_order([gnucash.gnucash_core_c.SPLIT_TRANS,gnucash.gnucash_core_c.TRANS_DATE_POSTED],[gnucash.gnucash_core_c.QUERY_DEFAULT_SORT],[])
    tmpqry.set_sort_increasing(True,True,True)
    tmpqry.set_max_results(1)
    splitlst = tmpqry.Run(gnucash.Split)

    # do we need these??
    #invqry.destroy()
    #tmpqry.destroy()

    # by set_max_results there is only 1 split returned I think
    if len(splitlst) > 0:
        balance_collector.add(account.GetCommodity(),splitlst[0].GetBalance())

    return balance_collector


def get_commodities (accountlst, exclude_commodity=None):
    #pdb.set_trace()
    newdct = {}
    for acc in accountlst:
        comod = acc.GetCommodity()
        comnm = comod.get_mnemonic()
        if not comnm in newdct:
            newdct[comod] = acc
    if exclude_commodity != None:
        if exclude_commodity in newdct:
            del newdct[exclude_commodity]
    return sorted(newdct.keys())


def get_all_subaccounts (accountlst):
    # do we add incoming accounts??
    #pdb.set_trace()
    newlst = []
    for acc in accountlst:
        subacc = acc.get_descendants_sorted()
        newlst.extend(subacc)
    return newlst

def filter_accountlist_type (typelist, accounts):
    #pdb.set_trace()
    # is this faster than scanning the list
    # in python we can say if acc.GetType() in typelist
    typedict = {}
    for acctyp in typelist:
        typedict[acctyp] = 1
    retlst = []
    for acc in accounts:
        if acc.GetType() in typedict:
            retlst.append(acc)
    return retlst


def monetary_to_string (value):
    sw_app_utils.PrintAmount


# so the class based way would be to make CommodityCollector
# a base function I think and the specific types

class Collector(object):

    def __init__ (self):
        pass


class DrcrCollector(Collector):

    def __init__ (self):
        pass

    #     ((add) (adder value))
    #     ((debits) (getdebits))
    #     ((credits) (getcredits))
    #     ((items) (getitems))
    #     ((reset) (reset-all))

    def add (self, value):
        self.gnc_total += value


class NumericCollector(Collector):

    def __init__ (self):
        self.gnc_total = GncNumeric(0)

    #     ((add) (adder value))
    #     ((debits) (getdebits))
    #     ((credits) (getcredits))
    #     ((items) (getitems))
    #     ((reset) (reset-all))

    def add (self, amount):
        if isinstance(amount,GncNumeric):
            self.gnc_total = self.gnc_total.add(amount,gnucash.GNC_DENOM_AUTO, gnucash.GNC_HOW_DENOM_LCD)
        else:
            gnucash_log.PWARN("gnc.python","gnc:numeric-collector called with wrong argument: %s"%amount)

    def total (self):
        return self.gnc_total


class CommodityCollector(object):

    def __init__ (self):
        self.commoditylist = {}

    def add_commodity_value (self, commodity, value):

        #pdb.set_trace()

        # ah - understanding - we maintain a separate collector
        # for each commodity - so we simply can sum the individual commodity
        # values - only need exchange rates for a final total
        if not commodity.get_unique_name() in self.commoditylist:
            cmdpr = [commodity, NumericCollector()]
            self.commoditylist[commodity.get_unique_name()] = cmdpr
        else:
            cmdpr = self.commoditylist[commodity.get_unique_name()]

        cmdpr[1].add(value)

    def add_commodity_clist (self, clist):
        for cmdpr in clist.values():
            self.add_commodity_value(cmdpr[0],cmdpr[1].total())

    def minus_commodity_clist (self, clist):
        for cmdpr in clist.values():
            self.add_commodity_value(cmdpr[0],cmdpr[1].total().neg())

    def process_commodity_list (self, fn):
        #pdb.set_trace()
        for pair in self.commoditylist.values():
            fn(pair[0], pair[1].total())


    # ;; The functions:
    # ;;   'add <commodity> <amount>: Add the given amount to the
    # ;;       appropriate currencies' total balance.
    # ;;   'format <fn> #f: Call the function <fn> (where fn takes two
    # ;;       arguments) for each commodity with the arguments <commodity>
    # ;;       and the corresponding total <amount>. The results is a list
    # ;;       of each call's result.
    # ;;   'merge <commodity-collector> #f: Merge the given other
    # ;;       commodity-collector into this one, adding all currencies'
    # ;;       balances, respectively.
    # ;;   'minusmerge <commodity-collector> #f: Merge the given other
    # ;;       commodity-collector into this one (like above) but subtract
    # ;;       the other's currencies' balance from this one's balance,
    # ;;       respectively.
    # ;;   'reset #f #f: Delete everything that has been accumulated
    # ;;       (even the fact that any commodity showed up at all).
    # ;;   'getpair <commodity> signreverse?: Returns the two-element-list
    # ;;       with the <commodity> and its corresponding balance. If
    # ;;       <commodity> doesn't exist, the balance will be
    # ;;       (gnc-numeric-zero). If signreverse? is true, the result's
    # ;;       sign will be reversed.

    # OK this is stupid -  the primary functions just call another function
    # (in scheme there is a switch table in a single function

    # also because some functions have 2 arguments all functions in scheme have to have 2 arguments
    # hence often see the merge function with a #f second argument - which is actually not used
    # by the merge function
    # - in python just have function directly so dont need 2nd argument

    # scheme variable is commodity - but it seems to be a collector list
    # ok - looks like different things for different functions

    def add (self, commodity, amount):
        self.add_commodity_value(commodity,amount)

    def merge (self, commodity_list): 
        self.add_commodity_clist(commodity_list.commoditylist)

    def minusmerge (self, commodity_list): 
        self.minus_commodity_clist(commodity_list.commoditylist)

    def format (self, commodity_fn):
        # hmm - commodity doesnt appear to be a commodity but a function??
        self.process_commodity_list(commodity_fn)

    def reset (self):
        self.commoditylist = {}

    def getpair (self, commod, sign=False):
        #pdb.set_trace()
        # ah - it looks up c in commoditylist
        # (pair (assoc c commoditylist))
        # the scheme code seems to return as second item a list of GncNumeric and empty list
	if commod.get_unique_name() in self.commoditylist:
            tmpcmdpr = self.commoditylist[commod.get_unique_name()]
            if sign:
                tmpval = tmpcmdpr[1].total().neg()
            else:
                tmpval = tmpcmdpr[1].total()
            return [commod, tmpval]
        else:
            return [commod, GncNumeric(0,1)]


    # these are separate definitions in scheme but would seem to be in this
    # class as all take collector as 1st argument
    def map (self, commodity_fn):
        self.format(commodity_fn)

    def assoc (self, commodity, sign=False):
        return self.getmonetary(commodity,sign)

    def assoc_pair (self, commodity, sign=False):
        return self.getpair(commodity,sign)


    # Im really confused here - not sorted out what objects are what
    # - in scheme the arguments are not consistent - commodity/currency/commoditycollector

    def getmonetary (self, curr, sign=False):

        #pdb.set_trace()

        # what is this doing?
        # ah - it looks up c in commoditylist
        # (pair (assoc c commoditylist))

        if curr.get_unique_name() in self.commoditylist:
            tmpcmdpr = self.commoditylist[curr.get_unique_name()]
            if sign:
                tmpval = tmpcmdpr[1].total().neg()
            else:
                tmpval = tmpcmdpr[1].total()
        else:
            tmpval = GncNumeric(0,1)

        getval = gnc_commodity_utilities.GncMonetary(curr,tmpval)

        return getval


    def sum (self, report_currency, exchange_fn): 
        #pdb.set_trace()
        sumcmd = sum_collector_commodity(self, report_currency, exchange_fn)
        return sumcmd


def sum_collector_commodity (foreign_commodityclctr, domestic, exchange_fn):

    #pdb.set_trace()

    balance = CommodityCollector()

    def commodity_fn (curr, val):
        if curr.equiv(domestic):
            balance.add(domestic,val)
        else:
            tmpval = exchange_fn(gnc_commodity_utilities.GncMonetary(curr,val), domestic)
            balance.add(domestic,tmpval.amount)

    foreign_commodityclctr.format(commodity_fn)

    sumval = balance.getmonetary(domestic)

    #print "sum collector total",sumval.amount.to_string()

    return sumval

