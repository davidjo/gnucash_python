
import distutils.sysconfig

from distutils.core import setup, Extension

import commands

myprefix='/opt/local/'

_pkgcfg = None
def get_pkgcfg(do_fail=True):
    global _pkgcfg
    if _pkgcfg == -1:
        _pkgcfg = distutils.spawn.find_executable("pkg-config")
    if _pkgcfg is None and do_fail:
        raise Exception("pkg-config binary is required to compile extensions")
    return _pkgcfg

def get_pkgcfg(do_fail=True):
    return "pkg-config"

def pkgconfig(*packages, **kw):
    flag_map = {'-I': 'include_dirs',
                '-L': 'library_dirs',
                '-l': 'libraries'}
    for token in commands.getoutput(get_pkgcfg()+" --libs --cflags %s"
                                    % ' '.join(packages)).split():
        if flag_map.has_key(token[:2]):
            kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
        else: # throw others to extra_link_args
            kw.setdefault('extra_link_args', []).append(token)
        for k, v in kw.iteritems(): # remove duplicates
            kw[k] = list(set(v))
    return kw

#CFLAGS = `env PKG_CONFIG_PATH=${PYTHONLIB}/pkgconfig pkg-config --cflags gtk+-2.0 pygtk-2.0 webkit-1.0` -I${PYTHONINC} -I../../libqof/qof -I../../gnome-utils -I../../app-utils -I../../html -I../../engine -I. -I../.. -I../../..
#LDFLAGS = `env PKG_CONFIG_PATH=${PYTHONLIB}/pkgconfig pkg-config --libs gtk+-2.0 pygtk-2.0` -L${PYTHONLIB} -lpython2.6

gtkpkgdict = pkgconfig("gtk+-2.0")

include_list = gtkpkgdict['include_dirs']

include_list_gnucash = [ \
                        '../../gnc-module',
                        '../../gnome-utils',
                        '../../libqof/qof',
                        '../../..',
                       ]

include_list_pgobject = [ \
                          myprefix+'Library/Frameworks/Python.framework/Versions/2.7/include/pygtk-2.0',
                         ]

include_list_python = [ \
                          myprefix+'Library/Frameworks/Python.framework/Versions/2.7/include/python2.7',
                         ]

gobjectpkg = pkgconfig("gobject-2.0")

#setup(name="pythonplugin",version="1.0",ext_modules=[Extension("pythonplugin",["pythonplugin.c"],include_dirs=include_list+include_list_pgobject+include_list_gnucash,libraries=['glib-2.0','gobject-2.0','ffi'])])
#setup(name="pythonplugin",version="1.0",ext_modules=[Extension("pythonplugin",["pythonplugin.c"],include_dirs=include_list+include_list_pgobject+include_list_gnucash)])

#setup(name="pythoncallback",version="1.0",ext_modules=[Extension("pythoncallback",["pythoncallback.c"],include_dirs=include_list+include_list_pgobject)])

setup(name="swighelpers",version="1.0",ext_modules=[Extension("swighelpers",["swighelpers.c"],include_dirs=include_list+include_list_python+['.'])])

#distutils.sysconfig._config_vars['SO'] = ".dylib"

setup(name="pygkeyfile",version="1.0",ext_modules=[Extension("pygkeyfile",["pygkeyfile.c"],include_dirs=include_list+include_list_pgobject+['.'],library_dirs=gobjectpkg['library_dirs'],libraries=gobjectpkg['libraries']+['ffi','/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/pyglib-2.0-python2.7'])])

#OK this doesnt work as the flags are extra and the 3 architecures are already added
#setup(name="typcl",version="1.0",ext_modules=[Extension("typcl",["typcl.c"],extra_compile_args=['-arch', 'x86_64'],libraries=['tcl'],extra_link_args=['-arch','x86_64'])])

