
import os

import glob

import pkgutil

import importlib


import traceback

import pdb



modules = glob.glob(os.path.dirname(__file__)+"/*.py")

__all__ = [ os.path.basename(f)[:-3] for f in modules if not os.path.basename(f).startswith('_') and not f.endswith('__init__.py') and os.path.isfile(f) ]

# this seems to only work in a __init__.py file - because __package__ is defined
for (module_loader, name, ispkg) in pkgutil.iter_modules([os.path.dirname(__file__)]):
    try:
        importlib.import_module('.'+name, __package__)
    except Exception as errexc:
        traceback.print_exc()
        pdb.set_trace()


