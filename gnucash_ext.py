#!/usr/bin/env python

# modded from simple_business_create.py

from os.path import abspath
import sys
import datetime
from datetime import timedelta
import re


from gnucash import Session, Account, GncNumeric
from gnucash.gnucash_business import Customer, Employee, Vendor, Job, \
    Address, Invoice, Entry, TaxTable, TaxTableEntry, GNC_AMT_TYPE_PERCENT, \
    GNC_DISC_PRETAX    
from gnucash.gnucash_core_c import \
    ACCT_TYPE_ASSET, ACCT_TYPE_RECEIVABLE, ACCT_TYPE_INCOME, ACCT_TYPE_EXPENSE, \
    GNC_OWNER_CUSTOMER, ACCT_TYPE_LIABILITY, \
    ACCT_TYPE_BANK, NUM_ACCOUNT_TYPES, \
    ACCT_TYPE_CHECKING, ACCT_TYPE_SAVINGS, ACCT_TYPE_STOCK

# until fix bug in gnucash_business.py
from gnucash.gnucash_business import entry_dict


from gnucash.gnucash_core import GnuCashCoreClass
from gnucash.gnucash_core import Book
from gnucash.gnucash_core import methods_return_instance,method_function_returns_instance, \
                                 method_function_returns_instance_list
from gnucash.gnucash_core import GUID

from gnucash.gnucash_core_c import string_to_guid as gnucash_core_string_to_guid

from gnucash import Query



import pdb


# make a class to handle QofCollections
class QofCollection(GnuCashCoreClass):
    _new_instance = 'gnc_collection_new'
    def __init__(self, id=None, 
                 instance=None):
        if instance == None:
            if id==None:
                raise Exception(
                    "you must call QofCollection.__init__ "
                    "with either an id or an existing "
                    "low level swig proxy in the argument instance")
            GnuCashCoreClass.__init__(self, id)
            #self.SetID(id)
            #self.SetCurrency(currency)
            #if name != None:
            #    self.set_name(name)
        else:
            GnuCashCoreClass.__init__(self, instance=instance)


# NOTA BENE add_methods_with_prefix adds functions that begin with qof_collection_
# but REMOVES the prefix to give python method name!!
# as comments say - all methods that work here must have a QofCollection object 
# as the first argument - otherwise the add_method... functions wont work
# note this adds functions for which this is not true - but no error
# - only get errors if call those functions!!
QofCollection.add_methods_with_prefix('qof_collection_')

# and this is how we define return types for the functions added above
# (I think the ctypes way is better!!)
# do we only need to define for those objects returning higher level objects
# - strings/ints etc dont need to be defined??
#QofCollection_dict =  {
#                'get_book' : Book,
#                }
#methods_return_instance(QofCollection,QofCollection_dict)

# and this is how to add property associated with functions
#QofCollection.data = property( QofCollection.get_data, QofCollection.set_data )

# attempt to add full budget lookup
#col = qof_book_get_collection (book, GNC_ID_BUDGET);

# construct a Recurrence object
# this is strange - I see no new function - it is a static component
# of a Budget object

class Recurrence(GnuCashCoreClass):

    PERIOD_ONCE = 0
    PERIOD_DAY = 1
    PERIOD_WEEK = 2
    PERIOD_MONTH = 3
    PERIOD_END_OF_MONTH = 4
    PERIOD_NTH_WEEKDAY = 5
    PERIOD_LAST_WEEKDAY = 6
    PERIOD_YEAR = 7
    NUM_PERIOD_TYPES = 8
    PERIOD_INVALID = -1

    WEEKEND_ADJ_NONE = 0
    WEEKEND_ADJ_BACK = 1
    WEEKEND_ADJ_FORWARD = 2
    NUM_WEEKEND_ADJS = 3
    WEEKEND_ADJ_INVALID = -1

    #_new_instance = 'gnc_budget_new'
    def __init__(self, book=None, id=None, currency=None, name=None,
                 instance=None):
        if instance == None:
            #if book==None or id==None or currency==None:
            if book==None:
                raise Exception(
                    "you must call Recurrence.__init__ "
                    "with either a book or an existing "
                    "low level swig proxy in the argument instance")
            GnuCashCoreClass.__init__(self, book)
            #self.SetID(id)
            #self.SetCurrency(currency)
            if name != None:
                self.set_name(name)
        else:
            GnuCashCoreClass.__init__(self, instance=instance)

    # curious - now things seem to be working
    # with changes to gdate.i to output typemaps and
    # define GDate class constructor/destructor

    def SetStart(self, dttim):
        pdb.set_trace()
        self.instance.start = dttim

    def GetStart(self):
        pdb.set_trace()
        return self.instance.start

    def SetPeriodType(self, mult):
        pdb.set_trace()
        self.instance.mult = mult

    def SetMultiplier(self, mult):
        pdb.set_trace()
        self.instance.mult = mult

    def SetWeekendAdjust(self, wadj):
        pdb.set_trace()
        self.instance.wadj = wadj

