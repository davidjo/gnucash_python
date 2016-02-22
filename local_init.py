import sys
import os
import pdb
import traceback

import gc

# wrap all this in try except so can silently fail in init.py
# if local_init.py does not exist

try:

    #pdb.set_trace()

    # uncomment to debug memory issues
    #gc.set_debug(gc.DEBUG_LEAK)

    # see if calling this prevents the crashes
    # well the previous comments are now incorrect - we do need to do this
    # and this solves the crash in the callback
    # at Py_EnterRecursiveCall (which gets bad thread data for checking recursion limit)
    # did I remove this when trying out importing webkit python module?
    # (now using gnucash functions that call webkit)
    import gobject
    gobject.threads_init()

    # see if can turn off g_log handlers installed by pygobject
    # note need to do this AFTER importing gobject
    # do we need to do this now?
    # maybe the threads_init above will fix this as well

    #print "loading CAPI"
    #from pygobjectcapi import PyGObjectCAPI

    #Cgobject = PyGObjectCAPI()
    #Cgobject.disable_warning_redirections()

    #print "done CAPI"

    #print "system path"
    #print sys.path


    # need to load early as we extend some base gnucash classes
    #import gnucash_ext


    import gnc_plugin_manager


    #import gnc_plugin_python_example

    #myplugin_example = gnc_plugin_python_example.GncPluginPythonExample()

    #gnc_plugin_manager.plugin_manager.add_plugin(myplugin_example)


    import gnc_plugin_python_tools

    python_tools = gnc_plugin_python_tools.GncPluginPythonTools()

    gnc_plugin_manager.plugin_manager.add_plugin(python_tools)


    # hmm - we need to instantiate the python report page module here
    # - other wise the callbacks wont exist when restoring pages saved on normal shutdown
    # however this means we need a re-factor as can now only do widget stuff later
    # looks like in gnucash modules are not effectively multiply instantiated
    # essentially we need to define the GType now and figure out how to set the callback
    # actually do we need the instantiation - maybe the import is enough??
    # yes - looks like the import is enough
    import gnc_plugin_page_python_report

    #import python_only_plugin 
    #myplugin = python_only_plugin.MyPlugin()

    import gnc_plugin_python_reports

    python_reports = gnc_plugin_python_reports.GncPluginPythonReports()

    gnc_plugin_manager.plugin_manager.add_plugin(python_reports)


    #pdb.set_trace()
    print "local_init loaded"

except Exception, errexc:
    print >> sys.stderr, "Failed to import in local_init!!"
    traceback.print_exc()
    pdb.set_trace()

