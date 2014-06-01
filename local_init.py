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


#import gnc_plugin_python_example

# this way seems to be failing
import python_only_plugin 
myplugin = python_only_plugin.MyPlugin()

#import gnc_plugin_page
