
# ctypes implementation of GncMainWindowActionData


import os


from ctypes import *


gboolean = c_byte
gpointer = c_void_p
guint = c_uint
gsize = c_uint


class GncMainWindowOpaque(Structure):
    pass

class GncPluginPageOpaque(Structure):
    pass

class GncMainWindowActionData(Structure):
    pass
GncMainWindowActionData._fields_ = [
                                    ('window', POINTER(GncMainWindowOpaque)),
                                    ('data', gpointer),
                                   ]

#libgnc_gnomeutilnm = find_library("libgncmod-gnome-utils")
#if libgnc_gnomeutilnm is None:
#    pdb.set_trace()
#    raise RuntimeError("Can't find a libgncmod-gnome-utils library to use.")

libgnc_gnomeutilnm = "/opt/local/lib/gnucash/libgncmod-gnome-utils.dylib"
if not os.path.exists(libgnc_gnomeutilnm):
    pdb.set_trace()
    raise RuntimeError("Can't find a libgncmod-gnome-utils library to use.")

libgnc_gnomeutils = CDLL(libgnc_gnomeutilnm)


libgnc_gnomeutils.gnc_main_window_open_page.argtypes = [ c_void_p, c_void_p ]
libgnc_gnomeutils.gnc_main_window_open_page.restype = None

