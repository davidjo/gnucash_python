
# this is primarily to access gnc_main_window_open_report
# which seems to be the primary access into creating a report page

import os

from ctypes import *

import pdb


# should really include this from gnc_main_window

class GncMainWindowOpaque(Structure):
    pass


libgnc_reportgnomenm = "/opt/local/lib/gnucash/libgncmod-report-gnome.dylib"
if not os.path.exists(libgnc_reportgnomenm):
    pdb.set_trace()
    raise RuntimeError("Can't find a libgncmod-report-gnome library to use.")

libgnc_reportgnome = CDLL(libgnc_reportgnomenm)

#libgnc_reportgnome.gnc_main_window_open_report.argtypes = [ c_int, POINTER(GncMainWindowOpaque) ]
libgnc_reportgnome.gnc_main_window_open_report.argtypes = [ c_int, c_void_p ]
libgnc_reportgnome.gnc_main_window_open_report.restype = None


class GncPluginPageReport(object):

    def __init__ (self):
        pass

    # for the moment not creating instance
    @classmethod
    def OpenReport (cls, report_id, window):
        #
        # how to handle window
        pdb.set_trace()
        #window_ptr = cast(window, POINTER(GncMainWindowOpaque))
        libgnc_reportgnome.gnc_main_window_open_report(report_id,window)
