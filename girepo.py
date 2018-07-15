
# functions to access class structure members using ctypes
# for gobject introspection

from __future__ import print_function

import sys

import os

import pdb

import gi

import gi.repository

from gi.repository import GObject

gi.require_version('GIRepository', '2.0')
from gi.repository import GIRepository


import ctypes

from ctypes.util import find_library

libgirepositorynm = find_library("libgirepository")

libgirepository = ctypes.CDLL(libgirepositorynm)


class GITypeTag(object):
    GI_TYPE_TAG_VOID      =  0
    GI_TYPE_TAG_BOOLEAN   =  1
    GI_TYPE_TAG_INT8      =  2
    GI_TYPE_TAG_UINT8     =  3
    GI_TYPE_TAG_INT16     =  4
    GI_TYPE_TAG_UINT16    =  5
    GI_TYPE_TAG_INT32     =  6
    GI_TYPE_TAG_UINT32    =  7
    GI_TYPE_TAG_INT64     =  8
    GI_TYPE_TAG_UINT64    =  9
    GI_TYPE_TAG_FLOAT     = 10
    GI_TYPE_TAG_DOUBLE    = 11
    GI_TYPE_TAG_GTYPE     = 12
    GI_TYPE_TAG_UTF8      = 13
    GI_TYPE_TAG_FILENAME  = 14
    # /* Non-basic types; compare with G_TYPE_TAG_IS_BASIC */
    GI_TYPE_TAG_ARRAY     = 15
    GI_TYPE_TAG_INTERFACE = 16
    GI_TYPE_TAG_GLIST     = 17
    GI_TYPE_TAG_GSLIST    = 18
    GI_TYPE_TAG_GHASH     = 19
    GI_TYPE_TAG_ERROR     = 20
    # /* Another basic type */
    GI_TYPE_TAG_UNICHAR   = 21
    # /* Note - there is currently only room for 32 tags */

    # special tag for potiner
    GI_TYPE_TAG_POINTER   = 31

class GIArrayType(object):
    GI_ARRAY_TYPE_C          = 0
    GI_ARRAY_TYPE_ARRAY      = 1
    GI_ARRAY_TYPE_PTR_ARRAY  = 2
    GI_ARRAY_TYPE_BYTE_ARRAY = 3

class GIInfoType(object):
    GI_INFO_TYPE_INVALID     =  0
    GI_INFO_TYPE_FUNCTION    =  1
    GI_INFO_TYPE_CALLBACK    =  2
    GI_INFO_TYPE_STRUCT      =  3
    GI_INFO_TYPE_BOXED       =  4
    GI_INFO_TYPE_ENUM        =  5    # /*  5 */
    GI_INFO_TYPE_FLAGS       =  6
    GI_INFO_TYPE_OBJECT      =  7
    GI_INFO_TYPE_INTERFACE   =  8
    GI_INFO_TYPE_CONSTANT    =  9
    GI_INFO_TYPE_INVALID_0   = 10    # /* 10 */
    GI_INFO_TYPE_UNION       = 11
    GI_INFO_TYPE_VALUE       = 12
    GI_INFO_TYPE_SIGNAL      = 13
    GI_INFO_TYPE_VFUNC       = 14
    GI_INFO_TYPE_PROPERTY    = 15    # /* 15 */
    GI_INFO_TYPE_FIELD       = 16
    GI_INFO_TYPE_ARG         = 17
    GI_INFO_TYPE_TYPE        = 18
    GI_INFO_TYPE_UNRESOLVED  = 19


class GIFieldInfoOpaque(ctypes.Structure):
    pass

libgirepository.g_field_info_get_offset.argtypes = [ ctypes.c_void_p ]
#libgirepository.g_field_info_get_offset.argtypes = [ ctypes.POINTER(GIFieldInfoOpaque) ]
libgirepository.g_field_info_get_offset.restype = ctypes.c_int

libgirepository.g_field_info_get_type.argtypes = [ ctypes.c_void_p ]
#libgirepository.g_field_info_get_type.argtypes = [ ctypes.POINTER(GIFieldInfoOpaque) ]
libgirepository.g_field_info_get_type.restype = ctypes.c_void_p


class GITypeInfoOpaque(ctypes.Structure):
    pass

libgirepository.g_type_info_get_tag.argtypes = [ ctypes.c_void_p ]
#libgirepository.g_type_info_get_tag.argtypes = [ ctypes.POINTER(GITypeInfoOpaque) ]
libgirepository.g_type_info_get_tag.restype = ctypes.c_uint

libgirepository.g_type_info_get_array_type.argtypes = [ ctypes.c_void_p ]
#libgirepository.g_type_info_get_array_type.argtypes = [ ctypes.POINTER(GITypeInfoOpaque) ]
libgirepository.g_type_info_get_array_type.restype = ctypes.c_uint