Recurrence.add_methods_with_prefix('recurrence')

# attempt construct Budget object - seems to be similar to PriceDB
# - although maybe should use the gnucash_business.py paradigm

class GncBudget(GnuCashCoreClass):
    _new_instance = 'gnc_budget_new'
    def __init__(self, book=None, id=None, currency=None, name=None,
                 instance=None):
        if instance == None:
            #if book==None or id==None or currency==None:
            if book==None:
                raise Exception(
                    "you must call GncBudget.__init__ "
                    "with either a book, id, and currency, or an existing "
                    "low level swig proxy in the argument instance")
            GnuCashCoreClass.__init__(self, book)
            #self.SetID(id)
            #self.SetCurrency(currency)
            if name != None:
                self.set_name(name)
        else:
            GnuCashCoreClass.__init__(self, instance=instance)


# NOTA BENE add_methods_with_prefix adds functions that begin with gnc_budget_
# but REMOVES the prefix to give python method name!!
# as comments say - all methods that work here must have a GncBudget object 
# as the first argument - otherwise the add_method... functions wont work
# note this adds functions for which this is not true - but no error
# - only get errors if call those functions!!
GncBudget.add_methods_with_prefix('gnc_budget_')

# and this is how we define return types for the functions added above
# (I think the ctypes way is better!!)
# do we only need to define for those objects returning higher level objects
# - strings/ints etc dont need to be defined??
# get_book removed now
GncBudget_dict =  {
                'get_guid' : GUID,
#                'get_book' : Book,
                'get_recurrence' : Recurrence,
                'get_account_period_value' : GncNumeric,
                }
methods_return_instance(GncBudget,GncBudget_dict)

# and this is how to add property associated with functions
GncBudget.name = property( GncBudget.get_name, GncBudget.set_name )


# so this function needs to be added to the GUID class as a guid object is the first
# argument - and like the others Book is the second
GUID.add_method('gnc_budget_lookup', 'BudgetLookup')
GUID.BudgetLookup = method_function_returns_instance(GUID.BudgetLookup,GncBudget)

# again this has been updated in 2.6.0
# we now have a GUIDString class
# which appears now contain the string_to_guid function
# but this should still work

# and another new trick - create a GUID from a hex string
def string_to_guid (guid, str):
    retval = gnucash_core_string_to_guid(str,guid.instance)
    return retval

def string_to_new_guid (cls, str):
    #pdb.set_trace()
    guid = cls()
    retval = gnucash_core_string_to_guid(str,guid.instance)
    if retval:
        return guid
    else:
        raise Exception("Unable to convert string to GUID")

GUID.string_to_guid = classmethod(string_to_new_guid)

#pdb.set_trace()


# we need to map swig instances to Python objects here
# as this returns a generic GList of arbitrary objects
# we cannot use current methods
# choices - pass a type to be returned - dont like
# this as have to know what getting
# or map from swig type to python type
# going with passing for ease at the moment

def Run (self, instance_class):
    #pdb.set_trace()
    retlst = self.run()
    # cant see a good way to get swig type 
    # going to assume all objects of same type
    # as the type extraction could be slow to do per list element
    #swigtype = repr(retlst[0]).split("'")[1].split()[0]
    newretlst = []
    for retinst in retlst:
        newinst = instance_class(instance=retinst)
        newretlst.append(newinst)
    return newretlst

Query.Run = Run


# and this function needs to be added to the book class
Book.add_method('gnc_budget_get_default', 'DefaultBudget')
Book.DefaultBudget = method_function_returns_instance(Book.DefaultBudget,GncBudget)

# but these methods are not mapped in swig
#Book.add_method('qof_book_get_collection', 'GetCollection')
#Book.GetCollection = method_function_returns_instance(Book.GetCollection,QofCollection)

