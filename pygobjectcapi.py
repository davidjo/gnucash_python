
# new version working with introspection and python 3

import gi
# change to load all ctypes objects
#import ctypes
#from ctypes import pythonapi
from ctypes import *

class _PyGObject_Functions(Structure):
    _fields_ = [
        ('register_class',
         PYFUNCTYPE(c_void_p, py_object, c_char_p,
                           c_int, py_object,
                           py_object)),
        ('register_wrapper',
         PYFUNCTYPE(c_void_p, py_object)),
        ('lookupclass',
         PYFUNCTYPE(py_object, c_int)),
        ('pygobject_new',
         PYFUNCTYPE(py_object, c_void_p)),

        ('closure_new',
         PYFUNCTYPE(c_void_p, py_object, py_object, py_object)),
        ('object_watch_closure',
         PYFUNCTYPE(c_void_p, py_object, c_void_p)),
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
         PYFUNCTYPE(c_void_p, c_int, py_object, CFUNCTYPE(c_int, c_void_p, py_object))),
        ('value_from_pyobject',
         PYFUNCTYPE(c_int, c_void_p, py_object)),
        ('value_as_pyobject',
         PYFUNCTYPE(py_object, c_void_p, c_bool)),

        # these are dummy definitions currently

        ('register_interface',
         PYFUNCTYPE(c_void_p)),

        ('boxed_type', c_void_p),
        ('register_boxed',
         PYFUNCTYPE(c_void_p)),
        ('boxed_new',
         PYFUNCTYPE(c_void_p)),

        ('pointer_type', c_void_p),
        ('register_pointer',
         PYFUNCTYPE(c_void_p)),
        ('pointer_new',
         PYFUNCTYPE(c_void_p)),

        ('enum_add_constants',
         PYFUNCTYPE(c_void_p)),
        ('flags_add_constants',
         PYFUNCTYPE(c_void_p)),

        ('constant_strip_prefix',
         PYFUNCTYPE(c_void_p)),

        ('error_check',
         PYFUNCTYPE(c_void_p)),

        ('set_thread_block_funcs',
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
        ('enum_add',
         PYFUNCTYPE(c_void_p)),
        ('enum_from_gtype',
         PYFUNCTYPE(c_void_p)),

        ('flag_type', c_void_p),
        ('flags_add',
         PYFUNCTYPE(c_void_p)),
        ('flags_from_gtype',
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
        ('pygobject_construct',
         PYFUNCTYPE(c_void_p)),
        ('set_object_has_new_constructor',
         PYFUNCTYPE(c_void_p)),

        ('add_warning_redirection',
         PYFUNCTYPE(c_void_p, c_char_p, py_object)),
        ('disable_warning_redirections',
         PYFUNCTYPE(c_void_p)),

        ('nullfunc1',
         PYFUNCTYPE(c_void_p)),

        ('gerror_exception_check',
         PYFUNCTYPE(c_bool)),

        ('option_group_new',
         PYFUNCTYPE(py_object)),
        ('type_from_object_strict',
         PYFUNCTYPE(c_int)),

        ('pygobjectnew_full',
         PYFUNCTYPE(py_object, c_void_p, c_bool, c_void_p)),
        ('PyGObject_Type',
         c_void_p),

        ('pyg_value_from_pyobject_with_error',
         PYFUNCTYPE(c_int, c_void_p, py_object)),

        ]

class PyGObjectCAPI(object):

    def __init__(self):
        addr = self._as_void_ptr(gi._gobject._PyGObject_API)
        self._api = _PyGObject_Functions.from_address(addr)

    @classmethod
    def _capsule_name(cls, capsule):
        pythonapi.PyCapsule_GetName.restype = c_char_p
        pythonapi.PyCapsule_GetName.argtypes = [py_object]
        return pythonapi.PyCapsule_GetName(capsule)

    @classmethod
    def _as_void_ptr(cls, capsule):
        name = cls._capsule_name(capsule)
        pythonapi.PyCapsule_GetPointer.restype = c_void_p
        pythonapi.PyCapsule_GetPointer.argtypes = [
            py_object, c_char_p]
        return pythonapi.PyCapsule_GetPointer(capsule, name)

    def to_object(self, addr):
        return self._api.pygobject_new(addr)



# call like this:
# Cgobject = PyGObjectCAPI()
# Cgobject.to_object(memory_address)

# to get memory address from a gobject:
#  address = hash(obj)

