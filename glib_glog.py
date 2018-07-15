

# ctypes interface to some glog components


from ctypes.util import find_library

from ctypes import *


import pdb


gchar = c_char
gcharp = c_char_p
#gboolean = c_byte
gboolean = c_int
gpointer = c_void_p
guint = c_uint
gsize = c_uint
gint = c_int

GType = gsize

libglibnm = find_library("libglib-2.0")
if libglibnm is None:
    raise RuntimeError("Can't find a libglib-2.0 library to use.")

libglib = cdll.LoadLibrary(libglibnm)

G_LOG_DOMAIN = None

# this is an enum which I think we can define in ctypes
class GLogLevelFlags(object):
    G_LOG_FLAG_RECURSION = (1 << 0)
    G_LOG_FLAG_FATAL = (1 << 1)
    G_LOG_LEVEL_ERROR = (1 << 2)
    G_LOG_LEVEL_CRITICAL = (1 << 3)
    G_LOG_LEVEL_WARNING = (1 << 4)
    G_LOG_LEVEL_MESSAGE = (1 << 5)
    G_LOG_LEVEL_INFO = (1 << 6)
    G_LOG_LEVEL_DEBUG = (1 << 7)
    G_LOG_LEVEL_MASK = ~((1 << 0) | (1 << 1))

# cant use this - variable arguments
# so will need to just format to a string then passes that only to g_log
libglib.g_log.argtypes = [gcharp,gint,gcharp]
libglib.g_log.restype = None

GLOGFUNC = CFUNCTYPE(None, gcharp, gint, gcharp, gpointer)

libglib.g_log_set_handler.argtypes = [gcharp, gint, GLOGFUNC, gpointer]
libglib.g_log_set_handler.restype = guint

libglib.g_log_remove_handler.argtypes = [gcharp, gint]
libglib.g_log_remove_handler.restype = None

libglib.g_log_default_handler.argtypes = [gcharp, gint, gcharp, gpointer]
libglib.g_log_default_handler.restype = None

libglib.g_log_set_default_handler.argtypes = [GLOGFUNC, gpointer]
libglib.g_log_set_default_handler.restype = GLOGFUNC

# still not sure if should re-implement here with the required type conversions

def glog (logmodule, loglevel, logstr):
    pdb.set_trace()
    libglib.g_log(logmodule.encode('utf-8'), loglevel, logstr.encode('utf-8'))