libgirepository.g_type_info_is_pointer.argtypes = [ ctypes.c_void_p ]
#libgirepository.g_type_info_is_pointer.argtypes = [ ctypes.POINTER(GITypeInfoOpaque) ]
libgirepository.g_type_info_is_pointer.restype = ctypes.c_uint

class GIBaseInfoOpaque(ctypes.Structure):
    pass

libgirepository.g_type_info_get_interface.argtypes = [ ctypes.c_void_p ]
#libgirepository.g_type_info_get_interface.argtypes = [ ctypes.POINTER(GITypeInfoOpaque) ]
libgirepository.g_type_info_get_interface.restype = ctypes.c_void_p
#libgirepository.g_type_info_get_interface.restype = ctypes.POINTER(GIBaseInfoOpaque)

libgirepository.g_base_info_get_type.argtypes = [ ctypes.c_void_p ]
#libgirepository.g_base_info_get_type.argtypes = [ ctypes.POINTER(GIBaseInfoOpaque) ]
libgirepository.g_base_info_get_type.restype = ctypes.c_uint

class GIStructInfoOpaque(ctypes.Structure):
    pass

#libgirepository.g_struct_info_set_size.argtypes = [ ctypes.c_void_p ]
##libgirepository.g_struct_info_set_size.argtypes = [ ctypes.POINTER(GIStructInfoOpaque) ]
#libgirepository.g_struct_info_set_size.restype = ctypes.c_uint

class GIUnionInfoOpaque(ctypes.Structure):
    pass

#libgirepository.g_union_info_set_size.argtypes = [ ctypes.c_void_p ]
##libgirepository.g_union_info_set_size.argtypes = [ ctypes.POINTER(GIUnionInfoOpaque) ]
#libgirepository.g_union_info_set_size.restype = ctypes.c_uint


def get_field_info (field_info):

    fieldinfo_ptr = id(field_info)
    #print("fieldinfo 0x%x"%fieldinfo_ptr)

    pygibaseinfo_ptr = ctypes.cast( fieldinfo_ptr, ctypes.POINTER(PyGIBaseInfo) )
    #print("baseinfo ptr 0x%x"%pygibaseinfo_ptr)

    #print("baseinfo ptr 0x%x"%ctypes.addressof(pygibaseinfo_ptr.contents))

    #print("type %x"%pygibaseinfo_ptr.contents.ob_type)

    #print("info %x"%pygibaseinfo_ptr.contents.info)

    return pygibaseinfo_ptr.contents.info

def get_field_type_tag (field_info_obj):

    type_info_ptr = libgirepository.g_field_info_get_type(field_info_obj)

    #print("type ptr %x"%type_info_ptr)

    chkptr = libgirepository.g_type_info_is_pointer(type_info_ptr)

    #pdb.set_trace()

    # what to do about pointer type??
    # make a special type - hopefully not found in C!!
    # WE DO NOT HANDLE THIS RIGHT YET!!
    #if chkptr:

    #    field_type_tag =  GITypeTag.GI_TYPE_TAG_POINTER

    #else:
    if True:

        field_type_tag = libgirepository.g_type_info_get_tag(type_info_ptr)

        #print("type tag %d"%field_type_tag)

        if field_type_tag == GITypeTag.GI_TYPE_TAG_INTERFACE:

            field_interface_ptr = libgirepository.g_type_info_get_interface(type_info_ptr)

            info_type = libgirepository.g_base_info_get_type(field_interface_ptr)

            print("info type %d"%info_type)

            field_type_tag = GITypeTag.GI_TYPE_TAG_INTERFACE*1000 + info_type


    return field_type_tag



# these are internal definitions - only use if really need to!!

class GIRealInfo(ctypes.Structure):
    _fields_ = [ ("type", ctypes.c_int),
                 ("ref_count", ctypes.c_int),
                 ("repository", ctypes.c_void_p),
                 ("container", ctypes.c_void_p),
                 ("typelib", ctypes.c_void_p),
                 ("offset", ctypes.c_uint),
                 ("type_is_embedded", ctypes.c_uint),
                 ("reserved2", ctypes.c_void_p*4),
               ]

class GIUnresolvedInfo(ctypes.Structure):
    _fields_ = [ ("type", ctypes.c_int),
                 ("ref_count", ctypes.c_int),
                 ("repository", ctypes.c_void_p),
                 ("container", ctypes.c_void_p),
                 ("name", ctypes.c_char_p),
                 ("namespace", ctypes.c_char_p),
               ]



# unfortunately I cant see any way to get round defining a structure
# type to get the info pointer
class PyGIBaseInfo(ctypes.Structure):
    _fields_ = [ ("ob_refcnt", ctypes.c_void_p),
                 ("ob_type", ctypes.c_void_p),
                 ("info", ctypes.c_void_p),
               ]


# well its problematic to store/access string pointers
# this should get us access to the string address which we can stuff in

