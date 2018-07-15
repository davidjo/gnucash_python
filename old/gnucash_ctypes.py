

# ctypes interface to some GLib components

# ctypes interface into gnucash libraries

# qof section no longer useful from gnucash 3 onwards as all in libgncmod-engine now
# the glib stuff is in glib_ctypes


from ctypes.util import find_library

from ctypes import *


import pdb


#gboolean = c_byte
gboolean = c_int
gpointer = c_void_p
guint = c_uint
gsize = c_uint

GType = gsize

GTime = c_uint32
GDateYear = c_uint16
GDateDay = c_uint8
GDateMonth = c_uint8
GDateWeekDay = c_uint8

class GDateRaw(Structure):
    pass
GDateRaw._fields_ = [
                     ('julian_days', guint, 32),
                     ('julian', guint, 1),
                     ('dmy', guint, 1),
                     ('day', guint, 6),
                     ('month', guint, 4),
                     ('year', guint, 16),
                    ]

class GListRaw(Structure):
    pass
GListRaw._fields_ = [
                     ('data', gpointer),
                     ('next', POINTER(GListRaw)),
                     ('prev', POINTER(GListRaw)),
                    ]


class GHashTableOpaque(Structure):
    pass


libglibnm = find_library("libglib-2.0")
if libglibnm is None:
    raise RuntimeError("Can't find a libglib-2.0 library to use.")

libglib = cdll.LoadLibrary(libglibnm)


libglib.g_date_valid.argtypes = [POINTER(GDateRaw)]
libglib.g_date_valid.restype = gboolean

libglib.g_date_get_weekday.argtypes = [POINTER(GDateRaw)]
libglib.g_date_get_weekday.restype = GDateWeekDay
libglib.g_date_get_month.argtypes = [POINTER(GDateRaw)]
libglib.g_date_get_month.restype = GDateMonth
libglib.g_date_get_year.argtypes = [POINTER(GDateRaw)]
libglib.g_date_get_year.restype = GDateYear
libglib.g_date_get_julian.argtypes = [POINTER(GDateRaw)]
libglib.g_date_get_julian.restype = c_uint32
libglib.g_date_get_day_of_year.argtypes = [POINTER(GDateRaw)]
libglib.g_date_get_day_of_year.restype = c_uint

libglib.g_date_set_day.argtypes = [POINTER(GDateRaw),GDateDay]
libglib.g_date_set_day.restype = None
libglib.g_date_set_month.argtypes = [POINTER(GDateRaw),GDateMonth]
libglib.g_date_set_month.restype = None
libglib.g_date_set_year.argtypes = [POINTER(GDateRaw),GDateYear]
libglib.g_date_set_year.restype = None
libglib.g_date_set_julian.argtypes = [POINTER(GDateRaw),c_uint32]
libglib.g_date_set_julian.restype = None
libglib.g_date_set_dmy.argtypes = [POINTER(GDateRaw),GDateDay,GDateMonth,GDateYear]
libglib.g_date_set_dmy.restype = None

libglib.g_date_free.argtypes = [POINTER(GDateRaw)]
libglib.g_date_free.restype = None


libglib.g_list_last.argtypes = [POINTER(GListRaw)]
libglib.g_list_last.restype = POINTER(GListRaw)
libglib.g_list_first.argtypes = [POINTER(GListRaw)]
libglib.g_list_first.restype = POINTER(GListRaw)
libglib.g_list_nth.argtypes = [POINTER(GListRaw)]
libglib.g_list_nth.restype = POINTER(GListRaw)
libglib.g_list_nth_data.argtypes = [POINTER(GListRaw)]
libglib.g_list_nth_data.restype = gpointer
libglib.g_list_length.argtypes = [POINTER(GListRaw)]
libglib.g_list_length.restype = guint
libglib.g_list_free.argtypes = [POINTER(GListRaw)]
libglib.g_list_free.restype = None


libglib.g_hash_table_get_keys.argtypes = [POINTER(GHashTableOpaque)]
libglib.g_hash_table_get_keys.restype = POINTER(GListRaw)
libglib.g_hash_table_get_values.argtypes = [POINTER(GHashTableOpaque)]
libglib.g_hash_table_get_values.restype = POINTER(GListRaw)