# want to extend the Book class
Book.GNC_ID_BUDGET = "Budget"

def BudgetLookup (self, budget_name):

    # use Query to find budgets
    qry = Query()

    qry.set_book(self)

    # this query finds all budgets defined
    # question is how to use Query to find budget with a name??
    # for the moment lets just search the list - in general its a small list
    qry.search_for(Book.GNC_ID_BUDGET)

    bdgtlst = qry.Run(GncBudget)

    # note this only finds first one if name is the same
    for bdgt in bdgtlst:
       if bdgt.name == budget_name:
           return bdgt

    raise KeyError("Unable to find budget %s"%budget_name)

Book.BudgetLookup = BudgetLookup

# add a budget list function

def GetBudgets (self):

    # use Query to find budgets
    qry = Query()

    qry.set_book(self)

    # this query finds all budgets defined
    # question is how to use Query to find budget with a name??
    # for the moment lets just search the list - in general its a small list
    qry.search_for(Book.GNC_ID_BUDGET)

    bdgtlst = qry.Run(GncBudget)

    return bdgtlst

Book.GetBudgets = GetBudgets

# make GncNumeric into better python class
# oh thats sneaky - gnc_numeric_eq means identical GncNumerics - same num and denom
# gnc_numeric_equal means numbers are equal
# gnc_numeric_same converts both values to a passed denom then compares
# note we could probably make this class fully python arithmetic by defining
# the arithmetic operations

GncNumeric.__cmp__ = GncNumeric.compare
GncNumeric.__eq__ = GncNumeric.equal

# fix account iterating and lookup functions to be more pythonic
# should do this in gnucash_core.py
# for the moment dont do this - so should error if use wrong function
#Account.get_descendants = method_function_returns_instance_list( Account.get_descendants, Account )
# add different name for function
# thats why this fails between 2.4.11 and 2.6.0 - get_descendants now defined
# in main source to return Account objects
# define my original name definitions
#Account.GetDescendants = method_function_returns_instance_list( Account.get_descendants, Account )
Account.GetDescendants = Account.get_descendants

#Account.GetChildren = method_function_returns_instance_list(Account.get_children, Account)
Account.GetChildren = Account.get_children

# weird - it is returning an Account class - but not with SWIG proxy
# if Account with name does not exist
# probably should fix method_function_returns_instance to return None
# if no instance returned - could raise exception - except would have to be generic
def LookupByName (self, account_name):
    try:
        found_acc = self.lookup_by_name(account_name)
    except RuntimeError, runerr:
        raise KeyError("No account exists with name %s"%account_name)
    else:
        if found_acc.get_instance() == None:
            raise KeyError("No account exists with name %s"%account_name)
    return found_acc

def LookupByCode (self, account_code):
    try:
        found_acc = self.lookup_by_code(account_code)
    except RuntimeError, runerr:
        raise KeyError("No account exists with code %s"%account_code)
    else:
        if found_acc == None:
            raise KeyError("No account exists with code %s"%account_code)
        elif found_acc.get_instance() == None:
            raise KeyError("No account exists with code %s"%account_code)
    return found_acc

def LookupByFullName (self, account_name):
    try:
        found_acc = self.lookup_by_full_name(account_name)
    except RuntimeError, runerr:
        raise KeyError("No account exists with full name %s"%account_name)
    else:
        if found_acc == None:
            raise KeyError("No account exists with full name %s"%account_name)
        elif found_acc.get_instance() == None:
            raise KeyError("No account exists with full name %s"%account_name)
    return found_acc

Account.LookupByName = LookupByName
Account.LookupByCode = LookupByCode
Account.LookupByFullName = LookupByFullName

# unfortunately a few xaccAccount functions are actually xaccAccountType functions
# we need to add these to a new class
# although this is just an enum
class GNCAccountType(GnuCashCoreClass):
    #_new_instance = 'gnc_collection_new'
    pass
GNCAccountType.add_methods_with_prefix('xaccAccountType')
GNCAccountType.add_methods_with_prefix('xaccAccountTypes')

# and this does not return Entry objects but the SWIG proxy - fix it to return Entry objects
Invoice.GetEntries = method_function_returns_instance_list(Invoice.GetEntries, Entry)

# heres a bug - the dict is set up but not used
methods_return_instance(Entry, entry_dict)
