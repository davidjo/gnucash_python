

# ctypes interface to some GLib components


from ctypes.util import find_library

from ctypes import *


import pdb


gboolean = c_byte
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

libglib.g_list_last.argtypes = [POINTER(GListRaw)]
libglib.g_list_last.restype = POINTER(GListRaw)

g_key_file_set_list_separator
g_key_file_has_group
g_key_file_get_start_group
g_key_file_set_value
g_key_file_set_double
g_key_file_set_uint64
g_key_file_set_int64
g_key_file_set_integer
g_key_file_set_boolean
g_key_file_get_groups
g_key_file_unref
g_key_file_free
g_key_file_ref
g_key_file_new
g_key_file_error_quark
g_key_file_remove_key
g_key_file_remove_group
g_key_file_has_key
g_key_file_get_comment
g_key_file_remove_comment
g_key_file_set_comment
g_key_file_get_value
g_key_file_get_double
g_key_file_get_uint64
g_key_file_get_int64
g_key_file_get_integer
g_key_file_get_boolean
g_key_file_get_string_list
g_key_file_get_double_list
g_key_file_get_integer_list
g_key_file_get_boolean_list
g_key_file_get_string
g_key_file_get_locale_string
g_key_file_get_locale_string_list
g_key_file_get_keys
g_key_file_load_from_data
g_key_file_load_from_file
g_key_file_load_from_dirs
g_key_file_load_from_data_dirs
g_key_file_to_data
g_key_file_set_double_list
g_key_file_set_integer_list
g_key_file_set_boolean_list
g_key_file_set_locale_string_list
g_key_file_set_locale_string
g_key_file_set_string_list
g_key_file_set_string
