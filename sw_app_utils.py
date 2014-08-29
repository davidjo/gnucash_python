
# we need a wrapper around _sw_app_utils.py
# also need to import the python bindings for wrapping
# some returns in reasonable type
# - at the moment the app_utils bindings are very crude

import sys

import os

import ctypes

from ctypes.util import find_library

import gobject

import pdb


import sw_core_utils

import engine_ctypes

import swighelpers

import gnucash



#pdb.set_trace()



#gboolean = ctypes.c_byte
gboolean = ctypes.c_int
gint64 = ctypes.c_longlong
guint8 = ctypes.c_uint8

class GncCommodityOpaque(ctypes.Structure):
    pass

class GncNumericOpaque(ctypes.Structure):
    pass

# dangerous because we duplicate the structure definitions
# here but we need them as these are passed and returned by value 
# and NOT by pointer

class GncNumeric(ctypes.Structure):
    pass
GncNumeric._fields_ = [ ("num", ctypes.c_int64),
                        ("denom", ctypes.c_int64),
                      ]

class GncPrintAmountInfo(ctypes.Structure):
    pass
GncPrintAmountInfo._fields_ = [ ("commodity", ctypes.c_void_p),
                                ("max_decimal_places", guint8),
                                ("min_decimal_places", guint8),
                                ("use_separators", ctypes.c_uint, 1), # /* Print thousands separators */
                                ("use_symbol", ctypes.c_uint, 1),     # /* Print currency symbol */
                                ("use_locale", ctypes.c_uint, 1),     # /* Use locale for some positioning */
                                ("monetary", ctypes.c_uint, 1),       # /* Is a monetary quantity */
                                ("force_fit", ctypes.c_uint, 1),      # /* Don't print more than max_dp places */
                                ("round", ctypes.c_uint, 1),          # /* Round at max_dp instead of truncating */
                              ]


# we cant search the gnucash sublib directory with find_library
# also to use CDLL means need to detect extension!!
# ah - maybe we can get the extension from core-utils and use that
# it looks as though should be the same
libgnc_coreutilnm = find_library("gnc-core-utils")
libgnc_ext = os.path.splitext(libgnc_coreutilnm)[1]
libgnc_apputilnm = os.path.join(os.path.dirname(libgnc_coreutilnm),"gnucash","libgncmod-app-utils"+libgnc_ext)
if not os.path.exists(libgnc_apputilnm):
    pdb.set_trace()
    raise RuntimeError("Can't find a libgncmod-app-utils library to use.")

libgnc_apputils = ctypes.CDLL(libgnc_apputilnm)

#libgnc_apputils.gnc_register_gui_component("window-report", None, close_handler, self)
libgnc_apputils.gnc_register_gui_component.argtypes = [ ctypes.c_char_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p ]
libgnc_apputils.gnc_register_gui_component.restype = ctypes.c_int

libgnc_apputils.gnc_get_current_session.argtypes = []
libgnc_apputils.gnc_get_current_session.restype = ctypes.c_void_p

libgnc_apputils.gnc_unregister_gui_component.argtypes = [ ctypes.c_int ]
libgnc_apputils.gnc_unregister_gui_component.restype = None

libgnc_apputils.gnc_unregister_gui_component_by_data.argtypes = [ ctypes.c_char_p, ctypes.c_void_p ]
libgnc_apputils.gnc_unregister_gui_component_by_data.restype = None


libgnc_apputils.gnc_default_report_currency.argtypes = []
#libgnc_apputils.gnc_default_report_currency.restype = ctypes.c_void_p
libgnc_apputils.gnc_default_report_currency.restype = ctypes.POINTER(GncCommodityOpaque)

libgnc_apputils.gnc_is_euro_currency.argtypes = [ ctypes.POINTER(GncCommodityOpaque) ]
libgnc_apputils.gnc_is_euro_currency.restype = gboolean

libgnc_apputils.gnc_convert_to_euro.argtypes = [ ctypes.POINTER(GncCommodityOpaque), GncNumeric ]
libgnc_apputils.gnc_convert_to_euro.restype = GncNumeric


