
import sys

import os

import gc

import ctypes


import pdb
import traceback


def N_(msg):
    return msg

# ctypes access to gnc_html and gnc_html_extras functions
# - mainly for build_url

class URLTypes(object):
    URL_TYPE_FILE       = "file"
    URL_TYPE_JUMP       = "jump"
    URL_TYPE_HTTP       = "http"
    URL_TYPE_FTP        = "ftp"
    URL_TYPE_SECURE     = "secure"
    URL_TYPE_REGISTER   = "register"   # /* for gnucash register popups */
    URL_TYPE_ACCTTREE   = "accttree"   # /* for account tree windows */
    URL_TYPE_REPORT     = "report"     # /* for gnucash report popups */
    URL_TYPE_OPTIONS    = "options"    # /* for editing report options */
    URL_TYPE_SCHEME     = "scheme"     # /* for scheme code evaluation */
    URL_TYPE_HELP       = "help"       # /* for a gnucash help window */
    URL_TYPE_XMLDATA    = "xmldata"    # /* links to gnucash XML data files */
    URL_TYPE_PRICE      = "price"      # /* for price editor popups */
    URL_TYPE_OTHER      = "other"
    URL_TYPE_BUDGET     = "budget"


# we cant search the gnucash sublib directory with find_library
# also to use CDLL means need to detect extension!!
# ah - maybe we can get the extension from core-utils and use that
# it looks as though should be the same
libgnc_coreutilnm = ctypes.util.find_library("gnc-core-utils")
libgnc_ext = os.path.splitext(libgnc_coreutilnm)[1]
libgnc_htmlnm = os.path.join(os.path.dirname(libgnc_coreutilnm),"gnucash","libgncmod-html"+libgnc_ext)
if not os.path.exists(libgnc_htmlnm):
    pdb.set_trace()
    raise RuntimeError("Can't find a libgncmod-html library to use.")

libgnc_html = ctypes.CDLL(libgnc_htmlnm)



gcharp = ctypes.c_char_p
URLType = gcharp

libgnc_html.gnc_build_url.argtypes = [ URLType, gcharp, gcharp ]
libgnc_html.gnc_build_url.restype = gcharp

def build_url (urltype, location, label):
    #pdb.set_trace()
    # for python 3 we need to convert from str type (unicode) to plain byte strings
    urltype_byte = urltype.encode('utf-8')
    location_byte = location.encode('utf-8')
    if label != None:
        label_byte = location.encode('utf-8')
    else:
        label_byte = None
    urlstr = libgnc_html.gnc_build_url(urltype_byte, location_byte, label_byte)
    return urlstr.decode('utf-8')


