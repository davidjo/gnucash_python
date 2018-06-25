
#  ctypes access to the engine library

import sys

import os

import ctypes

from ctypes.util import find_library
from ctypes import Structure
from ctypes import c_int64
from ctypes import c_long

#from gi.repository import GObject

import pdb


import gnucash


import glib_ctypes


#pdb.set_trace()


gboolean = ctypes.c_int
gint64 = ctypes.c_longlong
guint8 = ctypes.c_uint8

class GncCommodityOpaque(ctypes.Structure):
    pass

# we cant search the gnucash sublib directory with find_library
# also to use CDLL means need to detect extension!!
# ah - maybe we can get the extension from core-utils and use that
# it looks as though should be the same
libgnc_coreutilnm = find_library("gnc-core-utils")
libgnc_ext = os.path.splitext(libgnc_coreutilnm)[1]
libgnc_enginenm = os.path.join(os.path.dirname(libgnc_coreutilnm),"gnucash","libgncmod-engine"+libgnc_ext)
if not os.path.exists(libgnc_enginenm):
    pdb.set_trace()
    raise RuntimeError("Can't find a libgncmod-engine library to use.")

# theres no good way to do this
# we have to access the returned commodity by ctypes, get the individual values
# and create new GncCommodity using these values

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

# these are GncCommodity type arguments
libgnc_engine.gnc_commodity_equiv.argtypes = [ ctypes.c_void_p, ctypes.c_void_p ]
libgnc_engine.gnc_commodity_equiv.restype = ctypes.c_bool

libgnc_engine.gnc_commodity_is_currency.argtypes = [ ctypes.c_void_p ]
libgnc_engine.gnc_commodity_is_currency.restype = ctypes.c_bool


# add in gnc_get_account_separator_string

gcharp = ctypes.c_char_p

libgnc_engine.gnc_get_account_separator_string.argtypes = []
libgnc_engine.gnc_get_account_separator_string.restype = gcharp



# these really should be Account functions
# GNCAccountType is an enum
GNCAccountType = ctypes.c_uint
libgnc_engine.xaccParentAccountTypesCompatibleWith.argtypes = [ GNCAccountType ]
libgnc_engine.xaccParentAccountTypesCompatibleWith.restype = ctypes.c_uint

libgnc_engine.xaccAccountTypesValid.argtypes = []
libgnc_engine.xaccAccountTypesValid.restype = ctypes.c_uint


# for some reason a lot of the Query.h functions are not included in the swig bindings
# for python (but are for guile)

libgnc_engine.xaccQueryAddSingleAccountMatch.argtypes = [ ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint ]
libgnc_engine.xaccQueryAddSingleAccountMatch.restype = None

libgnc_engine.xaccQueryAddDateMatch.argtypes = [ ctypes.c_void_p, ctypes.c_bool, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint ]
libgnc_engine.xaccQueryAddDateMatch.restype = None

# to pass structs by value need to define struct
class Timespec(Structure):
    _fields_ = [ ("tv_sec", c_int64),      # seconds
                 ("tv_nsec", c_long),      # nanoseconds
               ]

libgnc_engine.xaccQueryAddDateMatchTS.argtypes = [ ctypes.c_void_p, ctypes.c_bool, Timespec, ctypes.c_bool, Timespec, ctypes.c_uint ]
libgnc_engine.xaccQueryAddDateMatchTS.restype = None



# for some reason a lot of the Query.h functions are not included in the swig bindings
# for python (but are for guile)

libgnc_engine.xaccQueryAddSingleAccountMatch.argtypes = [ ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint ]
libgnc_engine.xaccQueryAddSingleAccountMatch.restype = None

libgnc_engine.xaccQueryAddDateMatch.argtypes = [ ctypes.c_void_p, ctypes.c_bool, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint ]
libgnc_engine.xaccQueryAddDateMatch.restype = None

# to pass structs by value need to define struct
class Timespec(Structure):
    _fields_ = [ ("tv_sec", c_int64),      # seconds
                 ("tv_nsec", c_long),      # nanoseconds
               ]

libgnc_engine.xaccQueryAddDateMatchTS.argtypes = [ ctypes.c_void_p, ctypes.c_bool, Timespec, ctypes.c_bool, Timespec, ctypes.c_uint ]
libgnc_engine.xaccQueryAddDateMatchTS.restype = None

# what should enums be - c_uint or c_int?
# apparently is variable
libgnc_engine.xaccQueryAddClearedMatch.argtypes = [ ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint ]
libgnc_engine.xaccQueryAddClearedMatch.restype = None