ctypes.pythonapi.PyUnicode_AsUTF8.argtypes = (ctypes.py_object,)
ctypes.pythonapi.PyUnicode_AsUTF8.restype = ctypes.c_void_p
ctypes.pythonapi.PyUnicode_FromString.argtypes = (ctypes.c_void_p,)
ctypes.pythonapi.PyUnicode_FromString.restype = ctypes.py_object



# now getting some understanding of metaclasses
# - they may be useful here
# define a metaclass object which is used to modify creation of class objects
class GirMeta(gi.types.GObjectMeta):
    def __new__ (mcls, classname, bases, attrs):
        # code to operate on the arguments
        if not '__girmetaclass__' in attrs:
            raise AttributeError("__girmetaclass__ attribute MUST be defined")
        # it appears we cannot use other functions defined in the Meta class
        # - claims need an instance as first argument - mcls is not an instance
        # (we could of course define functions inside functions I suppose)
        #flds = attrs['__girmetaclass__'].__dict__['__info__'].get_fields()
        pdb.set_trace()
        # now generate class
        # do we need to use the parent meta class new here?? or always type??
        # or should we be using init??
        #return type.__new__(mcls, classname, bases, attrs)
        return gi.types.GObjectMeta.__new__(mcls, classname, bases, attrs)

# I think we need an explicit Meta class for the Plugin
# - we need to fixup the plugin_name - and be careful not to override
# virtual functions - how to detect??
# OK so understand difference between __new__ and __init__
# __new__  - at this point the class has not yet been created - the argument
#            is the metaclass
# __init__ - by this point the class has been created so the first argument
#            is the new class - ALMOST!!
#            NOTA BENE - the new class not fully created till AFTER the
#            class super __init__ call!!!
#            this is VERY important when subclassing Gir wrapped GTypes!!

# this is getting more confusing - it looks as though we cannot change
# the attributes at the init stage
# so we need to fixup the attributes in the __new__ phase
# but we cannot set the class pointer till the init phase!!
# because we interpose a Python wrapping class we need 2 metaclass objects
# GncPluginMeta is used in the GncPluginPython definition to define
# access to the C private data - we only define the __new__ function

# so Im still confused about subclassing a class with a __metaclass__
# - the subclass still seems to call the parent __metaclass__ __new__ if the subclass
# has no __metaclass__
# I thought we define the python class variables we need in the parent class
# - but if we have done that we dont need to redo this in the subclass (the parent
# class is now defined with the updated class variables)
# problem is if we forget to add the __metaclass__ in the subclass the parent
# __metaclass__ is called - how to detect this??
# also means in the subclass __metaclass__ we dont call the parent __new__
# - again would just redo whats been done
# should we just ignore the parent metaclass and only update the parent class
# variables when define the subclass - this just does not seem right??

# so it appears that making a python subclass of a python subclass of the GncPlugin GObject
# we will always have to subclass the GncPlugin GObject directly
# - for common code we make the current python subclass a mixin class

class GncPluginMeta(gi.types.GObjectMeta):
    def __new__ (mcls, classname, bases, attrs):
        # code to operate on the arguments
        print("GncPluginMeta new called:",str(mcls),classname,str(bases),str(attrs))
        #pdb.set_trace()
        if not '__girmetaclass__' in attrs:
            pdb.set_trace()
            # NOTA BENE - the correct order for multiple classes is base class last
            if len(bases) > 1:
                raise AttributeError("__metaclass__ multiple bases not implemented")
            if isinstance(bases[-1], GncPluginMeta):
                raise AttributeError("__metaclass__ class attribute MUST be defined")
            raise AttributeError("__girmetaclass__ class attribute MUST be defined")
        # it appears we cannot use other functions defined in the Meta class
        # - claims need an instance as first argument - mcls is not an instance
        # (we could of course define functions inside functions I suppose)
        # Im going to skip virtual functions(callback type - any others??)
        flds = attrs['__girmetaclass__'].__dict__['__info__'].get_fields()
        newattr = {}
        for fldobj in flds:
           if fldobj.get_name() in attrs:
               clsfldobj = GObjectField(fldobj, initial_value=attrs[fldobj.get_name()])
               if hasattr(clsfldobj,'get_value'):
                   newattr[fldobj.get_name()] = clsfldobj
           else:
               clsfldobj = GObjectField(fldobj)
               if hasattr(clsfldobj,'get_value'):
                   newattr[fldobj.get_name()] = clsfldobj
        if not 'plugin_name' in attrs:
            raise AttributeError("plugin_name class attribute MUST be defined")
        #pdb.set_trace()
        attrs['ClassVariables'] = GObjectClass(newattr.items())
        attrs['plugin_name'] = newattr['plugin_name']
        # now generate class
        # do we need to use the parent meta class new here?? or always type??
        # or should we be using init??
        #return type.__new__(mcls, classname, bases, attrs)
        return super(GncPluginMeta, mcls).__new__(mcls,classname, bases, attrs)
        #return gi.types.GObjectMeta.__new__(mcls, classname, bases, attrs)

    def __init__ (cls, name, bases, attrs):
        print("GncPluginMeta init called:",str(cls),name,str(bases),str(attrs))
        # NOTA BENE - for GType subclassing the class structure address returned at this point
        # is STILL the parent GType class structure!!
        # we need the cls variable AFTER the super call!!
        # so this is how to get the address of the class structure!!
        print("python meta gtype klass %s address %x"%(str(cls),hash(GObject.type_class_peek(cls))))
        super(GncPluginMeta, cls).__init__(name, bases, attrs)
        print("python meta gtype klass %s address %x"%(str(cls),hash(GObject.type_class_peek(cls))))
        #pdb.set_trace()
        # we delay this till subclass for subclass of subclass
        ## we have deleted plugin_name from attrs above!!
        #cls.plugin_name.set_klass_pointer(cls)
        #plugin_name = cls.plugin_name.field_value
        #print("python gtype plugin_name",plugin_name)
        #cls.plugin_name.set_value(plugin_name)