class GList(list):

    def __init__ (self,instance=None):
        if instance == None:
            raise Exception(
                "you must call GList.__init__ "
                "with an existing "
                "low level swig proxy in the argument instance")
        self.instance = instance

    def __len__ (self):
        #pdb.set_trace()
        if self.instance == None:
            raise Exception("No low level GList instance defined")
        clen = libglib.g_list_length(self.instance)
        return clen

    def __getitem__ (self, indx):
        #pdb.set_trace()
        if self.instance == None:
            raise Exception("No low level GList instance defined")
        dataptr = libglib.g_list_nth_data(self.instance, indx)
        return dataptr

    #def free (self):
    #    # junk fix up - special free function to free the raw GList
    #    pdb.set_trace()
    #    libglib.g_list_free(self.instance)
    #    self.instance = None



class QofBookOpaque(Structure):
    pass

QofIdType = c_char_p

class QofCollectionRaw(Structure):
    _fields_ = [
                ('e_type', c_char_p),
                ('is_dirty', gboolean),
                ('hash_of_entities', POINTER(GHashTableOpaque)),
                ('data', gpointer),
               ]





class GncGUIDRaw(Structure):
    GUID_DATA_SIZE = 16
    _fields_ = [
                ('data', c_ubyte*16),
               ]

#libgncofxnm = find_library("gnucash/libgncmod-ofx")
#if libgncofxnm is None:
#    raise RuntimeError("Can't find a libgncmod-ofx library to use.")
libgncofxnm = "/opt/local/lib/gnucash/libgncmod-ofx.dylib"
libgnc_ofx = cdll.LoadLibrary(libgncofxnm)




libgnc_qofnm = find_library("libgnc-qof")
if libgnc_qofnm is None:
    raise RuntimeError("Can't find a libgnc-qof library to use.")


libgnc_qof = cdll.LoadLibrary(libgnc_qofnm)

libgnc_qof.qof_book_get_collection.argtypes = [POINTER(QofBookOpaque),QofIdType]
libgnc_qof.qof_book_get_collection.restype = POINTER(QofCollectionRaw)

def qof_book_get_collection (swig_book_instance, collection_id):
    #pdb.set_trace()
    # so I can convert SWIG pointer to C pointer for ctypes
    swig_book_ptr = cast( swig_book_instance.__long__(), POINTER( QofBookOpaque ) )
    col = libgnc_qof.qof_book_get_collection(swig_book_ptr, collection_id)
    typstr = col.contents.e_type
    hsh = col.contents.hash_of_entities
    return col

def glib_hash_table_get_keys (hsh):
    # note this allocates a new GList - we need to free it specially
    # so best approach is to copy to python list and free
    keys = libglib.g_hash_table_get_keys(hsh)
    # ah - the keys are guids - or pointers to guids
    # but we have a problem - we dont have the GncGUID class here
    # data value for c_void_p is a plain integer!!
    keys = GList(keys)
    kylst = [ky for ky in keys]
    return kylst

def glib_hash_table_get_values (hsh):
    # vals should be pointers to budgets
    # - but how to map to SWIG??
    vals = libglib.g_hash_table_get_values(hsh)
    vals = GList(vals)
    dt = vals[0]

def qof_budget_convert (hsh):
    #pdb.set_trace()
    # note this allocates a new GList - we need to free it specially
    # so best approach is to copy to python list and free
    keys = libglib.g_hash_table_get_keys(hsh)
    # ah - the keys are guids - or pointers to guids
    # but we have a problem - we dont have the GncGUID class here
    # data value for c_void_p is a plain integer!!
    kylen = libglib.g_list_length(keys)
    #keys = GList(keys)
    nwkys = []
    #for ky in keys:
    for indx in xrange(kylen):
        ky = libglib.g_list_nth_data(keys, indx)
        nwvl = cast(ky, POINTER(GncGUIDRaw))
        nwkys.append(nwvl)
    #return [ky for ky in keys]
    return nwkys


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

    #pdb.set_trace()

    acc_ptr = cast( self.instance.__long__(), POINTER( QofInstanceOpaque ) )

    kvp_frame_ptr = libgnc_qof.qof_instance_get_slots(acc_ptr)

    if assocacc != None:

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


    # amazing - this does appear to work in that the value and slot
    # are deleted by passing None to libgnc_qof.kvp_frame_set_slot_nc

    self.BeginEdit()

    libgnc_qof.kvp_frame_set_slot_nc(kvp_frame_ptr, slotnm, None)

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


