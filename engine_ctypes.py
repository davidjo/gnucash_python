
#  ctypes access to the engine library

import sys

import os

import ctypes

from ctypes.util import find_library

import gobject

import pdb


import gnucash



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