# and GncPluginSubClassMeta is used in a subclass of GncPluginPython to actually set the
# variables - we need __new__ here as we need to substitute the initial definition

class GncPluginSubClassMeta(GncPluginMeta):
    def __new__ (mcls, classname, bases, attrs):
        print("GncPluginSubClassMeta new called:",str(mcls),classname,str(bases),str(attrs))
        #pdb.set_trace()
        if len(bases) > 1:
            raise AttributeError("__metaclass__ multiple bases not implemented")
        if not 'plugin_name' in attrs:
            raise AttributeError("plugin_name not defined for subclass - must be defined")
        # this assumes no multiple bases - base[-1] seems to be immediate superclass
        bases[-1].plugin_name.set_field_value(attrs['plugin_name'])
        # we need to delete this from attrs otherwise the new plain string definition
        # overrides the superclass (GncPluginPython) definition
        del attrs['plugin_name']
        # well doing GncPluginMeta.__new__ does call the supermetaclass __new__
        # - but this has already been done - whats the right way??
        # just use type call??
        #return GncPluginMeta.__new__(mcls, classname, bases, attrs)
        #return type.__new__(mcls, classname, bases, attrs)
        return gi.types.GObjectMeta.__new__(mcls, classname, bases, attrs)

    def __init__ (cls, name, bases, attrs):
        print("GncPluginSubClassMeta init called:",str(cls),name,str(bases),str(attrs))
        # NOTA BENE - for GType subclassing the class structure address returned at this point
        # is STILL the parent GType class structure!!
        # we need the cls variable AFTER the super call!!
        # so this is how to get the address of the class structure!!
        print("python sub gtype klass %s address %x"%(str(cls),hash(GObject.type_class_peek(cls))))
        super(GncPluginSubClassMeta, cls).__init__(name, bases, attrs)
        print("python sub gtype klass %s address %x"%(str(cls),hash(GObject.type_class_peek(cls))))
        #pdb.set_trace()
        # we have deleted plugin_name from attrs above!!
        cls.plugin_name.set_klass_pointer(cls)
        plugin_name = cls.plugin_name.field_value
        cls.plugin_name.set_value(plugin_name)


class GncPluginTryMeta(gi.types.GObjectMeta):
    def __new__ (mcls, classname, bases, attrs):
        # code to operate on the arguments
        print("GncPluginTryMeta new called:",str(mcls),classname,str(bases),str(attrs))
        return super(GncPluginTryMeta, mcls).__new__(mcls,classname, bases, attrs)
        #return gi.types.GObjectMeta.__new__(mcls, classname, bases, attrs)

    def __init__ (cls, name, bases, attrs):
        print("GncPluginTryMeta init called:",str(cls),name,str(bases),str(attrs))
        print("python meta gtype klass %s address %x"%(str(cls),hash(GObject.type_class_peek(cls))))
        super(GncPluginTryMeta, cls).__init__(name, bases, attrs)
        print("python meta gtype klass %s address %x"%(str(cls),hash(GObject.type_class_peek(cls))))

# this is for the GncPluginPage class - essentially a duplicate of GncPluginMeta

