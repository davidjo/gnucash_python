import sys
import os
import pdb
import traceback
print >> sys.stderr, "Imported python OK"

try:
    import _sw_app_utils
    from gnucash import *
    from _sw_core_utils import gnc_prefs_is_extra_enabled
except Exception, errexc:
    print >> sys.stderr, "Failed to import!!"
    print >> sys.stderr, str(errexc)
    pdb.set_trace()


print >> sys.stderr, "Imported python OK 1"

#pdb.set_trace()

# hmm - we apparently need to add the current path to search path

#sys.path.insert(0,os.path.dirname(__file__))
# switching to $HOME/.gnucash/python
hmpth = os.path.join(os.environ['HOME'],'.gnucash','python')
#if not os.path.exists(hmpth):
#    hmpth = os.path.dirname(__file__)
if os.path.exists(hmpth):
    sys.path.insert(0,hmpth)

try:
    import local_init
except ImportError:
    pass



from ctypes import *

from ctypes.util import find_library


# stupid but only way Ive figured to find where the gnucash library directory is

# use this to gain access to a quit function

libgnccorenm = find_library("libgnc-core-utils")
if libgnccorenm is None:
    raise RuntimeError("Can't find a libgnc-core-utils library to use.")

print libgnccorenm

libpth = os.path.dirname(libgnccorenm)

libgnomeutils = CDLL(os.path.join(libpth,"gnucash","libgncmod-gnome-utils.dylib"))

libgnomeutils.gnc_shutdown.argtypes = [ c_int ]
libgnomeutils.gnc_shutdown.restype = None


#pdb.set_trace()

# the reason it could not import pycons is because Id lost this!!
sys.path.append(os.path.dirname(__file__))

#noisy = gnc_prefs_is_extra_enabled()
noisy = True
if noisy:
    print "woop", os.path.dirname(__file__)

import pycons.console as cons
import gtk

if noisy:
    print "Hello from python!"
    #print "test", sys.modules.keys()
    #print "test2", dir(_sw_app_utils)

root = _sw_app_utils.gnc_get_current_root_account()

if noisy:
    #print "test", dir(root), root.__class__
    #print "test2", dir(gnucash_core_c)
    pass

acct = Account(instance = root)

if noisy:
   #print "test3", dir(acct)
   #print acct.GetName()
   #print acct.GetBalance()
   #print acct.GetSplitList()
   #print "test2", dir(gnucash.gnucash_core_c)
   pass

class Console (cons.Console):
    """ GTK python console """

    def __init__(self, argv=[], shelltype='python', banner=[],
                 filename=None, size=100):
        cons.Console.__init__(self, argv, shelltype, banner, filename, size)
        self.buffer.create_tag('center',
                               justification=gtk.JUSTIFY_CENTER,
                               font='Mono 4')
        self.figures = []
        self.callbacks = []
        self.last_figure = None
        self.active_canvas = None
        self.view.connect ('key-press-event', self.key_press_event)
        self.view.connect ('button-press-event', self.button_press_event)
        self.view.connect ('scroll-event', self.scroll_event)


    def key_press_event (self, widget, event):
        """ Handle key press event """
        
        if self.active_canvas:
            self.active_canvas.emit ('key-press-event', event)
            return True
        return cons.Console.key_press_event (self, widget, event)

    def scroll_event (self, widget, event):
        """ Scroll event """
        if self.active_canvas:
            return True
        return False
 
    def button_press_event (self, widget, event):
        """ Button press event """
        return self.refresh()

    def refresh (self):
        """ Refresh drawing """
        for fig in self.figures:
            figure, canvas, anchor = fig
            canvas.draw()
        return False


# Change this to "if True:" to switch on a python console at gnucash
# startup:
if False:
    console = Console(argv = [], shelltype = 'python', banner = [['woop', 'title']], size = 100)

    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_position(gtk.WIN_POS_CENTER)
    window.set_default_size(800,600)
    window.set_border_width(0)
    # Hm. gtk.main_quit will kill gnucash without closing the file
    # properly. That's kinda bad.
    #window.connect('destroy-event', gtk.main_quit)
    #window.connect('delete-event', gtk.main_quit)
    # this will call gtk.main_quit eventually
    window.connect('destroy-event', libgnomeutils.gnc_shutdown)
    window.connect('delete-event', libgnomeutils.gnc_shutdown)
    window.add (console)
    window.show_all()
    console.grab_focus()

