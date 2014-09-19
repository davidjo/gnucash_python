

import os

import sys

import gobject

import pdb


from ctypes import *


# this is taken from pygtk FAQ 23.41

# this boilerplate can convert a memory address
# into a proper python gobject.

# this fixup is needed as the apparent return type for PyCObject_AsVoidPtr
# is c_int!!

pythonapi.PyCObject_AsVoidPtr.argtypes = [ py_object ]
pythonapi.PyCObject_AsVoidPtr.restype = c_void_p

# NOTA BENE - this depends on the _PyGObject_Functions struct in gobjectmodule.c
# in pygobject

CAPI_GObject = c_void_p
CAPI_GClosure = c_void_p
CAPI_GValue = c_void_p

class _PyGObject_Functions(Structure):
    _fields_ = [
        ('register_class',
         PYFUNCTYPE(c_void_p, py_object, c_char_p,
                           c_int, py_object,
                           py_object)),
        ('register_wrapper',
         PYFUNCTYPE(c_void_p, py_object)),
        ('register_sinkfunc',
         PYFUNCTYPE(c_void_p, c_int, c_void_p)),
        ('lookupclass',
         PYFUNCTYPE(py_object, c_int)),
        ('newgobj',
         PYFUNCTYPE(py_object, CAPI_GObject)),

        ('closure_new',
         PYFUNCTYPE(CAPI_GClosure, py_object, py_object, py_object)),
        ('object_watch_closure',
         PYFUNCTYPE(c_void_p, py_object, CAPI_GClosure)),
        ('destroy_notify',
         PYFUNCTYPE(c_void_p)),

        ('type_from_object',
         PYFUNCTYPE(c_int, py_object)),
        ('type_wrapper_new',
         PYFUNCTYPE(py_object, c_int)),
        ('enum_get_value',
         PYFUNCTYPE(c_int, c_int, py_object, c_int)),
        ('flags_get_value',
         PYFUNCTYPE(c_int, c_int, py_object, c_int)),
        ('register_gtype_custom',
         PYFUNCTYPE(c_void_p, c_int, py_object, CFUNCTYPE(c_int, CAPI_GValue, py_object))),
        ('value_from_pyobject',
         PYFUNCTYPE(c_int, CAPI_GValue, py_object)),
        ('value_as_pyobject',
         PYFUNCTYPE(py_object, CAPI_GValue, c_bool)),

        # these are dummy definitions currently

        ('register_interface',
         PYFUNCTYPE(c_void_p)),

        ('boxed_type', c_void_p),
        ('pyg_register_boxed',
         PYFUNCTYPE(c_void_p)),
        ('pyg_boxed_new',
         PYFUNCTYPE(c_void_p)),

        ('pointer_type', c_void_p),
        ('register_pointer',
         PYFUNCTYPE(c_void_p)),
        ('pointer_new',
         PYFUNCTYPE(c_void_p)),

        ('pyg_enum_add_constants',
         PYFUNCTYPE(c_void_p)),
        ('pyg_flags_add_constants',
         PYFUNCTYPE(c_void_p)),

        ('pyg_constant_strip_prefix',
         PYFUNCTYPE(c_void_p)),

        ('pyg_error_check',
         PYFUNCTYPE(c_void_p)),

        ('pyg_set_thread_block_funcs',
         PYFUNCTYPE(c_void_p)),
        ('block_threads', # /* block_threads */
         CFUNCTYPE(c_void_p)),
	('unblock_threads', # /* unblock_threads */
         PYFUNCTYPE(c_void_p)),

        ('paramspec_type', c_void_p),
        ('param_spec_new',
         PYFUNCTYPE(c_void_p)),
        ('param_spec_from_object',
         PYFUNCTYPE(c_void_p)),

        ('pyobj_to_unichar_conv',
         PYFUNCTYPE(c_void_p)),
        ('parse_constructor_args',
         PYFUNCTYPE(c_void_p)),
        ('param_gvalue_as_pyobject',
         PYFUNCTYPE(c_void_p)),
        ('param_gvalue_from_pyobject',
         PYFUNCTYPE(c_void_p)),

        ('enum_type', c_void_p),
        ('pyg_enum_add',
         PYFUNCTYPE(c_void_p)),
        ('pyg_enum_from_gtype',
         PYFUNCTYPE(c_void_p)),

        ('flag_type', c_void_p),
        ('pyg_flags_add',
         PYFUNCTYPE(c_void_p)),
        ('pyg_flags_from_gtype',
         PYFUNCTYPE(c_void_p)),

        ('threads_enabled', c_bool), # /* threads_enabled */
        ('enable_threads',
         PYFUNCTYPE(c_int)),
        ('gil_state_ensure',
         PYFUNCTYPE(c_int)),
        ('gil_state_release',
         PYFUNCTYPE(c_void_p)),
        ('register_class_init',
         PYFUNCTYPE(c_void_p)),
        ('register_interface_info',
         PYFUNCTYPE(c_void_p)),

        ('closure_set_exception_handler',
         PYFUNCTYPE(c_void_p)),
        ('pygobject_constructv',
         PYFUNCTYPE(c_void_p)),
        ('pygobject_construct',
         PYFUNCTYPE(c_void_p)),
        ('set_object_has_new_constructor',
         PYFUNCTYPE(c_void_p)),

        ('add_warning_redirection',
         PYFUNCTYPE(c_void_p, c_char_p, py_object)),
        ('disable_warning_redirections',
         PYFUNCTYPE(c_void_p)),

        ('type_register_custom_callback',
         PYFUNCTYPE(c_void_p)),
        ('gerror_exception_check',
         PYFUNCTYPE(c_bool)),

        ('option_group_new',
         PYFUNCTYPE(py_object)),
        ('type_from_object_strict',
         PYFUNCTYPE(c_int)),

        ]



class PyGObjectCAPI(object):
    def __init__(self):
        # for the moment this appears to be the same
        # even with gi
        #pdb.set_trace()
        print "pygobject addr 1",gobject._PyGObject_API
        addr = pythonapi.PyCObject_AsVoidPtr(
            py_object(gobject._PyGObject_API))
        print "pygobject addr %x"%addr
        self._api = _PyGObject_Functions.from_address(addr)

    def pygobject_new(self, addr):
        return self._api.newgobj(addr)

    def disable_warning_redirections(self):
        return self._api.disable_warning_redirections()


# call like this:
# Cgobject = PyGObjectCAPI()
# Cgobject.pygobject_new(memory_address)

# to get memory address from a gobject:
#  address = hash(obj)