class GncPluginPageMeta(gi.types.GObjectMeta):
    def __new__ (mcls, classname, bases, attrs):
        # code to operate on the arguments
        print("GncPluginPageMeta new called:",str(mcls),classname,str(bases),str(attrs))
        #pdb.set_trace()
        if not '__girmetaclass__' in attrs:
            #pdb.set_trace()
            # NOTA BENE - the correct order for multiple classes is base class last
            if len(bases) > 1:
                raise AttributeError("__metaclass__ multiple bases not implemented")
            if isinstance(bases[-1], GncPluginPageMeta):
                raise AttributeError("__metaclass__ class attribute MUST be defined")
            raise AttributeError("__girmetaclass__ class attribute MUST be defined")
        # it appears we cannot use other functions defined in the Meta class
        # - claims need an instance as first argument - mcls is not an instance
        # (we could of course define functions inside functions I suppose)
        # Im going to skip virtual functions(callback type - any others??)
        flds = attrs['__girmetaclass__'].__dict__['__info__'].get_fields()
        newattr = {}
        for fldobj in flds:
           if fldobj.get_name() in attrs:
               clsfldobj = GObjectField(fldobj, initial_value=attrs[fldobj.get_name()])
               if hasattr(clsfldobj,'get_value'):
                   newattr[fldobj.get_name()] = clsfldobj
           else:
               clsfldobj = GObjectField(fldobj)
               if hasattr(clsfldobj,'get_value'):
                   newattr[fldobj.get_name()] = clsfldobj
        if not 'plugin_name' in attrs:
            raise AttributeError("plugin_name class attribute MUST be defined")
        if not 'tab_icon' in attrs:
            raise AttributeError("tab_icon class attribute MUST be defined")
        #pdb.set_trace()
        attrs['ClassVariables'] = GObjectClass(newattr.items())
        attrs['plugin_name'] = newattr['plugin_name']
        attrs['tab_icon'] = newattr['tab_icon']
        # now generate class
        # do we need to use the parent meta class new here?? or always type??
        # or should we be using init??
        #return type.__new__(mcls, classname, bases, attrs)
        return super(GncPluginPageMeta, mcls).__new__(mcls,classname, bases, attrs)
        #return gi.types.GObjectMeta.__new__(mcls, classname, bases, attrs)

    def __init__ (cls, name, bases, attrs):
        print("GncPluginPageMeta init called:",str(cls),name,str(bases),str(attrs))
        # NOTA BENE - for GType subclassing the class structure address returned at this point
        # is STILL the parent GType class structure!!
        # we need the cls variable AFTER the super call!!
        # so this is how to get the address of the class structure!!
        print("python meta gtype klass %s address %x"%(str(cls),hash(GObject.type_class_peek(cls))))
        super(GncPluginPageMeta, cls).__init__(name, bases, attrs)
        print("python meta gtype klass %s address %x"%(str(cls),hash(GObject.type_class_peek(cls))))
        #pdb.set_trace()
        # we delay this till subclass for subclass of subclass
        ## we have deleted plugin_name from attrs above!!
        #cls.plugin_name.set_klass_pointer(cls)
        #plugin_name = cls.plugin_name.field_value
        #print("python gtype plugin_name",plugin_name)
        #cls.plugin_name.set_value(plugin_name)
        #cls.tab_icon.set_klass_pointer(cls)
        #tab_icon = cls.tab_icon.field_value
        #print("python gtype tab_icon",tab_icon)
        #cls.tab_icon.set_value(tab_icon)


# and GncPluginPageSubClassMeta is used in a subclass of GncPluginPagePython to actually set the
# variables - we need __new__ here as we need to substitute the initial definition

class GncPluginPageSubClassMeta(GncPluginPageMeta):
    def __new__ (mcls, classname, bases, attrs):
        print("GncPluginPageSubClassMeta new called:",str(mcls),classname,str(bases),str(attrs))
        #pdb.set_trace()
        if len(bases) > 1:
            raise AttributeError("__metaclass__ multiple bases not implemented")
        if not 'plugin_name' in attrs:
            raise AttributeError("plugin_name not defined for subclass - must be defined")
        # this assumes no multiple bases - base[-1] seems to be immediate superclass
        bases[-1].plugin_name.set_field_value(attrs['plugin_name'])
        bases[-1].tab_icon.set_field_value(attrs['tab_icon'])
        # we need to delete this from attrs otherwise the new plain string definition
        # overrides the superclass (GncPluginPagePython) definition
        del attrs['plugin_name']
        del attrs['tab_icon']
        # well doing GncPluginPageSubClassMeta.__new__ does call the supermetaclass __new__
        # - but this has already been done - whats the right way??
        # just use type call??
        #return GncPluginPageSubClassMeta.__new__(mcls, classname, bases, attrs)
        #return type.__new__(mcls, classname, bases, attrs)
        return gi.types.GObjectMeta.__new__(mcls, classname, bases, attrs)

    def __init__ (cls, name, bases, attrs):
        print("GncPluginPageSubClassMeta init called:",str(cls),name,str(bases),str(attrs))
        # NOTA BENE - for GType subclassing the class structure address returned at this point
        # is STILL the parent GType class structure!!
        # we need the cls variable AFTER the super call!!
        # so this is how to get the address of the class structure!!
        print("python sub gtype klass %s address %x"%(str(cls),hash(GObject.type_class_peek(cls))))
        super(GncPluginPageSubClassMeta, cls).__init__(name, bases, attrs)
        print("python sub gtype klass %s address %x"%(str(cls),hash(GObject.type_class_peek(cls))))
        #pdb.set_trace()
        # we have deleted plugin_name from attrs above!!
        cls.plugin_name.set_klass_pointer(cls)
        plugin_name = cls.plugin_name.field_value
        cls.plugin_name.set_value(plugin_name)
        cls.tab_icon.set_klass_pointer(cls)
        tab_icon = cls.tab_icon.field_value
        cls.tab_icon.set_value(tab_icon)



