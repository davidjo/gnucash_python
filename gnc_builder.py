
# this is a recoding of the options dialog (defined in dialog-options.c)
# in python

import os

import sys

import gobject

import gtk



import _sw_app_utils


class GncBuilder(gtk.Builder):

    def __init__ (self):
        super(GncBuilder,self).__init__()

    def add_from_file (self, filename,  root):

        # find some global directory
        #gnc_builder_dir = gnc_path_get_gtkbuilderdir ()
        gnc_builder_dir = "/opt/local/share/gnucash/gtkbuilder"
        fname = os.path.join(gnc_builder_dir,filename)
        print "builder loading from %s root %s"%(fname,root)
        buildobjs = [ root ]
        result = self.add_objects_from_file(fname, buildobjs)
        if result == 0:
            # dont see immediate way we get errors
            #PWARN(log_module,"Couldn't load builder file: %s"%"IO ERROR")
            print "Couldn't load builder file: "
            pass
        return result

