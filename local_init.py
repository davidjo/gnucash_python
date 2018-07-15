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
    try:
        from gi.repository import GObject
        GObject.threads_init()
    except ImportError:
        import gobject
        gobject.threads_init()

    # see if can turn off g_log handlers installed by pygobject
    # note need to do this AFTER importing gobject
    # do we need to do this now?
    # maybe the threads_init above will fix this as well


    # check for introspection
    # if so add current path to girepository paths
    try:
        import gi
        gi.require_version('GIRepository', '2.0') 
        from gi.repository import GIRepository
    except ImportError:
        pass
    else:
        #pdb.set_trace()
        rep = GIRepository.Repository.get_default()
        addrep = os.path.join(sys.path[0],"girepository")
        rep.prepend_search_path(addrep)
        print("junk")
        # new feature - we apparently have no sys.argv
        # - fake up a null entry
        sys.argv = [ 'gnucash' ]


    #print("loading CAPI")
    #from pygobjectcapi import PyGObjectCAPI

    #Cgobject = PyGObjectCAPI()
    #Cgobject.disable_warning_redirections()

    #print("done CAPI")

    #print("system path")
    #print(sys.path)

    # so this is weird - if we leave the Gdk import till needed
    # we get import error on Gdk.Color
    # import here and it works
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    from gi.repository import Gtk
    from gi.repository import Gdk


    # need to load early as we extend some base gnucash classes
    #import gnucash_ext

    # probably need to add the following to the python module c
    # - otherwise sys.argv is not set at all
    # PySys_SetArgv(argc, argv);

    #pdb.set_trace()

    import gnc_plugin_manager

    import gnc_plugin

    myplugin = gnc_plugin.GncPluginPythonTest()

    # REMOVE COMMENT
    #gnc_plugin_manager.plugin_manager.add_plugin(myplugin)

    #pdb.set_trace()

    import gnc_plugin_python_example

    myplugin_example = gnc_plugin_python_example.GncPluginPythonExample()

    gnc_plugin_manager.plugin_manager.add_plugin(myplugin_example)


    plugins = gnc_plugin_manager.plugin_manager.get_plugins()

    #pdb.set_trace()

    for plugin in plugins:
        print("plugin loaded",plugin.get_name())


    import gnc_plugin_python_tools


    python_tools = gnc_plugin_python_tools.GncPluginPythonTools()

    gnc_plugin_manager.plugin_manager.add_plugin(python_tools)


    import gnc_plugin_page

    # hmm - we need to instantiate the python report page module here
    # - other wise the callbacks wont exist when restoring pages saved on normal shutdown
    # however this means we need a re-factor as can now only do widget stuff later
    # looks like in gnucash modules are not effectively multiply instantiated
    # essentially we need to define the GType now and figure out how to set the callback
    # actually do we need the instantiation - maybe the import is enough??
    # yes - looks like the import is enough
    import gnc_plugin_page_python_report

    # initial testing python plugin
    if False:
        import python_only_plugin 
        myplugin = python_only_plugin.MyPlugin()

    import gnc_plugin_python_reports


    python_reports = gnc_plugin_python_reports.GncPluginPythonReports()

    gnc_plugin_manager.plugin_manager.add_plugin(python_reports)


    #pdb.set_trace()
    print("local_init loaded")

except Exception as errexc:
    print("Failed to import in local_init!!", file=sys.stderr)
    traceback.print_exc()
    pdb.set_trace()

