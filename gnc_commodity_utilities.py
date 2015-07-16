
import pdb


import gnucash

from gnucash import GNC_DENOM_AUTO, GNC_HOW_RND_ROUND
from gnucash.gnucash_core_c import GNC_HOW_DENOM_SIGFIG


#import gnucash_ext

import sw_app_utils

import engine_ctypes

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

    def __init__ (self, date=None):
        self.date = date
        self.run = self.lambda_exchange_fn

class AverageCostFn(ExchangeFn):

    def __init__ (self, date, exchange_alist=None):
        super(AverageCostFn,self).__init__(date)
        self.exchange_alist = exchange_alist

    def exchange_fn (self, foreign, domestic):

        # the arguments seem to be currency commodities

        gnucash_log.PDEBUG("python","foreign: %s"%str(foreign))
        gnucash_log.PDEBUG("python","domestic: %s"%domestic.get_printname())

        # not implemented
        pdb.set_trace()

    def lambda_exchange_fn (self, foreign, domestic):
        return self.exchange_fn(foreign, domestic)


class WeightedAverageFn(ExchangeFn):

    def __init__ (self, date, exchange_alist=None):
        super(WeightedAverageFn,self).__init__(date)
        self.exchange_alist = exchange_alist

    def exchange_fn (self, foreign, domestic):
        # not implemented
        pdb.set_trace()

    def lambda_exchange_fn (self, foreign, domestic):
        return self.exchange_fn(foreign, domestic)


class PriceDBLatestFn(ExchangeFn):

    def __init__ (self, date, exchange_alist=None):
        super(PriceDBLatestFn,self).__init__(date)
        self.exchange_alist = exchange_alist

    def lambda_exchange_fn (self, foreign, domestic):
        #pdb.set_trace()
        return exchange_by_pricedb_latest(foreign, domestic)

class PriceDBNearestFn(ExchangeFn):

    def __init__ (self, date, exchange_alist=None):
        super(PriceDBNearestFn,self).__init__(date)
        self.exchange_alist = exchange_alist

    def lambda_exchange_fn (self, foreign, domestic):
        #pdb.set_trace()
        return exchange_by_pricedb_nearest(foreign, domestic, self.date)


class ExchangeTimeFn(object):

    def __init__ (self, date):
        self.date = date
        self.run = self.lambda_exchange_fn


class AverageExchangeTimeFn(ExchangeTimeFn):

    def __init__ (self, date, exchange_alist=None):
        super(AverageExchangeTimeFn,self).__init__(date)
        self.exchange_alist = exchange_alist

    def exchange_fn (self, foreign, domestic):

        # the arguments seem to be currency commodities

        gnucash_log.PDEBUG("python","foreign: %s"%str(foreign))
        gnucash_log.PDEBUG("python","domestic: %s"%domestic.get_printname())

        self.exchange_cost = ExchangeCost()

        # not fully implemented
        pdb.set_trace()

    def lambda_exchange_fn (self, foreign, domestic, date):

        self.exchange_fn(foreign,domestic)


class WeightedAverageTimeFn(ExchangeTimeFn):

    def __init__ (self, date, exchange_alist=None):
        super(WeightedAverageTimeFn,self).__init__(date)
        self.exchange_alist = exchange_alist

    def lambda_exchange_fn (self, foreign, domestic, date):

        # the arguments seem to be currency commodities

        gnucash_log.PDEBUG("python","foreign: %s"%str(foreign))
        gnucash_log.PDEBUG("python","domestic: %s"%domestic.get_printname())

        # not implemented
        pdb.set_trace()


class ActualTransactionsTimeFn(ExchangeTimeFn):

    def __init__ (self, date, exchange_alist=None):
        super(ActualTransactionsTimeFn,self).__init__(date)
        self.exchange_alist = exchange_alist

    def lambda_exchange_fn (self, foreign, domestic, date):

        # the arguments seem to be currency commodities

        gnucash_log.PDEBUG("python","foreign: %s"%str(foreign))
        gnucash_log.PDEBUG("python","domestic: %s"%domestic.get_printname())

        # not implemented
        pdb.set_trace()


