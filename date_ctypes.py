

# ctypes access to some date functions

# this should probably go into engine_ctypes
# as we now use the same library

import os

import time
import datetime


from ctypes.util import find_library

from ctypes import *

import sw_app_utils

import swighelpers

import gnucash


import pdb


#gboolean = c_byte
gboolean = c_int
gpointer = c_void_p
gcharp = c_char_p
gint = c_int
guint = c_uint
gsize = c_uint
gint64 = c_longlong

GType = gsize

GTime = c_uint32
GDateYear = c_uint16
GDateDay = c_uint8
GDateMonth = c_uint8
GDateWeekDay = c_uint8


# we need a ctypes definition for struct tm

class TM(Structure):
    _fields_ = [ ("tm_sec", c_int),     # seconds after the minute [0-60]
                 ("tm_min", c_int),     # minutes after the hour [0-59]
                 ("tm_hour", c_int),    # hours since midnight [0-23]
                 ("tm_mday", c_int),    # day of the month [1-31]
                 ("tm_mon", c_int),     # months since January [0-11]
                 ("tm_year", c_int),    # years since 1900
                 ("tm_wday", c_int),    # days since Sunday [0-6]
                 ("tm_yday", c_int),    # days since January 1 [0-365]
                 ("tm_isdst", c_int),   # Daylight Savings Time flag 
                 ("tm_gmtoff", c_long), # offset from UTC in seconds
                 ("tm_zone", c_char_p), # timezone abbreviation
               ]

# I had this - but actually the tv_nsec is just 32 bits - although is
# likely passed in 32 but register
#class Timespec(Structure):
#    _fields_ = [ ("tv_sec", c_int64),      # seconds
#                 ("tv_nsec", c_int64),     # nanoseconds
#               ]
class Timespec(Structure):
    _fields_ = [ ("tv_sec", c_int64),      # seconds
                 ("tv_nsec", c_long),      # nanoseconds
               ]

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

libgnc_engine = CDLL(libgnc_enginenm)


class QofDateFormat(object):
    QOF_DATE_FORMAT_US        = 0       # /**< United states: mm/dd/yyyy */
    QOF_DATE_FORMAT_UK        = 1       # /**< Britain: dd/mm/yyyy */
    QOF_DATE_FORMAT_CE        = 2       # /**< Continental Europe: dd.mm.yyyy */
    QOF_DATE_FORMAT_ISO       = 3       # /**< ISO: yyyy-mm-dd */
    QOF_DATE_FORMAT_LOCALE    = 4       # /**< Take from locale information */
    QOF_DATE_FORMAT_UTC       = 5       # /**< UTC: 2004-12-12T23:39:11Z */
    QOF_DATE_FORMAT_CUSTOM    = 6       # /**< Used by the check printing code */


libgnc_engine.qof_date_format_get.argtypes = []
libgnc_engine.qof_date_format_get.restype = c_int

def qof_date_format_get():
    return libgnc_engine.qof_date_format_get()

libgnc_engine.qof_date_format_get_string.argtypes = [c_int]
libgnc_engine.qof_date_format_get_string.restype = c_char_p

def qof_date_format_get_string(date_format):
    fmtstr = libgnc_engine.qof_date_format_get_string(date_format)
    return fmtstr.decode('utf-8')

libgnc_engine.qof_date_text_format_get_string.argtypes = [c_int]
libgnc_engine.qof_date_text_format_get_string.restype = c_char_p

def qof_date_text_format_get_string(date_format):
    fmtstr = libgnc_engine.qof_date_format_get_string(date_format)
    return fmtstr.decode('utf-8')

# so the time has been messed with right royally
# timespec.i has been removed from the python bindings - which is why some
# date functions are returning Timespec SWIG objects - but the Timespec functions
# still exist and are still used in gnucash itself
# it appears the right function to use is eg gnc_price_get_time64
# - because typemaps to python dates have been added for the time64 type 
# gnc_print_date still uses a Timespec
# the function to use for this seems to be the qof_print_date
# which uses the time64 time type.

libgnc_engine.gnc_print_date.argtypes = [Timespec]
libgnc_engine.gnc_print_date.restype = c_char_p

