
# ctypes wrap of GncPluginManager

import os

import sys

import ctypes

from ctypes import Structure

from ctypes import POINTER

from ctypes import CDLL

from ctypes.util import find_library


from pygobjectcapi import PyGObjectCAPI
#from pygobjectcapi_gi import PyGObjectCAPI

# call like this:
# Cgobject = PyGObjectCAPI()
# Cgobject.to_object(memory_address)

# to get memory address from a gobject:
#  address = hash(obj)

# this doesnt seem to be useful - it seems primarily to be used to
# define argument or return types in order to introspect higher level
# libraries - not for GLib functions itself
# eg GList is defined as a record but all glist functions are set as
# introspectable=0 - which means they are ignored/not implemented
#from gi.repository import GLib

# so for the moment use the glib_ctypes wrap
import glib_ctypes


import pdb


# use this to gain access to a quit function

libgnccorenm = find_library("libgnc-core-utils")
if libgnccorenm is None:
    raise RuntimeError("Can't find a libgnc-core-utils library to use.")

#print(libgnccorenm)

libpth = os.path.dirname(libgnccorenm)


libgnc_gnomeutils = CDLL(os.path.join(libpth,"gnucash","libgncmod-gnome-utils.dylib"))


class GncPluginManagerOpaque(Structure):
    pass

class GncPluginOpaque(Structure):
    pass

class GListOpaque(Structure):
    pass

GncPluginManagerOpaquePtr = POINTER(GncPluginManagerOpaque)
GncPluginOpaquePtr = POINTER(GncPluginOpaque)
GListOpaquePtr = POINTER(GListOpaque)

libgnc_gnomeutils.gnc_plugin_manager_get.argtypes = []
libgnc_gnomeutils.gnc_plugin_manager_get.restype = GncPluginManagerOpaquePtr

libgnc_gnomeutils.gnc_plugin_manager_add_plugin.argtypes = [ GncPluginManagerOpaquePtr, GncPluginOpaquePtr ]
libgnc_gnomeutils.gnc_plugin_manager_add_plugin.restype = None

libgnc_gnomeutils.gnc_plugin_manager_remove_plugin.argtypes = [ GncPluginManagerOpaquePtr, GncPluginOpaquePtr ]
libgnc_gnomeutils.gnc_plugin_manager_remove_plugin.restype = None

libgnc_gnomeutils.gnc_plugin_manager_get_plugin.argtypes = [ GncPluginManagerOpaquePtr, ctypes.c_char_p ]
libgnc_gnomeutils.gnc_plugin_manager_get_plugin.restype = GncPluginOpaquePtr

libgnc_gnomeutils.gnc_plugin_manager_get_plugins.argtypes = [ GncPluginManagerOpaquePtr ]
libgnc_gnomeutils.gnc_plugin_manager_get_plugins.restype = GListOpaquePtr


class WrapPluginManager(object):

    # the only real issue with this class is must ensure called
    # after has been inited
    # actually maybe not - calling gnc_plugin_manager_get will create if not
    # already created
    # remember we are not messing with this object - just primarily need to be
    # be able to call add and remove

    def __init__ (self):
        self.Cgobject = PyGObjectCAPI()
        self.plugin_manager_ptr = self.gnc_plugin_manager_get()


    def gnc_plugin_manager_get (self):

        global Cgobject

        #pdb.set_trace()

        plugin_manager_ptr = libgnc_gnomeutils.gnc_plugin_manager_get()
        #gnucash_log.dbglog_err("plugin_manager_ptr %x"%plugin_manager_ptr.contents)
        print("plugin_manager_ptr %x"%ctypes.addressof(plugin_manager_ptr.contents), file=sys.stderr)

        # we dont need to mess with this - we just pass it around
        return plugin_manager_ptr


    def add_plugin (self, pluginobj):

        # note pluginobj must be subclass GncPlugin
        pluginobj_ptr = hash(pluginobj)
        print("plugin_name %s"%pluginobj.get_name(), file=sys.stderr)
        #if pluginobj.get_name() == None: pdb.set_trace()
        print("plugin_ptr %x"%pluginobj_ptr, file=sys.stderr)
        print("plugin_manager_ptr %x"%ctypes.addressof(self.plugin_manager_ptr.contents), file=sys.stderr)
        pluginobj_ptr = ctypes.cast(pluginobj_ptr,GncPluginOpaquePtr)
        libgnc_gnomeutils.gnc_plugin_manager_add_plugin(self.plugin_manager_ptr, pluginobj_ptr)

    def remove_plugin (self, pluginobj):

        # note pluginobj must be subclass GncPlugin
        pluginobj_ptr = hash(pluginobj)
        print("plugin_ptr %x"%pluginobj_ptr, file=sys.stderr)
        print("plugin_manager_ptr %x"%ctypes.addressof(self.plugin_manager_ptr.contents), file=sys.stderr)
        pluginobj_ptr = ctypes.cast(pluginobj_ptr,GncPluginOpaquePtr)
        libgnc_gnomeutils.gnc_plugin_manager_remove_plugin(self.plugin_manager_ptr, pluginobj_ptr)


    # not clear we need these!!
    # our main need is to be able to add/remove plugins

    def get_plugin (self, plugin_name):

        pluginobj = libgnc_gnomeutils.gnc_plugin_manager_get_plugin(self.plugin_manager_ptr, plugin_name)

        # we need to do something with this
        # we need to convert back to a python instance
        #pluginobj = self.Cgobject.to_object(pluginobj_ptr)

        return pluginobj

    def get_plugins (self):

        # this returns a GList
        pluginlist_ptr = libgnc_gnomeutils.gnc_plugin_manager_get_plugins(self.plugin_manager_ptr)

        #pdb.set_trace()

        #gnucash_log.dbglog(pluginlist_ptr)
        glst_ptr = ctypes.cast( pluginlist_ptr, ctypes.POINTER( glib_ctypes.GListRaw ) )
        #gnucash_log.dbglog(glst_ptr)

        glst_len = glib_ctypes.libglib.g_list_length(glst_ptr)
        #gnucash_log.dbglog(glst_ptr)
        #gnucash_log.dbglog(glst_len)

        plg_lst = []
        glst_ptr_base = glst_ptr
        for irng in range(glst_len):
            #gelm1 = glib_ctypes.libglib.g_list_nth_data(glst_ptr_base,irng)
            gelm = glst_ptr.contents.data
            glst_ptr = glib_ctypes.g_list_next(glst_ptr)
            plugin_ptr = gelm
            #gnucash_log.dbglog_err("plugin_ptr 0x%x"%plugin_ptr)
            pluginobj = self.Cgobject.to_object(plugin_ptr)
            plg_lst.append(pluginobj)

        return plg_lst


plugin_manager = WrapPluginManager()

