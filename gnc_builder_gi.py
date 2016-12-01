
# this is a recoding of the options dialog (defined in dialog-options.c)
# in python

# this is annoying - the 2nd argument to add_objects_from_file is a vector
# of strings - and passing a python list of strings does not work
# try using ctypes


import os

import sys


from gi.repository import Gtk


import ctypes

from ctypes.util import find_library


import pdb


libgtkx11nm = find_library("gtk-x11-2.0")

libgtkx11 = ctypes.CDLL(libgtkx11nm)

libgtkx11.gtk_builder_add_objects_from_file.argtypes = [ ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_void_p ]
libgtkx11.gtk_builder_add_objects_from_file.restype = ctypes.c_uint



class GncBuilder(Gtk.Builder):

    def __init__ (self):
        super(GncBuilder,self).__init__()

    def add_from_file (self, filename,  root):

        #pdb.set_trace()

        # find some global directory
        #gnc_builder_dir = gnc_path_get_gtkbuilderdir ()
        gnc_builder_dir = "/opt/local/share/gnucash/gtkbuilder"
        fname = os.path.join(gnc_builder_dir,filename)
        print "builder loading from %s root %s"%(fname,root)
        buildobjs = [ root ]
        #result = self.add_objects_from_file(fname, buildobjs)
        # sneaky - this creates a char** vector
        strngvector = (ctypes.c_char_p * (len(buildobjs)+1))()
        strngvector[:-1] = buildobjs
        strngvector[-1] = None
        # and this converts the vector of strings to a python string
        #strngs = ctypes.string_at(ctypes.addressof(strngvector))
        # yet this does not work - we get a crash
        #result = self.add_objects_from_file(fname, strngs)
        print "builder address %x"%hash(self)
        print "strngs address %x"%ctypes.addressof(strngvector)
        # this seems to work - it does not crash (as it does if use strngs directly)
        # (probably because we defined the 3rd arg as c_void_p rather than c_char_p
        result = libgtkx11.gtk_builder_add_objects_from_file(hash(self), fname, ctypes.addressof(strngvector), None)
        if result == 0:
            # dont see immediate way we get errors
            #PWARN(log_module,"Couldn't load builder file: %s"%"IO ERROR")
            print "Couldn't load builder file: "
            pass
        return result

