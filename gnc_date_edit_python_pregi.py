


import time

import datetime

import ctypes

import gobject

import gtk


import pdb


import gnome_utils_ctypes

from qof_ctypes import TM
from qof_ctypes import qof_scan_date
from qof_ctypes import qof_date_format_get,qof_date_format_get_string


def N_(msg):
    return msg



class GncDateEdit(gtk.HBox):

    GNC_DATE_EDIT_SHOW_TIME             = 1 << 0
    GNC_DATE_EDIT_24_HR                 = 1 << 1
    GNC_DATE_EDIT_WEEK_STARTS_ON_MONDAY = 1 << 2

    GNC_RD_WID_AB_BUTTON_POS            = 0
    GNC_RD_WID_AB_WIDGET_POS            = 1
    GNC_RD_WID_REL_BUTTON_POS           = 2
    GNC_RD_WID_REL_WIDGET_POS           = 3

    # ah - this is something I think Ive missed - we can name the GType here
    __gtype_name__ = 'GncDateEdit'

    # OK Im now thinking gobject warning messages were happening previously but just did not get the message

    __gproperties__ = {
                       'time' : (gobject.TYPE_INT64,                     # type
                                      N_('Date/time (seconds)'),         # nick name
                                      N_('Date/time represented in seconds since January 31st, 1970'),    # description
                                      gobject.G_MININT64,                # min value
                                      gobject.G_MAXINT64,                # max value
                                      0,                                 # default value
                                      gobject.PARAM_READWRITE),          # flags
                      }

    __gsignals__ = {
                   'time_changed' : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (int,)),
                   'date_changed' : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (int,)),
                   'format_changed' : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (int,)),
                   }


    def __init__ (self, the_time, flags=None):

        # this is equvivalent to gnc_date_edit_new_flags

        super(GncDateEdit,self).__init__()

        self.popup_in_progress = False
        self.lower_hour = 7
        self.upper_hour = 19
        if flags == None:
            self.flags = GncDateEdit.GNC_DATE_EDIT_SHOW_TIME
        else:
            self.flags = flags
        self.in_selected_handler = False

        self.initial_time = -1
        self.create_children()
        self.set_time_dt(the_time)


    @classmethod
    def new (cls, the_time, show_time, use_24_format):
        flags = (GncDateEdit.GNC_DATE_EDIT_SHOW_TIME if show_time else 0) | \
                                 (GncDateEdit.GNC_DATE_EDIT_24_HR if use_24_format else 0)
        newobj = cls(the_time, flags)
        return newobj

    @classmethod
    def new_ts (cls, the_time, show_time, use_24_format):
        newobj = cls.new(the_time, show_time, use_24_format)
        return newobj

    @classmethod
    def new_flags (cls, the_time, flags):
        newobj = cls(the_time, flags)
        return newobj

    def do_set_property (self, prop, val):
        if prop.name == 'time':
            self.time = val
            self.set_time_internal(val)
        else:
            raise AttributeError, 'unknown property %s' % prop.name
    def do_get_property (self, prop):
        if prop.name == 'time':
            return self.time
        else:
            raise AttributeError, 'unknown property %s' % prop.name

    def create_children (self):

        self.date_entry = gtk.Entry()
        self.date_entry.set_width_chars(11)
        self.pack_start(self.date_entry, expand=True, fill=True, padding=0)
        self.date_entry.show()
        self.date_entry.connect('key-press-event',self.key_press_entry)
        self.date_entry.connect('focus-out-event',self.focus_out_event)

        self.date_button = gtk.ToggleButton()
        self.date_button.connect('button-press-event', self.button_pressed)
        self.date_button.connect('toggled', self.button_toggled)
        self.pack_start(self.date_button, expand=False, fill=False, padding=0)

        hbox = gtk.HBox(homogeneous=False, spacing=3)
        self.date_button.add(hbox)
        hbox.show()

        self.cal_label = gtk.Label(str=N_("Calendar"))
        self.cal_label.set_alignment(0.0,0.5)
        hbox.pack_start(self.cal_label, expand=True, fill=True, padding=0)
        if (self.flags & GncDateEdit.GNC_DATE_EDIT_SHOW_TIME):
            self.cal_label.show()

        arrow = gtk.Arrow(arrow_type=gtk.ARROW_DOWN,shadow_type=gtk.SHADOW_NONE)
        hbox.pack_start(arrow,  expand=True, fill=False, padding=0)
        arrow.show()
        self.date_button.show()

        self.time_entry = gtk.Entry()
        self.time_entry.set_max_length(12)
        self.time_entry.set_size_request(88,-1)
        hbox.pack_start(self.time_entry, expand=True, fill=True, padding=0)

        store = gtk.ListStore(gobject.TYPE_STRING)
        self.time_combo = gtk.ComboBox(model=store)
        cell = gtk.CellRendererText()
        self.time_combo.pack_start(cell, expand=True)
        self.time_combo.set_attributes(cell,text=0)
        self.time_combo.connect("changed", self.set_time_cb)
        self.pack_start(self.time_combo, expand=False, fill=False, padding=0)

        self.connect("realize", self.fill_time_combo)

        # this seems to be needed in python to prevent showing time all
        # the time - the show_all in set_ui_widget_date seems to apply
        # fully recursively
        self.time_entry.set_no_show_all(True)
        self.time_combo.set_no_show_all(True)
        if (self.flags & GncDateEdit.GNC_DATE_EDIT_SHOW_TIME):
            self.time_entry.show()
            self.time_combo.show()

        self.cal_popup = gtk.Window(type=gtk.WINDOW_POPUP)
        self.cal_popup.set_name("gnc-date-edit-popup-window")
        self.cal_popup.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_COMBO)
        self.cal_popup.set_events(self.cal_popup.get_events() | gtk.gdk.KEY_PRESS_MASK)

        self.cal_popup.connect("delete-event", self.delete_popup)
        self.cal_popup.connect("key-press-event", self.key_press_popup)
        self.cal_popup.connect("button-press-event", self.button_pressed)
        self.cal_popup.connect("button-release-event", self.button_released)
        self.cal_popup.set_resizable(False)
        self.cal_popup.set_screen(self.get_screen())

        frame = gtk.Frame()
        frame.set_shadow_type(gtk.SHADOW_NONE)
        self.cal_popup.add(frame)
        frame.show()

        self.calendar = gtk.Calendar()
        #self.calendar.set_display_options(gtk.CALENDAR_SHOW_DAY_NAMES | gtk.CALENDAR_SHOW_HEADING)
        self.calendar.set_display_options(gtk.CALENDAR_SHOW_DAY_NAMES | gtk.CALENDAR_SHOW_HEADING \
                                            | (gtk.CALENDAR_WEEK_START_MONDAY if (self.flags & GncDateEdit.GNC_DATE_EDIT_WEEK_STARTS_ON_MONDAY) else 0))
        self.calendar.connect("button-release-event", self.button_released)
        self.calendar.connect("day-selected", self.day_selected)
        self.calendar.connect("day-selected-double-click", self.day_selected_double_click)
        frame.add(self.calendar)
        self.calendar.show()

    def set_time_internal (self, the_time):
        # in C we convert the time passed in seconds BACK to a time tuple
        # because we have defined the gobject property as a gint64 so it has
        # to be a time in seconds
        mytm = time.localtime(the_time)
        # do we do this in time type tuples or as datetime objects
        mydttm = datetime.datetime.fromtimestamp(float(the_time))

        # this is a qof function which does it according to locale etc
        # we should get the value from gnc_date_format
        # just junkily do it for the moment
        dtstr = mydttm.strftime("%m/%d/%y")
        print "set_time_internal",the_time
        print "set_time_internal",mydttm
        print "set_time_internal",dtstr
        self.date_entry.set_text(dtstr)
        if not self.in_selected_handler:
            print "set_time_internal 2"
            self.calendar.select_day(1)
            self.calendar.select_month(mydttm.month-1,mydttm.year)
            self.calendar.select_day(mydttm.day)

        if (self.flags & GncDateEdit.GNC_DATE_EDIT_24_HR):
            timstr = mydttm.strftime("%H:%M")
        else:
            timstr = mydttm.strftime("%I:%M %p")
        self.time_entry.set_text(timstr)

        self.emit("date_changed", 0)
        self.emit("time_changed", 0)
        

    def set_time_dt (self, the_time):
        ts = time.mktime(the_time.timetuple())
        print "set_time_dt",the_time
        print "set_time_dt",ts
        self.set_time(ts)

    def set_time_ts (self, the_time):
        print "set_time_ts",the_time
        self.set_time(the_time.tv_sec)

    def set_time (self, the_time):
        # is this needed??
        # note this must be a timestamp in seconds
        if type(the_time) != float and type(the_time) != int: pdb.set_trace()
        print "in set_time",the_time
        self.initial_time = int(the_time)
        self.set_property("time", int(the_time))


    def set_time_cb (self, widget):
        # this is called set_time but we also have gnc_date_edit_set_time which maps to set_time
        # renaming this as a callback - which is what it is
        #pdb.set_trace()
        model = self.time_combo.get_model()
        iter = self.time_combo.get_active_iter()
        timtupl = model.get(iter,0)
        txtstr = timtupl[0]
        self.time_entry.set_text(txtstr)
        self.emit("time_changed",0)

    def fill_time_combo (self, widget):

        #pdb.set_trace()

        if self.lower_hour > self.upper_hour:
            return

        model = self.time_combo.get_model()

        curtim = datetime.datetime.now()
        #tm_ret = gnc_localtime(curtim, &mtm)
        # not sure what is a good way to copy datetime objects
        # one way maybe to add a 0 timedelta??
        mtm = curtim + datetime.timedelta(seconds=0)


        for i in xrange(self.lower_hour,self.upper_hour+1):

             mtmp = mtm.replace(hour=i,minute=0)
             if (self.flags & GncDateEdit.GNC_DATE_EDIT_24_HR):
                 bufr = mtmp.strftime("%H:00")
             else:
                 bufr = mtmp.strftime("%I:00")
             # this in C code but not needed here
             #model.append((bufr,))
             for j in xrange(0,60,15):
                 mtmp = mtmp.replace(minute=j)
                 if (self.flags & GncDateEdit.GNC_DATE_EDIT_24_HR):
                     bufr = mtmp.strftime("%H:%M")
                 else:
                     bufr = mtmp.strftime("%I:%M")
                 model.append((bufr,))


    def gnc_handle_date_accelerator (self,event,dttm,txtstr):
        #pdb.set_trace()
        event_ptr = hash(event)
        tm_ctypes = TM()
        #tm_ctypes.tm_year = dttm.year - 1900
        #tm_ctypes.tm_mon = dttm.month - 1
        #tm_ctypes.tm_mday = dttm.day
        #tm_ctypes.tm_hour = dttm.hour
        #tm_ctypes.tm_min = dttm.minute
        #tm_ctypes.tm_sec = dttm.second
        tm_ptr = ctypes.addressof(tm_ctypes)
        retval = gnome_utils_ctypes.libgnc_gnomeutils.gnc_handle_date_accelerator(event_ptr,tm_ptr,txtstr)
        print tm_ctypes
        return (retval, dttm, tm_ctypes)

    def scan_date_python (self, txtstr):
        # re-implement junkily here
        print "scan_date",txtstr

        dtfmt = qof_get_date_format()
        print "scan_date",dtfmt

        # bad date formats apparently give ValueError exception
        try:
            # this is format in C - why the Z - because this is the date format
            # we get in linux
            newdt = datetime.datetime.strptime(txtstr, "%Y-%m-%dT%H:%M:%SZ")
            print "scan 1",newdt
        except ValueError:
            try:
                newdt = datetime.datetime.strptime(txtstr, "%Y-%m-%d")
                print "scan 2",newdt
            except ValueError:
                print "scan date: bad date format",txtstr
                return (False, None)
            else:
                return (True, newdt)
        else:
            return (True, newdt)

    def scan_date (self, txtstr):

        #dtfmt = qof_date_format_get()
        #dtfmtstr = qof_date_format_get_string(dtfmt)
        #print "scan_date",dtfmt,dtfmtstr

        #print "scan_date",txtstr

        (retcod, myday, mymonth, myyear) = qof_scan_date(txtstr)

        if retcod:
            newdt = datetime.datetime(day=myday,month=mymonth,year=myyear)
        else:
            newdt = None

        return (retcod, newdt)

    def get_date (self):
        #pdb.set_trace()
        # changed to get_date_internal returns a python datetime
        dttm = self.get_date_internal()
        #return time.mktime(tm)
        return dttm

    def get_date_internal (self):
        #pdb.set_trace()
        txtstr = self.date_entry.get_text()

        (date_was_valid, dttm) = self.scan_date(txtstr)

        if not date_was_valid:
            # actually looks like we get the start of today
            dttm = datetime.datetime.now()
            dttm = dttm.replace(hour=0,minute=0,second=0,microsecond=0)

        # some code dealing with time
        if (self.flags & GncDateEdit.GNC_DATE_EDIT_SHOW_TIME):
           timstr = self.time_entry.get_text()
           newtm = None
           try:
               newtm = datetime.datetime.strptime(timstr, "%H:%M %p")
           except ValueError:
               try:
                   newtm = datetime.datetime.strptime(timstr, "%H:%M")
               except ValueError:
                   # not clear what happens if bad time given
                   print "get_date_internal: bad time format",timstr
           if newtm != None:
               dttm = dttm.replace(hour=newtm.hour,minute=newtm.minute,second=newtm.second)

        else:
            dttm = dttm.replace(hour=0,minute=0,second=0,microsecond=0)

        return dttm

    def date_accel_key_press (self, widget, event):
        print "date_accel_key_press", widget
        txtstr = widget.get_text()
        print "date_accel_key_press", txtstr
        dttm = self.get_date_internal()
        (retcod, dttm, jnk) = self.gnc_handle_date_accelerator(event,dttm,txtstr)
        print "retcod, dttm, jnk", retcod,dttm,jnk
        if not retcod:
            return False
        pdb.set_trace()

        # gnc_mktime seems to convert the dttm to seconds from epoch
        # just use python datetime functions
        #self.set_time(self.gnc_mktime(dttm))
        self.set_time_dt(dttm)

        self.emit("time_changed",0)


    def key_press_entry (self, widget, event, *args):
        print "key_press_entry", widget, event, args

        if not self.date_accel_key_press(widget,event):
            return False

        self.stop_emission_by_name("key-press-event")
        return True

    def focus_out_event (self, event, *args):
        print "focus_out_event", event, args

        dttm = self.get_date_internal()
        #self.set_time(gnc_mktime(dttm))
        self.set_time_dt(dttm)

        dttm = self.get_date_internal()

        self.emit("date_changed",0)
        self.emit("time_changed",0)

        return False

    def button_pressed (self, *args):
        print "button_pressed",args
        widget = args[0]
        event = args[1]

        #pdb.set_trace()

        #ewidget = event.get_event_widget()
        # this does not exist - what is the replacement??
        # for the moment do explicit widget checks
        ewidget = widget

        #ENTER("widget=%p, ewidget=%p, event=%p, gde=%p", widget, ewidget, event, gde)

        if ewidget == self.cal_popup:
            print "Press on calendar popup. Ignoring."
            #LEAVE("Press on calendar popup. Ignoring.")
            return True

        if ewidget == self.calendar:
            print "Press on calendar. Ignoring."
            #LEAVE("Press on calendar. Ignoring.")
            return True

        if ewidget != self.date_button or self.date_button.get_active():
            print "Press, not on popup button, or while popup is raised."
            #LEAVE("Press, not on popup button, or while popup is raised.")
            return False

        if not self.date_button.has_focus():
            self.date_button.grab_focus()

        print "popup_in_progress set True"
        self.popup_in_progress = True

        self.edit_popup()

        self.date_button.set_active(True)

        #LEAVE("Popup in progress.")
        return True

    def grab_on_window (self, window, activate_time, grab_keyboard):
        print "grab_on_window"
        #pdb.set_trace()
        if gtk.gdk.pointer_grab(window, owner_events=True, event_mask=gtk.gdk.BUTTON_PRESS_MASK | \
                                    gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK,
                                       confine_to=None, cursor=None, time=activate_time) == 0:
            if not grab_keyboard or gtk.gdk.keyboard_grab(window, True, time=activate_time) == 0:
                print "grab_on_window 1"
                return True
            else:
                gtk.gdk.pointer_ungrab(window,time=activate_time)
                print "grab_on_window 2"
                return False
        return False

    def edit_popup (self):

        #pdb.set_trace()

        txtstr = self.date_entry.get_text()

        (date_was_valid, dttm) = self.scan_date(txtstr)

        if not date_was_valid:
            # actually looks like we get the start of today
            dttm = datetime.datetime.now()
            dttm = dttm.replace(hour=0,minute=0,second=0,microsecond=0)

        dttm = dttm.replace(hour=0,minute=0,second=0,microsecond=0)

        print "edit_popup",dttm
        self.calendar.select_day(1)
        self.calendar.select_month(dttm.month-1, dttm.year)
        self.calendar.select_day(dttm.day)

        toplevel = self.get_toplevel()

        if isinstance(toplevel,gtk.Window):

            toplevel.get_group().add_window(self.cal_popup)
            self.cal_popup.set_transient_for(toplevel)

        self.position_popup()

        self.cal_popup.show()

        self.cal_popup.grab_focus()
        self.date_button.set_active(True)

        if not self.calendar.has_focus():
            self.calendar.grab_focus()

        if not self.grab_on_window(self.cal_popup.get_window(), 0, True):
            self.cal_popup.hide()
            #LEAVE("Failed to grab window")
            return

        self.cal_popup.grab_add()

        #LEAVE(" ")

    def edit_popdown (self):
        #pdb.set_trace()
        #ENTER("gde %p", gde)
        self.cal_popup.grab_remove()
        self.cal_popup.hide()
        gtk.gdk.pointer_ungrab(time=0)
        self.date_button.set_active(False)

    def delete_popup (self):
        self.edit_popdown()
        return True

    def key_press_popup (self, widget, event):
        print "key_press_popup", widget, event
        if event.keyval != gtk.keysyms.Return and \
             event.keyval != gtk.keysyms.KP_Enter and \
                event.keyval != gtk.keysyms.Escape:
            return self.date_entry.date_accel_key_press(widget,event)

    def position_popup (self):
        req = self.cal_popup.size_request()
        (x,y) = self.date_button.window.get_origin()
        x += self.date_button.allocation.x
        y += self.date_button.allocation.y
        bwidth = self.date_button.allocation.width
        bheight = self.date_button.allocation.height
        print "req",req
        print "x,y",x,y
        print "bw,h",bwidth,bheight
        x += bwidth - req[0]
        y += bheight
        if x < 0: x = 0
        if y < 0: y = 0
        print "x,y",x,y
        self.cal_popup.move(x,y)



    def button_toggled (self, widget):
        print "button_toggled",widget

        #ENTER("widget %p, gde %p", widget, gde)
        #pdb.set_trace()

        if widget.get_active():
            print "toggled active",self.popup_in_progress
            if not self.popup_in_progress:
                self.edit_popup()
        else:
            print "toggled inactive",self.popup_in_progress
            self.edit_popdown()

        #LEAVE(" ")


    def button_released (self, widget, event):
        print "button_released",widget, event

        #ENTER("widget=%p, ewidget=%p, event=%p, gde=%p", widget, ewidget, event, gde)
        #pdb.set_trace()

        popup_in_progress = False
        if self.popup_in_progress:
            popup_in_progress = True
            print "popup_in_progress set False"
            self.popup_in_progress = False

        # this does not exist - what is the replacement??
        # we just check the first argument I think
        #ewidget = event.get_event_widget()
        ewidget = widget

        if ewidget == self.calendar:
            print "Button release on calendar."
            #LEAVE("Button release on calendar.")
            return False

        # it appears this can either be self.cal_popup or self.date_button
        # presumably get_event_widget returns self.date_button
        # yes - checking both widgets gives same behaviour as C version
        # not sure ever seen date_button end up here
        #if ewidget == self.date_button:
        if ewidget == self.cal_popup or ewidget == self.date_button:
            print "Button release on button."
            if not popup_in_progress and \
                self.date_button.get_active():
                self.edit_popdown()
                print "Release on button, not in progress. Popped down."
                #LEAVE("Release on button, not in progress. Popped down.")
                return True

            print "Button release on button. Allowing."
            #LEAVE("Button release on button. Allowing.")
            return False

        self.edit_popdown()
        #LEAVE("Release not on button or calendar. Popping down.")
        return True


    def day_selected (self, event):
        self.in_selected_handler = True
        dttupl = self.calendar.get_date()
        # big miss here - the month is 0 based but day is 1 based!!
        dttm = datetime.datetime(year=dttupl[0],month=dttupl[1]+1,day=dttupl[2])
        # where to convert to seconds - which is what the C does - and it stores seconds
        # this is no good - this is a string!!
        # we could convert back to integer I guess
        print "day_selected",dttupl
        print "day_selected",dttm
        #dtts = dttm.strftime("%s")
        dtts = time.mktime(dttm.timetuple())
        print "day_selected",dtts
        self.set_time(dtts)
        self.in_selected_handler = False

    def day_selected_double_click (self, event):
        self.edit_popdown()