libgnc_apputils.gnc_accounting_period_fiscal_start.argtypes = []
libgnc_apputils.gnc_accounting_period_fiscal_start.restype = gint64

libgnc_apputils.gnc_accounting_period_fiscal_end.argtypes = []
libgnc_apputils.gnc_accounting_period_fiscal_end.restype = gint64


libgnc_apputils.gnc_default_print_info.argtypes = [ ctypes.c_bool ]
libgnc_apputils.gnc_default_print_info.restype = GncPrintAmountInfo

libgnc_apputils.gnc_commodity_print_info.argtypes = [ ctypes.POINTER(GncCommodityOpaque), ctypes.c_bool ]
libgnc_apputils.gnc_commodity_print_info.restype = GncPrintAmountInfo

libgnc_apputils.xaccPrintAmount.argtypes = [ GncNumeric, GncPrintAmountInfo ]
libgnc_apputils.xaccPrintAmount.restype = ctypes.c_char_p


def gnc_accounting_period_fiscal_start ():
    tmvl = libgnc_apputils.gnc_accounting_period_fiscal_start()
    return tmvl

def gnc_accounting_period_fiscal_end ():
    tmvl = libgnc_apputils.gnc_accounting_period_fiscal_end()
    return tmvl



import _sw_app_utils

#pdb.set_trace()

class QofBookOpaque(ctypes.Structure):
    pass


def get_current_book ():

    #print "types at get_current_book"
    #print gobject.type_children(gobject.type_from_name('GObject'))

    # not sure what type to convert this to yet
    curbook_inst = _sw_app_utils.gnc_get_current_book()

    curbook_ptr = ctypes.cast( curbook_inst.__long__(), ctypes.POINTER( QofBookOpaque ) )

    #pdb.set_trace()
    #print >> sys.stderr, "curbook_ptr %x"%curbook_inst.__long__()
    #print >> sys.stderr, "curbook_ptr %x"%ctypes.addressof(curbook_ptr.contents)

    # will this work - yes!!
    curbook = gnucash.Book(instance=curbook_inst)

    return curbook

    #pdb.set_trace()
    #self.add_book(ctypes.addressof(curbook_ptr.contents))
    #self.add_book(curbook.__long__())

def get_current_root_account ():
    # re-implement in python rather can calling C function??
    return get_current_book().get_root_account()


# so this function is apparently "inlined" in the swig

def default_report_currency_old ():

    #pdb.set_trace()

    #def_curr_inst = _sw_app_utils.gnc_default_report_currency()
    #def_curr = gnucash.GncCommodity(instance=def_curr_inst)

    def_curr_ptr = libgnc_apputils.gnc_default_report_currency()

    print >> sys.stderr, "curr ptr %x"%ctypes.addressof(def_curr_ptr.contents)

    def_fullname = engine_ctypes.libgnc_engine.gnc_commodity_get_fullname(def_curr_ptr)
    print >> sys.stderr, "curr fullname %s"%def_fullname
    def_namespace = engine_ctypes.libgnc_engine.gnc_commodity_get_namespace(def_curr_ptr)
    print >> sys.stderr, "curr namespace %s"%def_namespace
    def_mnemonic = engine_ctypes.libgnc_engine.gnc_commodity_get_mnemonic(def_curr_ptr)
    print >> sys.stderr, "curr mnemonic %s"%def_mnemonic
    def_cusip = engine_ctypes.libgnc_engine.gnc_commodity_get_cusip(def_curr_ptr)
    print >> sys.stderr, "curr cusip %s"%def_cusip
    def_fraction = engine_ctypes.libgnc_engine.gnc_commodity_get_fraction(def_curr_ptr)
    print >> sys.stderr, "curr fraction %d"%def_fraction

    #curbook_inst = _sw_app_utils.gnc_get_current_book()
    #curbook_ptr = ctypes.cast( curbook_inst.__long__(), ctypes.POINTER( QofBookOpaque ) )

    curbook = get_current_book()

    # to do this we need to convert the ctypes pointer to a low-level swig pointer

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

