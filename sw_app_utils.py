
# we need a wrapper around _sw_app_utils (libgncmod-app-utils-python.dylib)
# also need to import the python bindings for wrapping
# some returns in reasonable type
# - at the moment the app_utils bindings are very crude

import sys

import os

import ctypes

from ctypes.util import find_library

#from gi.repository import GObject

import pdb

import traceback


import sw_core_utils

import engine_ctypes

import swighelpers

import gnucash



#pdb.set_trace()


# this function is defined in scheme in app-utils directory
# in python can only just print the arguments
# oh great 2 definition of this function
# one is gnc:error->string here and other gnc:error in main.scm in scm
# Im really confused!!



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

class GncPrintAmountInfoNoBitFld(ctypes.Structure):
    pass
GncPrintAmountInfoNoBitFld._fields_ = [ ("commodity", ctypes.c_void_p),
                                        ("max_decimal_places", guint8),
                                        ("min_decimal_places", guint8),
                                        ("bitfld", guint8),
                                      ]

class GncPrintAmountInfoBitFlds(ctypes.Structure):
    pass
GncPrintAmountInfoBitFlds._fields_ = [ ("use_separators", ctypes.c_uint, 1), # /* Print thousands separators */
                                       ("use_symbol", ctypes.c_uint, 1),     # /* Print currency symbol */
                                       ("use_locale", ctypes.c_uint, 1),     # /* Use locale for some positioning */
                                       ("monetary", ctypes.c_uint, 1),       # /* Is a monetary quantity */
                                       ("force_fit", ctypes.c_uint, 1),      # /* Don't print more than max_dp places */
                                       ("round", ctypes.c_uint, 1),          # /* Round at max_dp instead of truncating */
                                     ]

# note we need to use ctypes.c_uint8 for the bitfld - if we use ctypes.c_uint we get
# bad data - probably byte swapping issues - ie it allocates 32 bits and we start at wrong end
# of the 32 bits - but if we use ctypes.c_uint8 the bit data is in the right order

class GncPrintAmountInfo(ctypes.Structure):
    pass
