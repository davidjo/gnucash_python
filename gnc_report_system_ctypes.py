

# ctypes access to report-system

import sys

import os

import ctypes

from ctypes.util import find_library

from gi.repository import GObject

import pdb


import gnucash



#pdb.set_trace()


gboolean = ctypes.c_int
gint64 = ctypes.c_longlong
guint8 = ctypes.c_uint8

# we cant search the gnucash sublib directory with find_library
# also to use CDLL means need to detect extension!!
# ah - maybe we can get the extension from core-utils and use that
# it looks as though should be the same
libgnc_coreutilnm = find_library("gnc-core-utils")
libgnc_ext = os.path.splitext(libgnc_coreutilnm)[1]
libgnc_reportsystemnm = os.path.join(os.path.dirname(libgnc_coreutilnm),"gnucash","libgncmod-report-system"+libgnc_ext)
if not os.path.exists(libgnc_reportsystemnm):
    pdb.set_trace()
    raise RuntimeError("Can't find a libgncmod-report-system library to use.")

libgnc_reportsystem = ctypes.CDLL(libgnc_reportsystemnm)

libgnc_reportsystem.gnc_get_default_report_font_family.argtypes = []
libgnc_reportsystem.gnc_get_default_report_font_family.restype = ctypes.c_char_p

# for python 3 need to map this as need conversion from c_char_p to python unicode

def get_default_report_font_family ():

    font_family_byte = libgnc_reportsystem.gnc_get_default_report_font_family()

    return font_family_byte.decode('utf-8')


