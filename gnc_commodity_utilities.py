
import pdb


import gnucash

from gnucash import GNC_DENOM_AUTO, GNC_HOW_RND_ROUND
from gnucash.gnucash_core_c import GNC_HOW_DENOM_SIGFIG


#import gnucash_ext

import sw_app_utils

import gnucash_log


# we may not import gnc_report_utilities in here!!
# can get circular imports

class ExchangeCost(object):

    def __init__ (self, report_commodity, end_date):

        pass
        #for exvl in 

    def make_alist (self, e):

       exch_val = e[1][0].total.div(e[1][1].total, GNC_DENOM_AUTO, GNC_HOW_DENOM_SIGFIG | 8*256 | GNC_HOW_RND_ROUND)
       newlst = [ e[0], exch_val ]

    def get_all_commodity_splits (self, currency_accounts, end_date_tp):

        retval = match_commodity_splits(currency_accounts, end_date_tp, None)

    def exchange_cost_totals (self, report_commodity, end_date):

       # ;; sumlist: a multilevel alist. Each element has a commodity
       # ;; as key, and another alist as a value. The value-alist's
       # ;; elements consist of a commodity as a key, and a pair of two
       # ;; value-collectors as value, e.g. with only one (the report-)
       # ;; commodity DEM in the outer alist: ( {DEM ( [USD (400 .
       # ;; 1000)] [FRF (300 . 100)] ) } ) where DEM,USD,FRF are
       # ;; <gnc:commodity> and the numbers are a numeric-collector
       # ;; which in turn store a <gnc:numeric>. In the example, USD
       # ;; 400 were bought for an amount of DEM 1000, FRF 300 were
       # ;; bought for DEM 100. The reason for the outer alist is that
       # ;; there might be commodity transactions which do not involve
       # ;; the report-commodity, but which can still be calculated
       # ;; after *all* transactions are processed.

       curr_accts = sw_app_utils.get_current_root_account().get_descendants_sorted()

       sumlist = [ [report_commodity, [] ] ]

       if len(curr_accts) > 0:

           all_splts =  []

           for acct in curr_accts:
               pass

    def exchange_cost_totals (self, report_commodity, end_date):

        pass



class ExchangeFn(object):

    def __init__ (self):
        self.run = self.exchange_fn

class AverageExchangeFn(ExchangeFn):

    def __init__ (self, exchange_alist=None):
        super(AverageExchangeFn,self).__init__()
        self.exchange_alist = exchange_alist

    def exchange_fn (self, foreign, domestic):

        # the arguments seem to be currency commodities

        gnucash_log.PDEBUG("python","foreign: %s"%str(foreign))
        gnucash_log.PDEBUG("python","domestic: %s"%domestic.get_printname())

        if foreign != None:

            if exchange_by_euro(foreign,domestic):
                return
            if exchange_if_same(foreign,domestic):
                return

class WeightedAverageFn(ExchangeFn):

    def __init__ (self, exchange_alist=None):
        super(WeightedAverageFn,self).__init__()
        self.exchange_alist = exchange_alist

    def exchange_fn (self, foreign, domestic):
        pdb.set_trace()


class PriceDBLatestFn(ExchangeFn):

    # not right - defined in pricedb somewhere

    def __init__ (self, exchange_alist=None):
        super(PriceDBLatestFn,self).__init__()
        self.exchange_alist = exchange_alist

    def exchange_fn (self, foreign, domestic):
        pdb.set_trace()

class PriceDBNearestFn(ExchangeFn):

    # not right - defined in pricedb somewhere

    def __init__ (self, exchange_alist=None):
        super(PriceDBNearestFn,self).__init__()
        self.exchange_alist = exchange_alist

    def exchange_fn (self, foreign, domestic):
        pdb.set_trace()


class ExchangeTimeFn(object):

    def __init__ (self):
        self.run = self.lambda_exchange_fn


