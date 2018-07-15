
# OK lets see if we can just use the GType directly
# we may be able to if register type before usage
# by calling the get_type function
# great - this does work!!

# well it does but still not figured out how to access
# the private data of the GType - in particular when
# it contains widgets we need access to


import sys

from gi.repository import GObject

import pdb


import gnome_utils_ctypes


from pygobjectcapi import PyGObjectCAPI

# call like this:
# Cgobject = PyGObjectCAPI()
# Cgobject.to_object(memory_address)

# to get memory address from a gobject:
#  address = hash(obj)

Cgobject = PyGObjectCAPI()

#pdb.set_trace()


gtyp = gnome_utils_ctypes.libgnc_gnomeutils.gnc_date_edit_get_type()

# so looks like this will allow gnc_date_edit_class_init to be called eventually
BadGncDateEdit = GObject.type_from_name('GNCDateEdit')

# this lists the properties
# this is where gnc_date_edit_class_init is called
# presumably will be called when need the the actual class instantiated
#print(GObject.list_properties(BadGncDateEdit), file=sys.stderr)

# this lists the signal names
#print(GObject.signal_list_names(BadGncDateEdit), file=sys.stderr)

#print(dir(BadGncDateEdit), file=sys.stderr)

# create a dummy instance in order to get correct type
# and this will call gnc_date_edit_init
# if gnc_date_edit_class_init has not been called it will be called
# before gnc_date_edit_init here
tmpdateedit = GObject.new(GObject.type_from_name('GNCDateEdit'))

BaseGncDateEdit = type(tmpdateedit)

#pdb.set_trace()

#class GncPluginExampleClass(type(tmpplugin)):
#    pass

#GObject.type_register(GncPluginExampleClass)

#tmpexampl = GObject.new(GncPluginExampleClass)



class GncDateEdit(BaseGncDateEdit):

    GNC_DATE_EDIT_SHOW_TIME             = 1 << 0
    GNC_DATE_EDIT_24_HR                 = 1 << 1
    GNC_DATE_EDIT_WEEK_STARTS_ON_MONDAY = 1 << 2

    GNC_RD_WID_AB_BUTTON_POS            = 0
    GNC_RD_WID_AB_WIDGET_POS            = 1
    GNC_RD_WID_REL_BUTTON_POS           = 2
    GNC_RD_WID_REL_WIDGET_POS           = 3

    def __init__ (self, the_time, flags):
        super(GncDateEdit,self).__init__()

    @classmethod
    def new (cls, the_time, show_time, use_24_format):
        pdb.set_trace()
        time_int = int(the_time)
        #gnc_flags = (GncDateEdit.GNC_DATE_EDIT_SHOW_TIME if show_time else 0) | \
        #                         (GncDateEdit.GNC_DATE_EDIT_24_HR if use_24_format else 0)
        newdateedit_ptr = gnome_utils_ctypes.libgnc_gnomeutils.gnc_date_edit_new(time_int,show_time,use_24_format)

        # call like this:
        newdateedit = Cgobject.to_object(newdateedit_ptr)

        return newdateedit