# class definition for python 2.7 using the meta class
#class NewGObject(object):
#    __metaclass__ = GirMeta
#    __girmetaclass__ = NewGObject.GObjectClass
# etc

# class definition for python 3 using the meta class
#class NewGObject(object, metaclass=GirMeta):
#    __girmetaclass__ = NewGObject.GObjectClass
# etc


# create a container object for storing GType class variables
# should I use a namedtuple
# for namedtuple we need to know variable names at definition time

#namedtuple('GObjectClass')

class GObjectClass(object):
    def __init__ (self, key_values):
        for key,val in key_values:
            setattr(self, key, val)


# this class handles a GType field variables

class GObjectField(object):

    # this object is instantiated for each field name

    def __init__ (self, fldobj, offset_adjust_hack=0, check_adjust_hack=0, initial_value=None):

        self.field_name = fldobj.get_name()
        self.field_info = fldobj

        #pdb.set_trace()

        field_info_obj = get_field_info(self.field_info)

        self.offset = libgirepository.g_field_info_get_offset(field_info_obj)

        print("offset %d"%self.offset)

        #pdb.set_trace()

        self.field_type_tag = get_field_type_tag(field_info_obj)

        print("type tag %d"%self.field_type_tag)

        #pdb.set_trace()

        # DANGEROUS - only one of instance_ptr or klass_ptr should be set!!
        self.instance_ptr = None
        self.klass_ptr = None
        self.value_pointer = None

        ## do we assign these as defaults??
        #self.get_value = None
        #self.set_value = None

        # DANGER WILL ROBINSON!!
        # this is extreme hackery - because of issues of introspection and
        # bit field sizes which lead to wrong field offsets this allows
        # the offset to be adjusted when computing field pointer values
        # the check_adjust_hack is used to try and detect if the offset is
        # needed - its values is checked against the original offset
        self.offset_adjust_hack = offset_adjust_hack
        self.check_adjust_hack = check_adjust_hack


        # now we need to create the get_value/set_value functions

        if self.field_type_tag == GITypeTag.GI_TYPE_TAG_UTF8:

            self.get_value = self.get_utf8_value
            self.set_value = self.set_utf8_value

        elif self.field_type_tag == GITypeTag.GI_TYPE_TAG_UINT32:

            self.get_value = self.get_uint32_value
            self.set_value = self.set_uint32_value

        elif self.field_type_tag == GITypeTag.GI_TYPE_TAG_VOID:

            # so far this seen for a virtual function call recreate_page which
            # creates a new GncPluginPage in gnc_plugin_page.h
            # ignore for the moment??
            pass

        elif self.field_type_tag == GITypeTag.GI_TYPE_TAG_ARRAY:

            type_info_ptr = libgirepository.g_field_info_get_type(field_info_obj)

            print("type ptr %x"%type_info_ptr)

            array_type = libgirepository.g_type_info_get_array_type(type_info_ptr)

            # what to do for this??
            self.get_value = self.get_object_value
            self.set_value = self.set_object_value

        elif self.field_type_tag >= GITypeTag.GI_TYPE_TAG_INTERFACE*1000:

            if self.field_type_tag == GITypeTag.GI_TYPE_TAG_INTERFACE*1000+GIInfoType.GI_INFO_TYPE_STRUCT:

                # this appears to be used for basic GObjects

                self.get_value = self.get_object_value
                self.set_value = self.set_object_value

            elif self.field_type_tag == GITypeTag.GI_TYPE_TAG_INTERFACE*1000+GIInfoType.GI_INFO_TYPE_OBJECT:

                # this appears to be used for basic GObjects

                self.get_value = self.get_object_value
                self.set_value = self.set_object_value

            elif self.field_type_tag == GITypeTag.GI_TYPE_TAG_INTERFACE*1000+GIInfoType.GI_INFO_TYPE_CALLBACK:

                # for the moment Im skipping callbacks/virtual functions as those should be
                # correctly available as virtual functions
                # by not defining the get_value/set_value attribute use this to check to exclude
                # from class variables
                pass

            else:

                pdb.set_trace()

                raise RuntimeError("Unimplemented info type tag %d for %s"%(self.field_type_tag,self.field_name))

        else:

            pdb.set_trace()

            raise RuntimeError("Unimplemented type tag %d for %s"%(self.field_type_tag,self.field_name))

        print("added class variable",self.field_name,self.field_type_tag)

        # we cannot set the value yet as class not implemented
        # - just save it
        if initial_value != None:
           self.field_value = initial_value

        #pdb.set_trace()


    def __get__ (self, obj, objtype=None):
        #pdb.set_trace()
        if obj == None:
            return self
        if self.get_value == None:
            raise AttributeError("unreadable GObject class attribute %s"%self.field_name)
        return self.get_value()

    def __set__ (self, obj, value):
        #pdb.set_trace()
        if self.set_value == None:
            raise AttributeError("can't set GObject class attribute %s"%self.field_name)
        return self.set_value(value)

    def __delete__ (self, obj):
        # we cant delete these attributes!!
        raise AttributeError("can't delete GObject class attribute %s"%self.field_name)


    def set_instance_pointer (self, ginstance):
        self.instance_pointer = hash(ginstance)
        print("python ginstance %s address %x"%(str(ginstance),hash(ginstance)))

        if self.offset_adjust_hack != 0:
            if self.offset != self.check_adjust_hack:
                pdb.set_trace()
                raise ValueError("Field offset is wrong - possible bad version of GType %s - may need to regenerate gir files"%self.field_name)

        self.value_pointer = self.instance_pointer + self.offset_adjust_hack + self.offset
        print("python value address %x"%self.value_pointer)


    def set_klass_pointer (self, gtype):
        # so this is how to get the address of the class structure!!
        self.klass_ptr = hash(GObject.type_class_peek(gtype))
        print("python gtype klass %s address %x"%(str(gtype),hash(GObject.type_class_peek(gtype))))

        if self.offset_adjust_hack != 0:
            if self.offset != self.check_adjust_hack:
                raise ValueError("Field offset is wrong - possible bad version of GType %s - may need to regenerate gir files"%self.field_name)

        self.value_pointer = self.klass_ptr + self.offset_adjust_hack + self.offset
        print("python value address %x"%self.value_pointer)


    def set_field_value (self, new_value):
        # a direct set
        self.field_value = new_value


    def get_utf8_value (self):

        print("called get_utf8_value")

        print("python value address %x"%self.value_pointer)

        #pdb.set_trace()
        # need to check if returning addresses or python values!!!

        strval = ctypes.cast(self.value_pointer, ctypes.POINTER(ctypes.c_char_p)).contents.value

        utf8val = ctypes.pythonapi.PyUnicode_FromString(strval)

        return utf8val


    def set_utf8_value (self, new_value):

        # for the moment this is limited to string type

        print("called set_utf8_value")

        #pdb.set_trace()

        print("python value address %x"%self.value_pointer)

        # save string to ensure not GCed
        self.field_value = new_value

        #pdb.set_trace()

        if new_value == None:

            new_value_str_ptr = 0

        else:

            # typeerror I think is correct exception to raise here
            if not isinstance(new_value,str):
                raise TypeError("argument value is not a string type - must be a string type")

            # this was sneakily using the address of the string object as the C pointer
            # we need to correct this to use the python object directly
            #new_value_str_ptr = ctypes.pythonapi.PyUnicode_AsUTF8(id(new_value))
            new_value_str_ptr = ctypes.pythonapi.PyUnicode_AsUTF8(new_value)

            print("python str address %x"%new_value_str_ptr)

        # finally - this is how we do pointer assignment given plain addresses
        # we must cast to a pointer type - its confusing because the pointed to type is also a generic
        # pointer!!
        ctypes.cast(self.value_pointer, ctypes.POINTER(ctypes.c_void_p)).contents.value = new_value_str_ptr

        return


    def get_object_value (self):

        print("called get_object_value")

        print("python value address %x"%self.value_pointer)

        #pdb.set_trace()

        objval = ctypes.cast(self.value_pointer, ctypes.POINTER(ctypes.c_void_p)).contents.value

        return objval

    def set_object_value (self, new_value):

        print("called set_object_value")

        print("python value address %x"%self.value_pointer)

        ## typeerror I think is correct exception to raise here
        #if not isinstance(new_value,str):
        #    raise TypeError("argument value is not a string type - must be a string type")

        # what is the address to use - 
        pdb.set_trace()
        #if isinstance(new_value, ctypes.c_void_p):
        #    new_value_ptr = ctypes.c_void_p
        new_value_ptr = new_value

        # finally - this is how we do pointer assignment given plain addresses
        # we must cast to a pointer type - its confusing because the pointed to type is also a generic
        # pointer!!
        ctypes.cast(self.value_pointer, ctypes.POINTER(ctypes.c_void_p)).contents.value = new_value_ptr

        return

    def get_uint32_value (self):

        print("called get_uint32_value")

        print("python value address %x"%self.value_pointer)

        pdb.set_trace()

        uintval = ctypes.cast(self.value_pointer, ctypes.POINTER(ctypes.c_uint)).contents.value

        return uintval

    def set_uint32_value (self, new_value):

        print("called set_object_value")

        print("python value address %x"%self.value_pointer)

        ## typeerror I think is correct exception to raise here
        ## test for positive or hex map??
        #if not isinstance(new_value,int) or new_value < 0:
        #    raise TypeError("argument value is not a valid positive integer")

        # finally - this is how we do pointer assignment given plain addresses
        # we must cast to a pointer type 
        ctypes.cast(self.value_pointer, ctypes.POINTER(ctypes.c_uint)).contents.value = new_value

        return

    # hmm - looks like we need both the GType (or a GObject instantiation) and its class structure
    # definition from the gir file
    # yes - hash on the klass object is not the same as the
    # hash on the type_class_peek of the gobject 

    @classmethod
    def SetupClass (cls, gtype, klass, field_name, offset_adjust_hack=0, check_adjust_hack=0):

        #Try.PluginClass.__dict__['__info__'].get_fields()[2]

        flds = klass.__dict__['__info__'].get_fields()

        fndfld = None
        for fldobj in flds:
            if fldobj.get_name() == field_name:
                fndfld = fldobj
                break

        if fndfld == None:
            raise RuntimeError("Class %s does not contain the field name %s"%(str(klass),field_name))

        newobj = cls(fldobj, offset_adjust_hack=offset_adjust_hack, check_adjust_hack=check_adjust_hack)

        newobj.set_klass_pointer(gtype)

        return newobj

    @classmethod
    def Setup (cls, ginstance, field_name, offset_adjust_hack=0, check_adjust_hack=0):

        #pdb.set_trace()

        flds = ginstance.__class__.__info__.get_fields()

        fndfld = None
        for fldobj in flds:
            if fldobj.get_name() == field_name:
                fndfld = fldobj
                break

        if fndfld == None:
            raise RuntimeError("Class %s does not contain the field name %s"%(str(klass),field_name))

        newobj = cls(fldobj, offset_adjust_hack=offset_adjust_hack, check_adjust_hack=check_adjust_hack)

        newobj.set_instance_pointer(ginstance)

        return newobj


