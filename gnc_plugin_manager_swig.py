

# new attempt at creating python classes for SWIG wrapped GObjects

import pdb

# for the moment do it manually - will also try to use metaclasses to add
# the private class data

# bummer - if we import sw_gnome_utils we get pre-defined python
# classes eg GncPluginManager and GncPluginManagerClass

# and it doesnt help to access the private class variables!!
# (these are only defined in the .c files and swig doesnt read the .c files!!)
# so I think this method is shot - we still need to use the introspection
# classes

import sw_gnome_utils


pdb.set_trace()


