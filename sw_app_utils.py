
# we need a wrapper around _sw_app_utils.py
# also need to import the python bindings for wrapping
# some returns in reasonable type
# - at the moment the app_utils bindings are very crude

import sys

import os

import ctypes

from ctypes.util import find_library

import pdb


import sw_core_utils


class GncCommodityOpaque(ctypes.Structure):
    pass

gboolean = ctypes.c_byte

# we cant search the gnucash sublib directory with find_library
# also to use CDLL means need to detect extension!!
libgnc_coreutilnm = find_library("gnc-core-utils")
libgnc_apputilnm = os.path.join(os.path.dirname(libgnc_coreutilnm),"gnucash","libgncmod-app-utils.dylib")
if not os.path.exists(libgnc_apputilnm):
    pdb.set_trace()
    raise RuntimeError("Can't find a libgncmod-app-utils library to use.")

libgnc_apputils = ctypes.CDLL(libgnc_apputilnm)

libgnc_apputils.gnc_default_report_currency.argtypes = []
libgnc_apputils.gnc_default_report_currency.restype = ctypes.POINTER(GncCommodityOpaque)

libgnc_apputils.gnc_is_euro_currency.argtypes = [ ctypes.POINTER(GncCommodityOpaque) ]
libgnc_apputils.gnc_is_euro_currency.restype = gboolean


# theres no good way to do this
# we have to access the returned commodity by ctypes, get the individual values
# and create new GncCommodity using these values
libgnc_enginenm = os.path.join(os.path.dirname(libgnc_coreutilnm),"gnucash","libgncmod-engine.dylib")
if not os.path.exists(libgnc_enginenm):
    pdb.set_trace()
    raise RuntimeError("Can't find a libgncmod-engine library to use.")
libgnc_engine = ctypes.CDLL(libgnc_enginenm)
libgnc_engine.gnc_commodity_get_fullname.argtypes = []
libgnc_engine.gnc_commodity_get_fullname.restype = ctypes.c_char_p
libgnc_engine.gnc_commodity_get_namespace.argtypes = []
libgnc_engine.gnc_commodity_get_namespace.restype = ctypes.c_char_p
libgnc_engine.gnc_commodity_get_mnemonic.argtypes = []
libgnc_engine.gnc_commodity_get_mnemonic.restype = ctypes.c_char_p
libgnc_engine.gnc_commodity_get_cusip.argtypes = []
libgnc_engine.gnc_commodity_get_cusip.restype = ctypes.c_char_p
libgnc_engine.gnc_commodity_get_fraction.argtypes = []
libgnc_engine.gnc_commodity_get_fraction.restype = ctypes.c_int


import _sw_app_utils


import gnucash

#pdb.set_trace()

class QofBookOpaque(ctypes.Structure):
    pass


def get_current_book ():

    # not sure what type to convert this to yet
    curbook_inst = _sw_app_utils.gnc_get_current_book()

    curbook_ptr = ctypes.cast( curbook_inst.__long__(), ctypes.POINTER( QofBookOpaque ) )

    #pdb.set_trace()
    print >> sys.stderr, "curbook_ptr %x"%curbook_inst.__long__()
    print >> sys.stderr, "curbook_ptr %x"%ctypes.addressof(curbook_ptr.contents)

    # will this work - yes!!
    curbook = gnucash.Book(instance=curbook_inst)

    return curbook

    #pdb.set_trace()
    #self.add_book(ctypes.addressof(curbook_ptr.contents))
    #self.add_book(curbook.__long__())


# so this function is apparently "inlined" in the swig


def default_report_currency ():

    #pdb.set_trace()

    #def_curr_inst = _sw_app_utils.gnc_default_report_currency()
    #def_curr = gnucash.GncCommodity(instance=def_curr_inst)

    def_curr_ptr = libgnc_apputils.gnc_default_report_currency()

    print >> sys.stderr, "curr ptr %x"%ctypes.addressof(def_curr_ptr.contents)

    def_fullname = libgnc_engine.gnc_commodity_get_fullname(def_curr_ptr)
    print >> sys.stderr, "curr fullname %s"%def_fullname
    def_namespace = libgnc_engine.gnc_commodity_get_namespace(def_curr_ptr)
    print >> sys.stderr, "curr namespace %s"%def_namespace
    def_mnemonic = libgnc_engine.gnc_commodity_get_mnemonic(def_curr_ptr)
    print >> sys.stderr, "curr mnemonic %s"%def_mnemonic
    def_cusip = libgnc_engine.gnc_commodity_get_cusip(def_curr_ptr)
    print >> sys.stderr, "curr cusip %s"%def_cusip
    def_fraction = libgnc_engine.gnc_commodity_get_fraction(def_curr_ptr)
    print >> sys.stderr, "curr fraction %d"%def_fraction

    #curbook_inst = _sw_app_utils.gnc_get_current_book()
    #curbook_ptr = ctypes.cast( curbook_inst.__long__(), ctypes.POINTER( QofBookOpaque ) )

    curbook = get_current_book()

    # bugger - to do this we need to convert the ctypes pointer to a low-level swig pointer

    # theres only one way I can see
    # allocate a new GncCommodity
    #tmp_curr = gnucash.GncCommodity(curbook,"US Dollar","CURRENCY","USD","840",100)

    # very sneakily replace the internal swig pointer to actual C object with the ctypes pointer
    # unfortunately does not look as though this is possible
    #def_curr = gnucash.GncCommodity(instance=def_curr_inst)

    # for junky quick fixup create new GncCommodity
    # - of course this is completely new object and wont reflect changes made to the gnucash
    # internal default currency without re-calling this routine
    def_curr = gnucash.GncCommodity(curbook,def_fullname,def_namespace,def_mnemonic,def_cusip,def_fraction)

    return def_curr


def get_current_commodities ():

    # for some reason this is not in the swig wrap
    # - replicate in python

    curbook = get_current_book()

    commod_table = curbook.get_table()

    return commod_table

def get_euro ():

    curbook = get_current_book()

    commod_table = curbook.get_table()

    eur = commond_table.lookup('CURRENCY', "EUR")

    return eur


def locale_default_currency_nodefault ():

    table = get_current_commodities()
    code = sw_core_utils.gnc_locale_default_iso_currency_code()

    currency = table.lookup('CURRENCY', code)

    currency_ptr = ctypes.cast( currency.__long__(), ctypes.POINTER( GncCommodityOpaque ) )

    is_euro = libgnc_apputils.gnc_is_euro_currency(currency_ptr)

    print >> sys.stderr, "is_euro %x"%is_euro

    if is_euro:

        currency = get_euro()

    return currency if currency != None else None

def locale_default_currency ():

    currency = locale_default_currency_nodefault()

    if currency != None:
        return currency

    table = get_current_commodities()

    currency = table.lookup('CURRENCY', "USD")

    return currency