class PriceDBLatestTimeFn(ExchangeTimeFn):

    def __init__ (self, date, exchange_alist=None):
        super(PriceDBLatestTimeFn,self).__init__(date)
        self.exchange_alist = exchange_alist

    def lambda_exchange_fn (self, foreign, domestic, date):

        # the arguments seem to be currency commodities

        gnucash_log.PDEBUG("python","foreign: %s"%str(foreign))
        gnucash_log.PDEBUG("python","domestic: %s"%domestic.get_printname())

        return exchange_by_pricedb_latest(foreign, domestic)


class PriceDBNearestTimeFn(ExchangeTimeFn):

    def __init__ (self, date, exchange_alist=None):
        super(PriceDBNearestTimeFn,self).__init__(date)
        self.exchange_alist = exchange_alist

    def lambda_exchange_fn (self, foreign, domestic, date):

        # the arguments seem to be currency commodities

        gnucash_log.PDEBUG("python","foreign: %s"%str(foreign))
        gnucash_log.PDEBUG("python","domestic: %s"%domestic.get_printname())

        return exchange_by_pricedb_nearest(foreign, domestic, date)



def exchange_by_pricedb_latest (foreign, domestic):

    # ;; This is another ready-to-use function for calculation of exchange
    # ;; rates. (Note that this is already the function itself. It doesn't
    # ;; return a function as opposed to make-exchange-function.) It takes
    # ;; the <gnc-monetary> 'foreign' amount and the <gnc:commodity*>
    # ;; 'domestic' commodity. It exchanges the amount into the domestic
    # ;; currency, using the latest price from the pricedb. The function
    # ;; returns a <gnc-monetary>.

    #pdb.set_trace()

    gnucash_log.PDEBUG("python","foreign: %s"%str(foreign))
    gnucash_log.PDEBUG("python","domestic: %s"%domestic.get_printname())

    dommon = None

    if isinstance(foreign,GncMonetary):

        dommon = exchange_by_euro(foreign, domestic, None)
        if dommon == None:
            dommon = exchange_if_same(foreign, domestic)
            if dommon == None:
                #pdb.set_trace()
                # it appears this may return a 0 price if doesnt find one
                prcdb = sw_app_utils.get_current_book().get_price_db()
                nrval = prcdb.convert_balance_latest_price( \
                    foreign.amount,foreign.commodity,domestic)
                dommon = GncMonetary(domestic,nrval)

    return dommon

def exchange_by_pricedb_nearest (foreign, domestic, date):

    # ;; Yet another ready-to-use function for calculation of exchange
    # ;; rates. (Note that this is already the function itself. It doesn't
    # ;; return a function as opposed to make-exchange-function.) It takes
    # ;; the <gnc-monetary> 'foreign' amount, the <gnc:commodity*>
    # ;; 'domestic' commodity *and* a <gnc:time-pair> 'date'. It exchanges
    # ;; the amount into the domestic currency, using a price from the
    # ;; pricedb according to the given date. The function returns a
    # ;; <gnc-monetary>.

    #pdb.set_trace()

    gnucash_log.PDEBUG("python","foreign: %s"%str(foreign))
    gnucash_log.PDEBUG("python","domestic: %s"%domestic.get_printname())

    dommon = None

    if isinstance(foreign,GncMonetary) and date != None:

        dommon = exchange_by_euro(foreign, domestic, date)
        if dommon == None:
            dommon = exchange_if_same(foreign, domestic)
            if dommon == None:
                #pdb.set_trace()
                # it appears this may return a 0 price if doesnt find one
                prcdb = sw_app_utils.get_current_book().get_price_db()
                nrval = prcdb.convert_balance_nearest_price( \
                    foreign.amount,foreign.commodity,domestic,date)
                dommon = GncMonetary(domestic,nrval)

    return dommon


