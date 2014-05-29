

# emulation of the g_log functions in gnucash
# whats missing is calling function name for the moment

import glib_glog

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