def BaseInfoCast (intype):

    # see if we can make a type caster
    # apparently we can - this works!!
    # - but we also need an inverse version
    # - in which we take a BaseInfo object and re-cast to
    # one of the others - for functions which return BaseInfo
    # objects

    pdb.set_trace()

    intype_ptr = id(intype)
    print("intype 0x%x"%intype_ptr)

    pyinfo_ptr = ctypes.cast( intype_ptr, ctypes.POINTER(PyGIBaseInfo) )
    #print("baseinfo ptr 0x%x"%pyinfo_ptr)

    print("baseinfo ptr 0x%x"%ctypes.addressof(pyinfo_ptr.contents))

    print("type %x"%pyinfo_ptr.contents.ob_type)

    print("info %x"%pyinfo_ptr.contents.info)

    newbaseinfo = gi.repository.GIRepository.BaseInfo()

    base_ptr = id(newbaseinfo)
    print("intype 0x%x"%base_ptr)

    newpygibaseinfo_ptr = ctypes.cast( base_ptr, ctypes.POINTER(PyGIBaseInfo) )
    #print("newbaseinfo ptr 0x%x"%newpygibaseinfo_ptr)

    print("newbaseinfo ptr 0x%x"%ctypes.addressof(newpygibaseinfo_ptr.contents))

    print("newtype %x"%newpygibaseinfo_ptr.contents.ob_type)

    print("newinfo %x"%newpygibaseinfo_ptr.contents.info)

    newpygibaseinfo_ptr.contents.info = pyinfo_ptr.contents.info

    return newbaseinfo