class AverageExchangeTimeFn(ExchangeTimeFn):

    def __init__ (self, exchange_alist=None):
        super(AverageExchangeTimeFn,self).__init__()
        self.exchange_alist = exchange_alist

    def exchange_fn (self, foreign, domestic):

        # the arguments seem to be currency commodities

        gnucash_log.PDEBUG("python","foreign: %s"%str(foreign))
        gnucash_log.PDEBUG("python","domestic: %s"%domestic.get_printname())

        self.exchange_cost = ExchangeCost()
        #def __init__ (self, report_commodity, end_date):

    def lambda_exchange_fn (self, foreign, domestic, date):

        self.exchange_fn(foreign,domestic)


class WeightedAverageTimeFn(ExchangeTimeFn):

    def __init__ (self, exchange_alist=None):
        super(WeightedAverageTimeFn,self).__init__()
        self.exchange_alist = exchange_alist
        self.run = self.lambda_exchange_fn

    def exchange_fn (self, foreign, domestic):

        # the arguments seem to be currency commodities

        gnucash_log.PDEBUG("python","foreign: %s"%str(foreign))
        gnucash_log.PDEBUG("python","domestic: %s"%domestic.get_printname())

        self.exchange_cost = ExchangeCost()

    def lambda_exchange_fn (self, foreign, domestic, date):

        self.exchange_fn(foreign,domestic)

class ActualTransactionsTimeFn(ExchangeTimeFn):

    def __init__ (self, exchange_alist=None):
        super(ActualTransactionsTimeFn,self).__init__()
        self.exchange_alist = exchange_alist

    def exchange_fn (self, foreign, domestic):

        # the arguments seem to be currency commodities

        gnucash_log.PDEBUG("python","foreign: %s"%str(foreign))
        gnucash_log.PDEBUG("python","domestic: %s"%domestic.get_printname())

        self.exchange_cost = ExchangeCost()

    def lambda_exchange_fn (self, foreign, domestic, date):

        self.exchange_fn(foreign,domestic)

class PriceDBLatestTimeFn(ExchangeTimeFn):

    def __init__ (self, exchange_alist=None):
        super(PriceDBLatestTimeFn,self).__init__()
        self.exchange_alist = exchange_alist

    def exchange_fn (self, foreign, domestic):

        # the arguments seem to be currency commodities

        gnucash_log.PDEBUG("python","foreign: %s"%str(foreign))
        gnucash_log.PDEBUG("python","domestic: %s"%domestic.get_printname())

        self.exchange_cost = ExchangeCost()

    def lambda_exchange_fn (self, foreign, domestic, date):

        self.exchange_fn(foreign,domestic)

class PriceDBNearestTimeFn(ExchangeTimeFn):

    def __init__ (self, exchange_alist=None):
        super(PriceDBNearestTimeFn,self).__init__()
        self.exchange_alist = exchange_alist

    def lambda_exchange_fn (self, foreign, domestic, date):

        # ;; Yet another ready-to-use function for calculation of exchange
        # ;; rates. (Note that this is already the function itself. It doesn't
        # ;; return a function as opposed to make-exchange-function.) It takes
        # ;; the <gnc-monetary> 'foreign' amount, the <gnc:commodity*>
        # ;; 'domestic' commodity *and* a <gnc:time-pair> 'date'. It exchanges
        # ;; the amount into the domestic currency, using a price from the
        # ;; pricedb according to the given date. The function returns a
        # ;; <gnc-monetary>.

        gnucash_log.PDEBUG("python","foreign: %s"%str(foreign))
        gnucash_log.PDEBUG("python","domestic: %s"%domestic.get_printname())

        dommon = None

        if isinstance(foreign,GncMonetary) and date != None:

            dommon = exchange_by_euro(foreign, domestic, date)
            if dommon == None:
                dommon = exchange_if_same(foreign, domestic)
                if dommon == None:
                    pdb.set_trace()
                    prcdb = sw_app_utils.get_current_book().get_price_db()
                    nrval = prcdb.convert_balance_nearest_price( \
                        foreign.amount,foreign.commodity,domestic,date)
                    dommon = GncMonetary(domestic,nrval)

        return dommon


