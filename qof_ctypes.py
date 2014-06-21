

# ctypes interface into libqof


from ctypes.util import find_library

from ctypes import *


import pdb


gboolean = c_byte
gpointer = c_void_p
gcharp = c_char_p
gint = c_int
guint = c_uint
gsize = c_uint

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


libgnc_qofnm = find_library("libgnc-qof")
if libgnc_qofnm is None:
    raise RuntimeError("Can't find a libgnc-qof library to use.")

libgnc_qof = cdll.LoadLibrary(libgnc_qofnm)

class QofDateFormat(object):
    QOF_DATE_FORMAT_US        = 0       # /**< United states: mm/dd/yyyy */
    QOF_DATE_FORMAT_UK        = 1       # /**< Britain: dd/mm/yyyy */
    QOF_DATE_FORMAT_CE        = 2       # /**< Continental Europe: dd.mm.yyyy */
    QOF_DATE_FORMAT_ISO       = 3       # /**< ISO: yyyy-mm-dd */
    QOF_DATE_FORMAT_LOCALE    = 4       # /**< Take from locale information */
    QOF_DATE_FORMAT_UTC       = 5       # /**< UTC: 2004-12-12T23:39:11Z */
    QOF_DATE_FORMAT_CUSTOM    = 6       # /**< Used by the check printing code */


libgnc_qof.qof_date_format_get.argtypes = []
libgnc_qof.qof_date_format_get.restype = c_int

def qof_date_format_get():
    return libgnc_qof.qof_date_format_get()

libgnc_qof.qof_date_format_get_string.argtypes = [c_int]
libgnc_qof.qof_date_format_get_string.restype = c_char_p

def qof_date_format_get_string(date_format):
    return libgnc_qof.qof_date_format_get_string(date_format)

libgnc_qof.qof_date_text_format_get_string.argtypes = [c_int]
libgnc_qof.qof_date_text_format_get_string.restype = c_char_p

def qof_date_text_format_get_string(date_format):
    return libgnc_qof.qof_date_format_get_string(date_format)

libgnc_qof.qof_strftime.argtypes = [c_char_p, gint, c_char_p, POINTER(TM)]
libgnc_qof.qof_strftime.restype = gint

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
    retval = libgnc_qof.qof_strftime(bufptr,256,format,byref(newtm))
    print "qof_strftime", buf.value
    return buf.value

# unfortunately this function is local
#libgnc_qof.qof_format_time.argtypes = [c_char_p, POINTER(tm)]
#libgnc_qof.qof_format_time.restype = c_char_p

#def qof_format_time(format,tm):
#    # this is called by qof_strftime - which then essentially limits the size
#    # of the return string to max
#    # tm is a C struct tm - needs fixing!!
#    return libgnc_qof.qof_strftime(format,tm)
