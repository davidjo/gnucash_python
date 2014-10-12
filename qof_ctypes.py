

# ctypes interface into libqof


import time
import datetime


from ctypes.util import find_library

from ctypes import *

import sw_app_utils


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

class Timespec(Structure):
    _fields_ = [ ("tv_sec", c_int64),      # seconds
                 ("tv_nsec", c_int64),     # nanoseconds
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

libgnc_qof.gnc_print_date.argtypes = [Timespec]
libgnc_qof.gnc_print_date.restype = c_char_p

def gnc_print_date (dttm):
    # stupid but no simple function to do this
    ts_sec = int(dttm.strftime("%s"))
    newts = Timespec()
    newts.tv_sec = ts_sec
    newts.tb_nsec = 0
    return libgnc_qof.gnc_print_date(newts)

libgnc_qof.qof_print_date.argtypes = [c_ulonglong]
libgnc_qof.qof_print_date.restype = c_char_p

def qof_print_date (mytime):
    # print date from mytime in seconds (time64)
    return libgnc_qof.qof_print_date(mytime)

libgnc_qof.qof_scan_date.argtypes = [c_char_p, POINTER(c_int), POINTER(c_int), POINTER(c_int)]
libgnc_qof.qof_scan_date.restype = c_bool

def qof_scan_date(buff):

    myday = c_int(-1)
    mymonth = c_int(-1)
    myyear = c_int(-1)

    retcod = libgnc_qof.qof_scan_date(buff,byref(myday),byref(mymonth),byref(myyear))

    return (retcod, myday.value, mymonth.value, myyear.value)
  

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


class GncGUIDRaw(Structure):
    GUID_DATA_SIZE = 16
    _fields_ = [
                ('data', c_ubyte*16),
               ]


class QofInstanceOpaque(Structure):
    pass

class KvpFrameOpaque(Structure):
    pass

class KvpValueOpaque(Structure):
    pass

libgnc_qof.qof_instance_set_dirty.argtypes = [POINTER(QofInstanceOpaque)]
libgnc_qof.qof_instance_set_dirty.restype = None

libgnc_qof.qof_instance_get_slots.argtypes = [POINTER(QofInstanceOpaque)]
libgnc_qof.qof_instance_get_slots.restype = POINTER(KvpFrameOpaque)

libgnc_qof.qof_instance_get_guid.argtypes = [POINTER(QofInstanceOpaque)]
libgnc_qof.qof_instance_get_guid.restype = POINTER(GncGUIDRaw)


# ah - I think I understand the kvp system - this is a hash/python dict
# type system using glib hashes
# it appears a lot of information is stored in these structures that
# is often not available in the GUI
# Im confused by usage of slot and value - they seem the same
# yes kvp_frame_get_value is implemented as kvp_frame_get_slot
# ie the value is the return of kvp_frame_get_slot

# what should really do here is implement these as a Python dict equivalent

# kvp_frame_get_frame_slash creates path if doesnt exist
# kvp_frame_get_frame returns NULL if path doesnt exist

libgnc_qof.kvp_frame_get_frame.argtypes = [POINTER(KvpFrameOpaque), c_char_p]
libgnc_qof.kvp_frame_get_frame.restype = POINTER(KvpFrameOpaque)

libgnc_qof.kvp_frame_get_frame_slash.argtypes = [POINTER(KvpFrameOpaque), c_char_p]
libgnc_qof.kvp_frame_get_frame_slash.restype = POINTER(KvpFrameOpaque)

libgnc_qof.kvp_frame_get_slot.argtypes = [POINTER(KvpFrameOpaque), c_char_p]
libgnc_qof.kvp_frame_get_slot.restype = POINTER(KvpValueOpaque)

libgnc_qof.kvp_frame_get_guid.argtypes = [POINTER(KvpFrameOpaque)]
libgnc_qof.kvp_frame_get_guid.restype = POINTER(GncGUIDRaw)

libgnc_qof.kvp_value_get_guid.argtypes = [POINTER(KvpValueOpaque)]
libgnc_qof.kvp_value_get_guid.restype = POINTER(GncGUIDRaw)

libgnc_qof.kvp_value_new_guid.argtypes = [POINTER(GncGUIDRaw)]
libgnc_qof.kvp_value_new_guid.restype = POINTER(KvpValueOpaque)

libgnc_qof.kvp_value_get_gint64.argtypes = [POINTER(KvpFrameOpaque), c_char_p]
libgnc_qof.kvp_value_get_gint64.restype = gint64

libgnc_qof.kvp_value_get_double.argtypes = [POINTER(KvpFrameOpaque), c_char_p]
libgnc_qof.kvp_value_get_double.restype = c_double

libgnc_qof.kvp_frame_get_frame_slash.argtypes = [POINTER(KvpFrameOpaque), c_char_p]
libgnc_qof.kvp_frame_get_frame_slash.restype = POINTER(KvpFrameOpaque)

# ah - _nc means the value is not copied
# so need to worry about where eg pointers are allocated

libgnc_qof.kvp_frame_set_slot_nc.argtypes = [POINTER(KvpFrameOpaque), c_char_p, POINTER(KvpValueOpaque)]
libgnc_qof.kvp_frame_set_slot_nc.restype = None

class KvpSlots(object):

    def __init__ (self):
        pdb.set_trace()
        # what to do here
        self.slots = None

    @classmethod
    def FromSlots (cls, acc):

        pdb.set_trace()

        acc_ptr = cast( acc.instance.__long__(), POINTER( QofInstanceOpaque ) )

        self.slots = libgnc_qof.qof_instance_get_slots(acc_ptr)


class Kvp(object):

    def __init__ (self, kvp_frame_ptr):
        self.kvp_frame_ptr = kvp_frame_ptr

    def GetSlot (self, slotnm):

        pdb.set_trace()

        kvp_value_ptr = libgnc_qof.kvp_frame_get_slot(self.kvp_frame_ptr, slotnm)

        return kvp_value_ptr


class QofBookOpaque(Structure):
    pass

libgnc_qof.qof_book_get_slots.argtypes = [POINTER(QofBookOpaque)]
libgnc_qof.qof_book_get_slots.restype = POINTER(KvpFrameOpaque)

def get_fy_end ():

    pdb.set_trace()

    book = sw_app_utils.get_current_book()

    book_ptr = cast( book.instance.__long__(), POINTER( QofBookOpaque ) )

    book_frame = libgnc_qof.qof_book_get_slots(book_ptr)

    month = libgnc_qof.kvp_frame_get_gint64(book_frame,"/book/fyear_end/month")
    day = libgnc_qof.kvp_frame_get_gint64(book_frame,"/book/fyear_end/day")

    # here there is a call to g_date_valid_dmy - not sure this is callable
    #if g_date_valid_dmy(day, month, 2005):
    #    return g_date_new_dmy(day, month, G_DATE_BAD_YEAR)
    dttm = datetime.datetime(year=2005,month=month+1,day=day+1)
    return dttm



# not sure what to do here
# - do we use the ofx import routines directly
# (loaded from gnucash/libgncmod-ofx.dylib)
# or as below re-implement them (meaning if C code changes we need to update below)

def GetAssociatedAccountGUIDString (self, slotnm):

    #pdb.set_trace()

    acc_ptr = cast( self.instance.__long__(), POINTER( QofInstanceOpaque ) )

    kvp_frame_ptr = libgnc_qof.qof_instance_get_slots(acc_ptr)

    kvp_value_ptr = libgnc_qof.kvp_frame_get_slot(kvp_frame_ptr, slotnm)

    try:
        jnk = kvp_value_ptr.contents
    except ValueError:
        #raise KeyError()
        return None
    else:
        kvguid = libgnc_qof.kvp_value_get_guid(kvp_value_ptr)
        #pdb.set_trace()
        return "".join([ "%02x"%x for x in kvguid.contents.data ])

def SetAssociatedAccount (self, slotnm, assocacc):

    pdb.set_trace()

    acc_ptr = cast( self.instance.__long__(), POINTER( QofInstanceOpaque ) )

    kvp_frame_ptr = libgnc_qof.qof_instance_get_slots(acc_ptr)

    assocguid = assocacc.GetGUID()

    # need to munge swig GUID to ctypes GUID
    # new feature - why is data object in GncGUID
    # - this is what has the long
    # how would you know which type had data??
    # weird - the object this should store the underlying native object
    # assocguid.instance.data.__long__() == assocguid.instance.this.__long__()
    newguid = GncGUIDRaw()
    guid_ptr = cast( assocguid.instance.data.__long__(), POINTER( GncGUIDRaw ) )

    kvp_value_ptr = libgnc_qof.kvp_value_new_guid(guid_ptr)

    self.BeginEdit()

    libgnc_qof.kvp_frame_set_slot_nc(kvp_frame_ptr, slotnm, kvp_value_ptr)

    libgnc_qof.qof_instance_set_dirty(acc_ptr)

    self.CommitEdit()

    return None


def GetGainAcctGUIDString (self, slotnm, currencynm):

    pdb.set_trace()

    kvpslots = Kvp.FromSlots(self)

    kvp_value_ptr = kvpslots.GetSlot(slotnm)

    kvpobj = Kvp(cast( kvp_value_ptr, POINTER(KvpFrameOpaque) ))

    kvp_value_ptr = kvpobj.GetSlot(currencynm)

    try:
        jnk = kvp_value_ptr.contents
    except ValueError:
        #raise KeyError()
        return None
    else:
        kvguid = libgnc_qof.kvp_value_get_guid(kvp_value_ptr)
        #pdb.set_trace()
        return "".join([ "%02x"%x for x in kvguid.contents.data ])


