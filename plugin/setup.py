
import distutils.sysconfig

from distutils.core import setup, Extension

myprefix='/opt/local/'

#-I/opt/local/include/gtk-2.0 -I/opt/local/lib/gtk-2.0/include -I/opt/local/include/atk-1.0 -I/opt/local/include/cairo -I/opt/local/include/gdk-pixbuf-2.0 -I/opt/local/include/pango-1.0 -I/opt/local/include/gio-unix-2.0/ -I/opt/local/include/glib-2.0 -I/opt/local/lib/glib-2.0/include -I/opt/local/include/pixman-1 -I/opt/local/include/freetype2 -I/opt/local/include/libpng14

include_list = [ \
                myprefix,
                myprefix+'include/gtk-2.0',
                myprefix+'include/gtk-2.0/include',
                myprefix+'include/atk-1.0',
                myprefix+'include/cairo',
                myprefix+'include/gdk-pixbuf-2.0',
                myprefix+'include/pango-1.0',
                myprefix+'include/gio-unix-2.0',
                myprefix+'lib/gtk-2.0/include',
                myprefix+'lib/glib-2.0/include',
                myprefix+'include/glib-2.0',
               ]

include_list_gnucash = [ \
                        '../../gnc-module',
                        '../../gnome-utils',
                        '../../libqof/qof',
                        '../../..',
                       ]

include_list_pgobject = [ \
                          myprefix+'Library/Frameworks/Python.framework/Versions/2.6/include/python2.6/pygtk-2.0',
                         ]

#setup(name="pythonplugin",version="1.0",ext_modules=[Extension("pythonplugin",["pythonplugin.c"],include_dirs=include_list+include_list_pgobject+include_list_gnucash,libraries=['glib-2.0','gobject-2.0','ffi'])])
#setup(name="pythonplugin",version="1.0",ext_modules=[Extension("pythonplugin",["pythonplugin.c"],include_dirs=include_list+include_list_pgobject+include_list_gnucash)])

#setup(name="pythoncallback",version="1.0",ext_modules=[Extension("pythoncallback",["pythoncallback.c"],include_dirs=include_list+include_list_pgobject)])

setup(name="swighelpers",version="1.0",ext_modules=[Extension("swighelpers",["swighelpers.c"],include_dirs=include_list+include_list_pgobject+['.'])])

#distutils.sysconfig._config_vars['SO'] = ".dylib"

setup(name="pygkeyfile",version="1.0",ext_modules=[Extension("pygkeyfile",["pygkeyfile.c"],include_dirs=include_list+include_list_pgobject+['.'],library_dirs=['/opt/local/lib'],libraries=['glib-2.0','gobject-2.0','ffi','/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/pyglib-2.0-python2.6'])])

#OK this doesnt work as the flags are extra and the 3 architecures are already added
#setup(name="typcl",version="1.0",ext_modules=[Extension("typcl",["typcl.c"],extra_compile_args=['-arch', 'x86_64'],libraries=['tcl'],extra_link_args=['-arch','x86_64'])])