GncPrintAmountInfo._fields_ = [ ("commodity", ctypes.c_void_p),
                                ("max_decimal_places", guint8),
                                ("min_decimal_places", guint8),
                                ("use_separators", guint8, 1), # /* Print thousands separators */
                                ("use_symbol", guint8, 1),     # /* Print currency symbol */
                                ("use_locale", guint8, 1),     # /* Use locale for some positioning */
                                ("monetary", guint8, 1),       # /* Is a monetary quantity */
                                ("force_fit", guint8, 1),      # /* Don't print more than max_dp places */
                                ("round", guint8, 1),          # /* Round at max_dp instead of truncating */
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


libgnc_apputils.gnc_get_default_directory.argtypes = [ ctypes.c_char_p ]
libgnc_apputils.gnc_get_default_directory.restype = ctypes.c_char_p

libgnc_apputils.gnc_set_default_directory.argtypes = [ ctypes.c_char_p, ctypes.c_char_p ]
libgnc_apputils.gnc_set_default_directory.restype = None



# not available - static symbol
#libgnc_apputils.gnc_default_print_info_helper.argtypes = [ ctypes.c_int ]
#libgnc_apputils.gnc_default_print_info_helper.restype = GncPrintAmountInfoNoBitFld

libgnc_apputils.gnc_default_share_print_info.argtypes = []
libgnc_apputils.gnc_default_share_print_info.restype = GncPrintAmountInfoNoBitFld

libgnc_apputils.gnc_share_print_info_places.argtypes = [ ctypes.c_int ]
libgnc_apputils.gnc_share_print_info_places.restype = GncPrintAmountInfoNoBitFld

libgnc_apputils.gnc_default_print_info.argtypes = [ ctypes.c_bool ]
libgnc_apputils.gnc_default_print_info.restype = GncPrintAmountInfoNoBitFld

libgnc_apputils.gnc_commodity_print_info.argtypes = [ ctypes.POINTER(GncCommodityOpaque), ctypes.c_bool ]
libgnc_apputils.gnc_commodity_print_info.restype = GncPrintAmountInfoNoBitFld

libgnc_apputils.xaccPrintAmount.argtypes = [ GncNumeric, GncPrintAmountInfoNoBitFld ]
libgnc_apputils.xaccPrintAmount.restype = ctypes.c_char_p



# try adding in financial functions

libgnc_apputils.fi_calc_payment.argtypes = [ ctypes.c_void_p ]
libgnc_apputils.fi_calc_payment.restype = ctypes.c_double

libgnc_apputils.fi_calc_future_value.argtypes = [ ctypes.c_void_p ]
libgnc_apputils.fi_calc_future_value.restype = ctypes.c_double

libgnc_apputils.fi_calc_present_value.argtypes = [ ctypes.c_void_p ]
libgnc_apputils.fi_calc_present_value.restype = ctypes.c_double

libgnc_apputils.fi_calc_interest.argtypes = [ ctypes.c_void_p ]
libgnc_apputils.fi_calc_interest.restype = ctypes.c_double

libgnc_apputils.fi_calc_num_payments.argtypes = [ ctypes.c_void_p ]
libgnc_apputils.fi_calc_num_payments.restype = ctypes.c_uint


class FinancialInfo(ctypes.Structure):
    _fields_ = [ ("ir", ctypes.c_double),      # interest rate
                 ("pv", ctypes.c_double),      # present value
                 ("pmt", ctypes.c_double),     # periodic  payment
                 ("fv", ctypes.c_double),      # future value
                 ("npp", ctypes.c_uint),       # number of payment periods
                 ("CF", ctypes.c_uint),        # Compounding frequency
                 ("PF", ctypes.c_uint),        # payment frequency
                 ("bep", ctypes.c_uint),       # beginning/end of period payment flag
                 ("disc", ctypes.c_uint),      # discrete/continuous compounding flag
                 ("prec", ctypes.c_uint),      # precision of roundoff for pv, pmt and fv
               ]

FinancialInfoPtr = ctypes.POINTER(FinancialInfo)


class FiCalc(object):

    def __init__ (self):
        self.fi_info = FinancialInfo()
        self.fi_ptr = ctypes.cast( ctypes.addressof(self.fi_info), FinancialInfoPtr)

    def num_payments (self):
        intvl = libgnc_apputils.fi_calc_num_payments(self.fi_ptr)
        return intvl

    def interest (self):
        dbvl = libgnc_apputils.fi_calc_interest(self.fi_ptr)
        return dbvl

    def present_value (self):
        dbvl = libgnc_apputils.fi_calc_present_value(self.fi_ptr)
        return dbvl

    def payment (self):
        dbvl = libgnc_apputils.fi_calc_payment(self.fi_ptr)
        return dbvl

    def future_value (self):
        dbvl = libgnc_apputils.fi_calc_future_value(self.fi_ptr)
        return dbvl

    def print_finfo (self):
        print("  ir",self.fi_info.ir)
        print("  pv",self.fi_info.pv)
        print(" pmt",self.fi_info.pmt)
        print("  fv",self.fi_info.fv)
        print(" npp",self.fi_info.npp)
        print("  CF",self.fi_info.CF)
        print("  PF",self.fi_info.PF)
        print("bep",self.fi_info.bep)
        print("disc",self.fi_info.disc)
        print("prec",self.fi_info.prec)


def gnc_accounting_period_fiscal_start ():
    tmvl = libgnc_apputils.gnc_accounting_period_fiscal_start()
    return tmvl

def gnc_accounting_period_fiscal_end ():
    tmvl = libgnc_apputils.gnc_accounting_period_fiscal_end()
    return tmvl



import gnucash._sw_app_utils as _sw_app_utils

#pdb.set_trace()

class QofBookOpaque(ctypes.Structure):
    pass


def register_gui_component (component_class_name, refresh_handler, close_handler, widget):

    pdb.set_trace()

    component_close_callback_type = ctypes.CFUNCTYPE(None,ctypes.c_void_p)

    component_id = libgnc_apputils.gnc_register_gui_component(component_class_name.encode('utf-8'), None, component_close_callback_type(self.component_close_handler), hash(widget))

    return component_id


def get_current_book ():

    #print("types at get_current_book")
    #print(GObject.type_children(GObject.type_from_name('GObject')))

    #pdb.set_trace()

    # not sure what type to convert this to yet
    curbook_inst = _sw_app_utils.gnc_get_current_book()

    #print("curbook_inst %x"%curbook_inst.__int__(), file=sys.stderr)

    curbook_ptr = ctypes.cast( curbook_inst.__int__(), ctypes.POINTER( QofBookOpaque ) )

    #pdb.set_trace()
    #print("curbook_ptr 0x%x"%curbook_inst.__int__(), file=sys.stderr)
    #print("curbook_ptr 0x%x"%ctypes.addressof(curbook_ptr.contents), file=sys.stderr)

    # will this work - yes!!
    curbook = gnucash.Book(instance=curbook_inst)

    return curbook

    #pdb.set_trace()
    #self.add_book(ctypes.addressof(curbook_ptr.contents))
    #self.add_book(curbook.__int__())

def get_current_root_account ():
    # re-implement in python rather than calling C function??
    return get_current_book().get_root_account()


def get_default_directory (section):

    dirpath = libgnc_apputils.gnc_get_default_directory(section)

    return dirpath

def set_default_directory (section, directory):

    libgnc_apputils.gnc_set_default_directory(section, directory)


# so this function is apparently "inlined" in the swig

def default_report_currency_old ():

    #pdb.set_trace()

    #def_curr_inst = _sw_app_utils.gnc_default_report_currency()
    #def_curr = gnucash.GncCommodity(instance=def_curr_inst)

    def_curr_ptr = libgnc_apputils.gnc_default_report_currency()

    print("curr ptr 0x%x"%ctypes.addressof(def_curr_ptr.contents), file=sys.stderr)

    def_fullname = engine_ctypes.libgnc_engine.gnc_commodity_get_fullname(def_curr_ptr)
    print("curr fullname %s"%def_fullname, file=sys.stderr)
    def_namespace = engine_ctypes.libgnc_engine.gnc_commodity_get_namespace(def_curr_ptr)
    print("curr namespace %s"%def_namespace, file=sys.stderr)
    def_mnemonic = engine_ctypes.libgnc_engine.gnc_commodity_get_mnemonic(def_curr_ptr)
    print("curr mnemonic %s"%def_mnemonic, file=sys.stderr)
    def_cusip = engine_ctypes.libgnc_engine.gnc_commodity_get_cusip(def_curr_ptr)
    print("curr cusip %s"%def_cusip, file=sys.stderr)
    def_fraction = engine_ctypes.libgnc_engine.gnc_commodity_get_fraction(def_curr_ptr)
    print("curr fraction %d"%def_fraction, file=sys.stderr)

    #curbook_inst = _sw_app_utils.gnc_get_current_book()
    #curbook_ptr = ctypes.cast( curbook_inst.__int__(), ctypes.POINTER( QofBookOpaque ) )

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
    print("curr ptr 0x%x"%ctypes.addressof(def_curr_ptr.contents), file=sys.stderr)

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

    currency_ptr = ctypes.cast( currency.__int__(), ctypes.POINTER( GncCommodityOpaque ) )

    euro_val = libgnc_apputils.gnc_convert_to_euro(currency_ptr, value)

    print("euro_val 0x%x"%euro_val, file=sys.stderr)

    new_euro_inst = swighelpers.int_to_swig(ctypes.addressof(euro_val.value),"_p_gnc_numeric")
    new_euro = gnucash.GncNumeric(instance=new_euro_inst)

    new_euro = gnucash.GncNumeric(euro_val.num,euro_val.denom)

    return new_euro

def is_euro_currency (currency):

    #pdb.set_trace()

    currency_ptr = ctypes.cast( currency.instance.__int__(), ctypes.POINTER( GncCommodityOpaque ) )

    is_euro = libgnc_apputils.gnc_is_euro_currency(currency_ptr)

    #print("is_euro %x"%is_euro, file=sys.stderr)

    return is_euro

def locale_default_currency_nodefault ():

    pdb.set_trace()

    table = get_current_commodities()
    code = sw_core_utils.gnc_locale_default_iso_currency_code()

    currency = table.lookup('CURRENCY', code)

    print("locale_default_currency_nodefault",currency)

    currency_ptr = ctypes.cast( currency.instance.__int__(), ctypes.POINTER( GncCommodityOpaque ) )

    is_euro = libgnc_apputils.gnc_is_euro_currency(currency_ptr)

    #print("is_euro %x"%is_euro, file=sys.stderr)

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
    gnccmd_ptr = ctypes.cast( commodity.instance.__int__(), ctypes.POINTER(GncCommodityOpaque) )
    prtinfonobitfld = libgnc_apputils.gnc_commodity_print_info(gnccmd_ptr,use_symbol)

    #print("CommodityPrintInfo", commodity.get_mnemonic(), "0x%x"%ctypes.addressof(prtinfonobitfld), prtinfonobitfld)
    #print("CommodityPrintInfo", commodity.get_mnemonic(), "0x%x"%ctypes.addressof(prtinfonobitfld), prtinfonobitfld.bitfld)

    # I tried just creating a ctypes structure object from the return here  but had problems
    # - some seemingly random data changes occurring at some random later point
    # the C gnc_commodity_print_info function returns a structure (not pointer to structure!) from a stack allocated
    # version - the C compiler does some magic to ensure this works - which may be getting messed up when calling from
    # ctypes (note there are other functions in gnc-ui-util.c which do this)
    # at this point the returned structure seems correct - so lets make an explicit copy here
    prtinfo_ptr = ctypes.cast( ctypes.addressof(prtinfonobitfld), ctypes.POINTER(GncPrintAmountInfo) )
    #prtinfo = prtinfo_ptr.contents
    prtinfo = GncPrintAmountInfo()
    ctypes.pointer(prtinfo)[0] = prtinfo_ptr[0]

    #print("CommodityPrintInfo", commodity.get_mnemonic(), prtinfo.use_separators, prtinfo.use_symbol, prtinfo.use_locale, prtinfo.monetary, prtinfo.force_fit, prtinfo.round)

    return prtinfo

def SharePrintInfoPlaces (dec_places):
    prtinfonobitfld = libgnc_apputils.gnc_share_print_info_places(dec_places)
    prtinfo_ptr = ctypes.cast( ctypes.addressof(prtinfonobitfld), ctypes.POINTER(GncPrintAmountInfo) )
    #prtinfo = prtinfo_ptr.contents
    # make explicit copy - see above
    prtinfo = GncPrintAmountInfo()
    ctypes.pointer(prtinfo)[0] = prtinfo_ptr[0]
    return prtinfo

def DefaultPrintInfo (use_symbol):
    prtinfonobitfld = libgnc_apputils.gnc_default_print_info(use_symbol)
    prtinfo_ptr = ctypes.cast( ctypes.addressof(prtinfonobitfld), ctypes.POINTER(GncPrintAmountInfo) )
    #prtinfo = prtinfo_ptr.contents
    # make explicit copy - see above
    prtinfo = GncPrintAmountInfo()
    ctypes.pointer(prtinfo)[0] = prtinfo_ptr[0]
    return prtinfo

def PrintAmount (amnt, gnc_print_info=None):
    # this is defined in gnc-ui-util.c
    # should be a method of GncNumeric as first argument is a GncNumeric
    #pdb.set_trace()

    #if gnc_print_info != None:
    #   print("PrintAmount  ", gnc_print_info, "0x%x"%ctypes.addressof(gnc_print_info))
    #   print("PrintAmount  ", gnc_print_info.use_separators, gnc_print_info.use_symbol, gnc_print_info.use_locale, gnc_print_info.monetary, gnc_print_info.force_fit, gnc_print_info.round)

    if gnc_print_info == None:
        prtinfonobitfld = libgnc_apputils.gnc_default_print_info(False)
        prtinfo_ptr = ctypes.cast( ctypes.addressof(prtinfonobitfld), ctypes.POINTER(GncPrintAmountInfo) )
        # make explicit copy - see above
        prtinfo = GncPrintAmountInfo()
        ctypes.pointer(prtinfo)[0] = prtinfo_ptr[0]
    else:
        prtinfo = gnc_print_info

    #print("PrintAmount 1", prtinfo, "0x%x"%ctypes.addressof(prtinfo))
    #print("PrintAmount 1", prtinfo.use_separators, prtinfo.use_symbol, prtinfo.use_locale, prtinfo.monetary, prtinfo.force_fit, prtinfo.round)

    #pdb.set_trace()

    # I still dont understand why some gnucash objects the instance is the swig object
    # but for others the instance object has a this pointer which is the swig object
    # seems to be associated with if the instance is labelled a proxy of a swig object
    # ah - a swig proxy exists when swig has recognized an class object in the underlying
    # language
    # this is also labelled as shadow objects in the swig code
    if hasattr(amnt,"instance"):
        #print("PrintAmount 2", prtinfo, "0x%x"%ctypes.addressof(prtinfo))
        #print("PrintAmount 2", prtinfo.use_separators, prtinfo.use_symbol, prtinfo.use_locale, prtinfo.monetary, prtinfo.force_fit, prtinfo.round)
        # so looks like we can pass by value - and return by value!!
        gncnum_ptr = ctypes.cast( amnt.instance.this.__int__(), ctypes.POINTER( GncNumeric ) )
        #print("gncnum_ptr 0x%x"%amnt.instance.this.__int__(), file=sys.stderr)
        #print("gncnum_ptr 0x%x"%ctypes.addressof(gncnum_ptr.contents), file=sys.stderr)
        prtinfonobitfld_ptr = ctypes.cast( ctypes.addressof(prtinfo), ctypes.POINTER(GncPrintAmountInfoNoBitFld) )
        prtinfonobitfld = prtinfonobitfld_ptr.contents
        #print("PrintAmount 6", prtinfo.use_separators, prtinfo.use_symbol, prtinfo.use_locale, prtinfo.monetary, prtinfo.force_fit, prtinfo.round)
        prtstr_byte = libgnc_apputils.xaccPrintAmount(gncnum_ptr.contents, prtinfonobitfld)
    elif hasattr(amnt,"this"):
        #print("PrintAmount 2", prtinfo, "0x%x"%ctypes.addressof(prtinfo))
        #print("PrintAmount 2", prtinfo.use_separators, prtinfo.use_symbol, prtinfo.use_locale, prtinfo.monetary, prtinfo.force_fit, prtinfo.round)
        # so looks like we can pass by value - and return by value!!
        gncnum_ptr = ctypes.cast( amnt.this.__int__(), ctypes.POINTER( GncNumeric ) )
        #print("gncnum_ptr %x"%amnt.this.__int__(), file=sys.stderr)
        #print("gncnum_ptr %x"%ctypes.addressof(gncnum_ptr.contents), file=sys.stderr)
        prtinfonobitfld_ptr = ctypes.cast( ctypes.addressof(prtinfo), ctypes.POINTER(GncPrintAmountInfoNoBitFld) )
        prtinfonobitfld = prtinfonobitfld_ptr.contents
        #print("PrintAmount 6", prtinfo.use_separators, prtinfo.use_symbol, prtinfo.use_locale, prtinfo.monetary, prtinfo.force_fit, prtinfo.round)
        prtstr_byte = libgnc_apputils.xaccPrintAmount(gncnum_ptr.contents, prtinfonobitfld)
    else:
        # for direct GncNumeric objects (which ar GObjects) the memory address
        # is given by the id value
        pdb.set_trace()
        gncnum_ptr = ctypes.cast( amnt.id, ctypes.POINTER( GncNumeric ) )
        prtinfonobitfld_ptr = ctypes.cast( ctypes.addressof(prtinfo), ctypes.POINTER(GncPrintAmountInfoNoBitFld) )
        prtinfonobitfld = prtinfonobitfld_ptr.contents
        prtstr_byte = libgnc_apputils.xaccPrintAmount(gncnum_ptr, prtinfonobitfld)

    prtstr = prtstr_byte.decode('utf-8')

    #print("Print Amount", prtstr)

    #pdb.set_trace()

    return prtstr
