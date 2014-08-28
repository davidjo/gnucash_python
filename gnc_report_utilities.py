

import pdb


import gnucash

from gnucash import GncNumeric


import gnome_utils_ctypes

import gnucash_log

import gnc_commodity_utilities


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

def get_all_subaccounts (accountlst):
    # do we add incoming accounts??
    pdb.set_trace()
    newlst = []
    for acc in accountlist:
        subacc = acc.get_descendents_sorted()
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


    def sum (self, report_currency, exchange_fn): 
        #pdb.set_trace()
        sumcmd = sum_collector_commodity(self, report_currency, exchange_fn)
        return sumcmd

    # Im really confused here - not sorted out what objects are what
    # - in scheme the arguments are not consistent - commodity/currency/commoditycollector

    def getmonetary (self, curr, sign=False):

        #pdb.set_trace()

        # what is this doing?
        # ah - it looks up c in commoditylist
        # (pair (assoc c commoditylist))

        if curr.get_unique_name() in self.commoditylist:
            if sign:
                tmpcmdpr = self.commoditylist[curr.get_unique_name()]
                tmpval = tmpcmdpr[1].total().neg()
            else:
                tmpcmdpr = self.commoditylist[curr.get_unique_name()]
                tmpval = tmpcmdpr[1].total()
        else:
            tmpval = GncNumeric(0,1)

        getval = gnc_commodity_utilities.GncMonetary(curr,tmpval)

        return getval


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

