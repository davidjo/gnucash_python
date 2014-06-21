
# OK lets see if we can just use the GType directly
# well that fails because the GType is not defined
# till an option window is actually opened


import gobject

import pdb



pdb.set_trace()


gncdateedit = gobject.type_from_name('GNCDateEdit')

# this lists the properties
print >> sys.stderr, gobject.list_properties(gncdateedit)

# this lists the signal names
print >> sys.stderr, gobject.signal_list_names(gncdateedit)

print >> sys.stderr, dir(gncdateedit)


tmpdateedit = gobject.new(gobject.type_from_name('GNCDateEdit'))

pdb.set_trace()

#class GncPluginExampleClass(type(tmpplugin)):
#    pass

#gobject.type_register(GncPluginExampleClass)

#tmpexampl = gobject.new(GncPluginExampleClass)


