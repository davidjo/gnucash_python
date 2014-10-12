
from __future__ import print_function

import sys

import pdb

# emulation of the g_log functions in gnucash
# whats missing is calling function name for the moment

import glib_glog

#pdb.set_trace()

# oh well thats not going to work - we need to pass log_module

def FATAL (log_module, msg):
    glib_glog.libglib.g_log(log_module, glib_glog.GLogLevelFlags.G_LOG_LEVEL_ERROR, msg)
def PERR (log_module, msg):
    glib_glog.libglib.g_log(log_module, glib_glog.GLogLevelFlags.G_LOG_LEVEL_CRITICAL, msg)
def PWARN (log_module, msg):
    glib_glog.libglib.g_log(log_module, glib_glog.GLogLevelFlags.G_LOG_LEVEL_WARNING, msg)
def PINFO (log_module, msg):
    glib_glog.libglib.g_log(log_module, glib_glog.GLogLevelFlags.G_LOG_LEVEL_INFO, msg)
def PDEBUG (log_module, msg):
    glib_glog.libglib.g_log(log_module, glib_glog.GLogLevelFlags.G_LOG_LEVEL_DEBUG, msg)
def ENTER (log_module, msg):
    msg = "[enter : "+msg+"]"
    glib_glog.libglib.g_log(log_module, glib_glog.GLogLevelFlags.G_LOG_LEVEL_DEBUG, msg)
def LEAVE (log_module, msg):
    msg = "[leave : "+msg+"]"
    glib_glog.libglib.g_log(log_module, glib_glog.GLogLevelFlags.G_LOG_LEVEL_DEBUG, msg)


# create a gnc_error message function to emulate the scheme error functions
def gnc_msg (msg):
    glib_glog.libglib.g_log("gnc.python", glib_glog.GLogLevelFlags.G_LOG_LEVEL_MESSAGE, msg)
def gnc_warn (msg):
    glib_glog.libglib.g_log("gnc.python", glib_glog.GLogLevelFlags.G_LOG_LEVEL_WARNING, msg)
def gnc_error (msg):
    glib_glog.libglib.g_log("gnc.python", glib_glog.GLogLevelFlags.G_LOG_LEVEL_CRITICAL, msg)
def gnc_debug (msg):
    glib_glog.libglib.g_log("gnc.python", glib_glog.GLogLevelFlags.G_LOG_LEVEL_DEBUG, msg)


# some junky print functions for debugging
# so can turn them off easily
debug = False
#debug = True

def dbglog(*args):
    #pdb.set_trace()
    if debug:
        print(*args)

def dbglog_err(*args):
    #pdb.set_trace()
    if debug:
        print(*args,file=sys.stderr)