def access_class_data (gtype):

    # so this is how to get the address of the class structure!!
    # note gtype is a GObject type - NOT the GObjectClass type!!
    klass_ptr = hash(GObject.type_class_peek(gtype))

    return klass_ptr


def main ():

    from gi.repository import Gtk

    # so this is how to get the address of the class structure!!
    #trymod_klass = hash(GObject.type_class_peek(Try.Plugin))
    #print("python gobject trymod klass address %x"%hash(GObject.type_class_peek(Try.Plugin)))

    pdb.set_trace()

    gobjflds = Gtk.Bin.__info__.get_fields()
    #gobjflds = Gtk.Container.__info__.get_fields()

    for gobjfld in gobjflds:
        print("gobjfld",gobjfld)
        print("gobjfld",gobjfld.get_name())

        field_info_obj = get_field_info(gobjfld)

        offset = libgirepository.g_field_info_get_offset(field_info_obj)
        print("gobjfld offset",offset)

    #g_field_get_value(gobjfld, trymod_klass)
    #g_field_get_value(Try.PluginClass.__dict__['__info__'].get_fields()[1], trymod_klass)
    #g_field_get_value(Try.PluginClass.__dict__['__info__'].get_fields()[2], trymod_klass)

    pass


if __name__ == '__main__':
    main()