def gnc_print_date (dttm):
    # stupid but no simple function to do this
    ts_sec = int(dttm.strftime("%s"))
    newts = Timespec()
    newts.tv_sec = ts_sec
    newts.tb_nsec = 0
    datestr = libgnc_engine.gnc_print_date(newts)
    return datestr.decode('utf-8')

libgnc_engine.qof_print_date.argtypes = [c_ulonglong]
libgnc_engine.qof_print_date.restype = c_char_p

def qof_print_date (mytime):
    # print date from mytime in seconds (time64)
    datestr = libgnc_engine.qof_print_date(mytime)
    return datestr.decode('utf-8')

libgnc_engine.qof_scan_date.argtypes = [c_char_p, POINTER(c_int), POINTER(c_int), POINTER(c_int)]
libgnc_engine.qof_scan_date.restype = c_bool

def qof_scan_date(buff):

    myday = c_int(-1)
    mymonth = c_int(-1)
    myyear = c_int(-1)

    retcod = libgnc_engine.qof_scan_date(buff.encode('utf-8'),byref(myday),byref(mymonth),byref(myyear))

    return (retcod, myday.value, mymonth.value, myyear.value)
  

libgnc_engine.qof_strftime.argtypes = [c_char_p, gint, c_char_p, POINTER(TM)]
libgnc_engine.qof_strftime.restype = gint

def qof_strftime(format,tm):
    # tm is a C struct tm - needs fixing!!
    # we need to map from datetime structure to tm
    tmtupl = tm.timetuple()
    newtm = TM()
    newtm.tm_sec = tmtupl.tm_sec
    newtm.tm_min = tmtupl.tm_min
    newtm.tm_hour = tmtupl.tm_hour
    newtm.tm_mday = tmtupl.tm_mday
    newtm.tm_mon = tmtupl.tm_mon - 1
    newtm.tm_year = tmtupl.tm_year - 1900
    newtm.tm_wday = tmtupl.tm_wday
    newtm.tm_yday = tmtupl.tm_yday
    newtm.tm_isdst = tmtupl.tm_isdst
    #newtm.tm_gmtoff = 0
    #newtm.tm_zone = None
    buf = create_string_buffer(256)
    bufptr = cast(byref(buf),c_char_p)
    retval = libgnc_engine.qof_strftime(bufptr,256,format.encode('utf-8'),byref(newtm))
    print("qof_strftime", buf.value)
    return buf.value

# unfortunately this function is local
#libgnc_engine.qof_format_time.argtypes = [c_char_p, POINTER(tm)]
#libgnc_engine.qof_format_time.restype = c_char_p

#def qof_format_time(format,tm):
#    # this is called by qof_strftime - which then essentially limits the size
#    # of the return string to max
#    # tm is a C struct tm - needs fixing!!
#    return libgnc_engine.qof_strftime(format.encode('utf-8'),tm)

# debugging addition while determining why price retrieval seems to have stopped working

libgnc_engine.gnc_pricedb_lookup_nearest_in_time_any_currency.argtypes = [c_void_p, c_void_p, Timespec]
libgnc_engine.gnc_pricedb_lookup_nearest_in_time_any_currency.restype = c_void_p

def gnc_pricedb_lookup_nearest_in_time_any_currency (db, commod, timesec):

    pdb.set_trace()

    tmts = Timespec()
    tmts.tv_sec = timesec
    tmts.tb_nsec = 0

    db_ptr = cast( db.instance.__int__(), POINTER( c_void_p ) )
    commod_ptr = cast( commod.instance.__int__(), POINTER( c_void_p ) )

    prclst_ptr = libgnc_engine.gnc_pricedb_lookup_nearest_in_time_any_currency(db_ptr, commod_ptr, tmts)

    prclstp = cast( prclst_ptr, POINTER( c_void_p ) )


    newlst = []
    ptr_indx = 0
    while True:
       prc_ptr = prclstp[ptr_indx]
       if prc_ptr == None:
           break
       prc = swighelpers.int_to_swig(prc_ptr,"_p_GNCPrice")
       newprc = gnucash.GncPrice(instance=prc)
       newlst.append(newprc)
       ptr_indx += 1


    pdb.set_trace()

    return newlst