# new version of default_report_currency using swighelpers!!
# yay - working nicely!!

def default_report_currency ():

    #pdb.set_trace()

    #def_curr_inst = _sw_app_utils.gnc_default_report_currency()
    #def_curr = gnucash.GncCommodity(instance=def_curr_inst)

    def_curr_ptr = libgnc_apputils.gnc_default_report_currency()

    # we have confirmed that this gives the address of the raw C object
    # when the function return is defined as a POINTER type
    print >> sys.stderr, "curr ptr %x"%ctypes.addressof(def_curr_ptr.contents)

    # to do this we need to convert the ctypes pointer to a low-level swig pointer
    # - which we can now do via swighelpers!!
    def_curr_inst = swighelpers.int_to_swig(ctypes.addressof(def_curr_ptr.contents),"_p_gnc_commodity")
    def_curr = gnucash.GncCommodity(instance=def_curr_inst)

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

def convert_to_euro (currency, value):

    pdb.set_trace()

    currency_ptr = ctypes.cast( currency.__long__(), ctypes.POINTER( GncCommodityOpaque ) )

    euro_val = libgnc_apputils.gnc_convert_to_euro(currency_ptr, value)

    print >> sys.stderr, "euro_val %x"%euro_val

    new_euro_inst = swighelpers.int_to_swig(ctypes.addressof(euro_val.value),"_p_gnc_numeric")
    new_euro = gnucash.GncNumeric(instance=new_euro_inst)

    new_euro = gnucash.GncNumeric(euro_val.num,euro_val.denom)

    return new_euro

def is_euro_currency (currency):

    #pdb.set_trace()

    currency_ptr = ctypes.cast( currency.instance.__long__(), ctypes.POINTER( GncCommodityOpaque ) )

    is_euro = libgnc_apputils.gnc_is_euro_currency(currency_ptr)

    #print >> sys.stderr, "is_euro %x"%is_euro

    return is_euro

def locale_default_currency_nodefault ():

    pdb.set_trace()

    table = get_current_commodities()
    code = sw_core_utils.gnc_locale_default_iso_currency_code()

    currency = table.lookup('CURRENCY', code)

    currency_ptr = ctypes.cast( currency.__long__(), ctypes.POINTER( GncCommodityOpaque ) )

    is_euro = libgnc_apputils.gnc_is_euro_currency(currency_ptr)

    #print >> sys.stderr, "is_euro %x"%is_euro

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

def CommodityPrintInfo (commodity, use_symbol):
    gnccmd_ptr = ctypes.cast( commodity.instance.__long__(), ctypes.POINTER(GncCommodityOpaque) )
    prtinfo = libgnc_apputils.gnc_commodity_print_info(gnccmd_ptr,use_symbol)
    return prtinfo

def PrintInfo (use_symbol):
    prtinfo = libgnc_apputils.gnc_default_print_info(use_symbol)
    return prtinfo

def PrintAmount (amnt, gnc_print_info=None):
    # this is defined in gnc-ui-util.c
    # should be a method of GncNumeric as first argument is a GncNumeric
    #pdb.set_trace()
    if gnc_print_info == None:
        prtinfo = libgnc_apputils.gnc_default_print_info(False)
    else:
        prtinfo = gnc_print_info

    # I still dont understand why some gnucash objects the instance is the swig object
    # but for others the instance object has a this pointer which is the swig object
    # seems to be associated with if the instance is labelled a proxy of a swig object
    # ah - a swig proxy exists when swig has recognized an class object in the underlying
    # language
    # this is also labelled as shadow objects in the swig code
    gncnum_ptr = ctypes.cast( amnt.instance.this.__long__(), ctypes.POINTER( GncNumeric ) )

    #print >> sys.stderr, "gncnum_ptr %x"%amnt.instance.this.__long__()
    #print >> sys.stderr, "gncnum_ptr %x"%ctypes.addressof(gncnum_ptr.contents)

    # so looks like we can pass by value - and return by value!!
    prtstr = libgnc_apputils.xaccPrintAmount(gncnum_ptr.contents, prtinfo)

    return prtstr
