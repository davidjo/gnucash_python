
# we need a wrapper around _sw_core_utils.py
# also need to import the python bindings for wrapping
# some returns in reasonable type
# - at the moment the core_utils python bindings are very crude

import sys

import ctypes

import pdb


import _sw_core_utils

import gnucash

print "COREUTILS"
print dir(_sw_core_utils)
print "COREUTILS"


#pdb.set_trace()

gnc_locale_default_iso_currency_code = _sw_core_utils.gnc_locale_default_iso_currency_code

gnc_path_find_localized_html_file = _sw_core_utils.gnc_path_find_localized_html_file

print "coreutilsjunk"