def match_commodity_splits (currency_accounts, end_date_tp, commodity=None):

    pdb.set_trace()

    qry = qnucash.Query()

    qry.set_book(sw_app_utils.get_current_book())

    set_match_non_voids_only(qry,sw_app_utils.get_current_book())

    qry.search_for(Book.GNC_ID_BUDGET)

    bdgtlst = qry.Run(GncBudget)


def set_match_non_voids_only (query, book):

    pdb.set_trace()

    tmpqry = qry.create_for(Book.GNC_ID_SPLIT)

    tmpqry.set_book(book)

    tmpqry.AddClearedMatch(gnucash.CLEARED-VOIDED,gnucash.QOF_QUERY_AND)

    invqry = tmpqry.invert()

    query.merge_in_place(invqry,gnucash.QOF_QUERY_AND)

    # do we need these??
    #invqry.destroy()
    #tmpqry.destroy()



def exchange_if_same (foreign, domestic):
    # ;; A trivial exchange function - if the "foreign" monetary amount
    # ;; and the domestic currency are the same, return the foreign
    # ;; amount unchanged, otherwise return 0
    # ;; WARNING: many uses of exchange functions assume that the function
    # ;; will return a valid <gnc:monetary>.  However, this function returns
    # ;; #f if the commodities don't match.  Therefore, if you use this
    # ;; function in a mixed commodity context, stuff will probably crash.
    #pdb.set_trace()
    if foreign.commodity.equiv(domestic):
        return foreign
    return None


def exchange_by_euro (foreign, domestic, date):

    #pdb.set_trace()

    if sw_app_utils.is_euro_currency(domestic) and \
        sw_app_utils.is_euro_currency(foreign.commodity):
        euro_val = convert_to_euro(foreign.commodity, foreign.amount)
        dom_val = convert_from_euro(domestic)
        dommon = GncMonetary(domestic,dom_val)
        return dommon
    return None

def case_exchange_fn (source_option, report_currency, to_date_tp):

    pdb.set_trace()

    if source_option == 'average-cost':
        exchange_fn = AverageExchangeFn()
    elif source_option == 'weighted-average':
        exchange_fn = WeightedAverageFn()
    elif source_option == 'pricedb-latest':
        exchange_fn = PriceDBLatestFn()
    elif source_option == 'pricedb-nearest':
        exchange_fn = PriceDBNearestFn()

    return exchange_fn

def case_exchange_time_fn (source_option, report_currency, commodity_list, to_date_tp, start_percent, delta_percent):

    pdb.set_trace()

    if source_option == 'average-cost':
        exchange_fn = AverageExchangeTimeFn()
    elif source_option == 'weighted-average':
        exchange_fn = WeightedAverageTimeFn()
    elif source_option == 'actual-transactions':
        exchange_fn = ActualTransactionsTimeFn()
    elif source_option == 'pricedb-latest':
        exchange_fn = PriceDBLatestTimeFn()
    elif source_option == 'pricedb-nearest':
        exchange_fn = PriceDBNearestTimeFn()

    return exchange_fn


class GncMonetary(object):

    def __init__ (self, commodity, amount):
        if isinstance(amount,gnucash.GncNumeric):
            self.commodity = commodity
            self.amount = amount
        else:
            #warn "wrong arguments for gnc:make-gnc-monetary: " c a)
            pdb.set_trace()

    # this or a class method??
    def neg (self):
        newgncmon = self.__class__(self.commodity,self.amount.neg())
        return newgncmon

    # this is defined in html-style-info.scm
    # where should this go???
    def to_currency_string (self):
        #pdb.set_trace()
        prtinfo = sw_app_utils.CommodityPrintInfo(self.commodity,True)
        prtstr = sw_app_utils.PrintAmount(self.amount,prtinfo)
	return prtstr