libgnc_engine.xaccQueryAddAccountMatch.argtypes = [ ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint ]
libgnc_engine.xaccQueryAddAccountMatch.restype = None


class GncCommodityOpaque(Structure):
    pass

def CommodityEquiv (a, b):
    a_ptr = ctypes.cast( a.instance.__long__(), ctypes.POINTER( GncCommodityOpaque ) )
    b_ptr = ctypes.cast( b.instance.__long__(), ctypes.POINTER( GncCommodityOpaque ) )
    retval = libgnc_engine.gnc_commodity_equiv(a_ptr, b_ptr)
    # this is returning a ctypes.c_bool type  - convert to basic python type??
    return retval

def CommodityIsCurrency (a):
    a_ptr = ctypes.cast( a.instance.__long__(), ctypes.POINTER( GncCommodityOpaque ) )
    retval = libgnc_engine.gnc_commodity_is_currency(a_ptr)
    # this is returning a ctypes.c_bool type  - convert to basic python type??
    return retval


def GetAccountSeparatorString ():
    # note that the return here should be a simple python string
    # auto magic conversion from c_char_p
    sepstr = libgnc_engine.gnc_get_account_separator_string()
    return sepstr

def ParentAccountTypesCompatibleWith (account_type):
    retval = libgnc_engine.xaccParentAccountTypesCompatibleWith(account_type)
    return retval

def AccountTypesValid ():
    retval = libgnc_engine.xaccAccountTypesValid()
    return retval


class QofQueryOpaque(Structure):
    pass

class GNCAccountOpaque(Structure):
    pass


def AddSingleAccountMatch (query, account, matchop):
    #pdb.set_trace()
    query_ptr = ctypes.cast( query.instance.__long__(), ctypes.POINTER( QofQueryOpaque ) )
    acc_ptr = ctypes.cast( account.instance.__long__(), ctypes.POINTER( GNCAccountOpaque ) )
    libgnc_engine.xaccQueryAddSingleAccountMatch(query_ptr, acc_ptr, matchop)

def AddDateMatchTS (query, use_from, from_date, use_to, to_date, matchop):
    #pdb.set_trace()

    query_ptr = ctypes.cast( query.instance.__long__(), ctypes.POINTER( QofQueryOpaque ) )

    # stupid but no simple function to do this
    if use_from:
        from_sec = int(from_date.strftime("%s"))
    else:
        from_sec = 0
    fromts = Timespec()
    fromts.tv_sec = from_sec
    fromts.tb_nsec = 0

    if use_to:
        to_sec = int(to_date.strftime("%s"))
    else:
        to_sec = 0
    tots = Timespec()
    tots.tv_sec = to_sec
    tots.tb_nsec = 0

    libgnc_engine.xaccQueryAddDateMatchTS(query_ptr, use_from, fromts, use_to, tots, matchop)

def AddClearedMatch (query, cleared_flag, matchop):
    #pdb.set_trace()
    query_ptr = ctypes.cast( query.instance.__long__(), ctypes.POINTER( QofQueryOpaque ) )
    libgnc_engine.xaccQueryAddClearedMatch(query_ptr, cleared_flag, matchop)

def AddAccountMatch (query, accounts, howmatch, matchop):
    pdb.set_trace()
    # this is not simple - we have to convert the python list to a GList
    # and is not working - if add this get every single split!!
    query_ptr = ctypes.cast( query.instance.__long__(), ctypes.POINTER( QofQueryOpaque ) )
    if len(accounts) > 0:
        # construct a g_list from list of accounts
        glst_ptr = None
        for elm in accounts:
            acc_ptr = ctypes.cast( elm.instance.__long__(), ctypes.POINTER( GNCAccountOpaque ) )
            glst_ptr = glib_ctypes.libglib.g_list_prepend(glst_ptr,acc_ptr)
        glst_ptr = glib_ctypes.libglib.g_list_reverse(glst_ptr)
        print "glst_ptr", "0x%x"%ctypes.addressof(glst_ptr)
        #gnucash_log.dbglog_err("0x%x"%ctypes.addressof(glst_ptr))
        #pdb.set_trace()
        libgnc_engine.xaccQueryAddAccountMatch(query_ptr, glst_ptr, howmatch, matchop)
        # does removing this make it work?? 
        #glib_ctypes.libglib.g_list_free(glst_ptr)
