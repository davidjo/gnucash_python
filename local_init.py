import sys
import os
import pdb
import traceback


#pdb.set_trace()

# see if calling this prevents the crashes
# no - this causes a total lockup after first menu click
# so this is really confusing - currently if we make callbacks
# for gnucash menus looks like we need to do a GIL state ensure
# before going into python - even though all the evidence I have
# is that this also being done by eg pyg_closure_marshal before going into python
# otherwise on second menu click we get a crash in the callback
# at Py_EnterRecursiveCall (which gets bad thread data for checking recursion limit)
#import gobject
#gobject.threads_init()
# and this locks up main loop as expected!!
#import gtk
#gtk.gdk.threads_init()


# hmm - we need to instantiate the python report page module here
# - other wise the callbacks wont exist when restoring pages saved on normal shutdown
# however this means we need a re-factor as can now only do widget stuff later
# looks like in gnucash modules are not effectively multiply instantiated
# essentially we need to define the GType now and figure out how to set the callback
# actually do we need the instantiation - maybe the import is enough??
# yes - looks like the import is enough
import gnc_plugin_page_python_report

#import gnc_plugin_python_example

import python_only_plugin 
myplugin = python_only_plugin.MyPlugin()

#pdb.set_trace()

print "junk"