def match_commodity_splits (currency_accounts, end_date_tp, commodity=None):
    # ;; Returns a list of all splits in the 'currency-accounts' up to
    # ;; 'end-date-tp' which have two different commodities involved, one of
    # ;; which is equivalent to 'commodity' (the latter constraint only if
    # ;; 'commodity' != #f ).

    #pdb.set_trace()

    splits = []

    curbook = sw_app_utils.get_current_book()

    qry = gnucash.Query.CreateFor(curbook.GNC_ID_SPLIT)

    qry.set_book(sw_app_utils.get_current_book())

    set_match_non_voids_only(qry,sw_app_utils.get_current_book())

    #qry.AddAccountMatch(currency_accounts,qry.QOF_GUID_MATCH_ANY,gnucash.QOF_QUERY_AND)
    #qry.AddDateMatchTS(False,end_date_tp,True,end_date_tp,gnucash.QOF_QUERY_AND)
    #engine_ctypes.AddAccountMatch(qry,currency_accounts,qry.QOF_GUID_MATCH_ANY,gnucash.QOF_QUERY_AND)
    if len(currency_accounts) > 1: pdb.set_trace()
    engine_ctypes.AddSingleAccountMatch(qry,currency_accounts[0],gnucash.QOF_QUERY_AND)
    engine_ctypes.AddDateMatchTS(qry,False,end_date_tp,True,end_date_tp,gnucash.QOF_QUERY_AND)

    # ;; Get the query result, i.e. all splits in currency
    # ;; accounts.
    spltlst = qry.Run(gnucash.Split)
    print "spltlst",spltlst
    # ;; Filter such that we get only those splits
    # ;; which have two *different* commodities
    # ;; involved.
    def lambda_filter (s):
          #print "inside lambda filter"
          #print dir(s) 
          #pdb.set_trace()
          trans_comm = s.GetParent().GetCurrency()
          acc_comm = s.GetAccount().GetCommodity()
          if not engine_ctypes.CommodityEquiv(trans_comm,acc_comm) and \
             (commodity == None or engine_ctypes.CommodityEquiv(commodity,trans_comm) or engine_ctypes.CommodityEquiv(commodity,acc_comm)):
              return s
          # if we dont return value what happens
          # (isnt there a default return of None??)

    #pdb.set_trace()
    newlst = map(lambda_filter, spltlst)

    #pdb.set_trace()

    return newlst

def match_commodity_splits_sorted (currency_accounts, end_date_tp, commodity=None):

    newaccs = match_commodity_splits(currency_accounts, end_date_tp, commodity)

    # need to sort by date
    # try makeing list of dates then sorting - using a cmp function likely slower
    srtlst = [ (x.GetParent().RetDatePostedTS(), x) for x in newaccs ]
    srtlst.sort()

    #if len(srtlst) > 0: pdb.set_trace()
    print srtlst

    return [ x[1] for x in srtlst ]


def set_match_non_voids_only (query, book):

    #pdb.set_trace()

    tmpqry = query.CreateFor(book.GNC_ID_SPLIT)

    tmpqry.set_book(book)

    #tmpqry.AddClearedMatch(query.CLEARED_VOIDED,gnucash.QOF_QUERY_AND)
    engine_ctypes.AddClearedMatch(tmpqry,query.CLEARED_VOIDED,gnucash.QOF_QUERY_AND)

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

    #pdb.set_trace()

    # this is really horrid - the primary function of this is to store the date!!
    # these functions are not passed a date when called but use the stored value

    if source_option == 'average-cost':
        exchange_fn = AverageCostFn(to_date_tp)
    elif source_option == 'weighted-average':
        exchange_fn = WeightedAverageFn(to_date_tp)
    elif source_option == 'pricedb-latest':
        exchange_fn = PriceDBLatestFn(to_date_tp)
    elif source_option == 'pricedb-nearest':
        exchange_fn = PriceDBNearestFn(to_date_tp)

    return exchange_fn

def case_exchange_time_fn (source_option, report_currency, commodity_list, to_date_tp, start_percent, delta_percent):

    #pdb.set_trace()

    # this also seems to store the date even though all functions when called
    # are passed the date

    if source_option == 'average-cost':
        exchange_fn = AverageExchangeTimeFn(to_date_tp)
    elif source_option == 'weighted-average':
        exchange_fn = WeightedAverageTimeFn(to_date_tp)
    elif source_option == 'actual-transactions':
        exchange_fn = ActualTransactionsTimeFn(to_date_tp)
    elif source_option == 'pricedb-latest':
        exchange_fn = PriceDBLatestTimeFn(to_date_tp)
    elif source_option == 'pricedb-nearest':
        exchange_fn = PriceDBNearestTimeFn(to_date_tp)

    return exchange_fn


class GncMonetary(object):

    def __init__ (self, commodity, amount):
        if isinstance(amount,gnucash.GncNumeric):
            self.commodity = commodity
            self.amount = amount
        else:
            #warn "wrong arguments for gnc:make-gnc-monetary: " c a)
            print "wrong arguments for gnc:make-gnc-monetary: %s %s"%(commodity, amount)
            pdb.set_trace()
            raise TypeError("wrong arguments for gnc:make-gnc-monetary: %s %s"%(commodity, amount))

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

