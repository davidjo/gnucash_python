


import time

import datetime

from gi.repository import GObject

from gi.repository import GLib

from gi.repository import Gtk
from gi.repository import Gdk


import pdb


def N_(msg):
    return msg


class GncDateEdit(Gtk.HBox):

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
                       # 'time' : (GObject.TYPE_INT64,                     # type
                       'time' : (long,                                   # type
                                      N_('Date/time (seconds)'),         # nick name
                                      N_('Date/time represented in seconds since January 31st, 1970'),    # description
                                      GLib.MININT64,                     # min value
                                      GLib.MAXINT64,                     # max value
                                      0,                                 # default value
                                      GObject.ParamFlags.READWRITE),     # flags
                      }

    __gsignals__ = {
                   'time_changed' : (GObject.SignalFlags.RUN_FIRST, None, (int,)),
                   'date_changed' : (GObject.SignalFlags.RUN_FIRST, None, (int,)),
                   'format_changed' : (GObject.SignalFlags.RUN_FIRST, None, (int,)),
                   }


    def __init__ (self, the_time, flags):

        # this is equvivalent to gnc_date_edit_new_flags

        super(GncDateEdit,self).__init__()

        #pdb.set_trace()

	self.popup_in_progress = False
        self.lower_hour = 7
        self.upper_hour = 19
        # need to rename as self.flags is parent HBox flags
        self.gde_flags = GncDateEdit.GNC_DATE_EDIT_SHOW_TIME
        self.in_selected_handler = False

        self.gde_flags = flags
        self.initial_time = -1
        self.create_children()
        self.set_time(the_time)


    @classmethod
    def new (cls, the_time, show_time, use_24_format):
        newobj = cls(the_time, (GncDateEdit.GNC_DATE_EDIT_SHOW_TIME if show_time else 0) | \
                                 (GncDateEdit.GNC_DATE_EDIT_24_HR if use_24_format else 0))
        return newobj

    @classmethod
    def new_ts (cls, the_time, show_time, use_24_format):
        newobj = cls(the_time, show_time, use_24_format)
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

        self.date_entry = Gtk.Entry()
        self.date_entry.set_width_chars(11)
        self.pack_start(self.date_entry, True, True, 0)
        self.date_entry.show()
        self.date_entry.connect('key-press-event',self.key_press_entry)
        self.date_entry.connect('focus-out-event',self.focus_out_event)

        self.date_button = Gtk.ToggleButton()
        self.date_button.connect('button-press-event', self.button_pressed)
        self.date_button.connect('toggled', self.button_toggled)
        self.pack_start(self.date_button, False, False, 0)

        hbox = Gtk.HBox(homogeneous=False, spacing=3)
        self.date_button.add(hbox)
        hbox.show()

        self.cal_label = Gtk.Label(N_("Calendar"))
        self.cal_label.set_alignment(0.0,0.5)
        hbox.pack_start(self.cal_label, True, True, 0)
        if self.gde_flags & GncDateEdit.GNC_DATE_EDIT_SHOW_TIME:
            self.cal_label.show()

        arrow = Gtk.Arrow(arrow_type=Gtk.ArrowType.DOWN,shadow_type=Gtk.ShadowType.NONE)
        hbox.pack_start(arrow,  True, False, 0)
        arrow.show()
        self.date_button.show()

        self.time_entry = Gtk.Entry()
        self.time_entry.set_max_length(12)
        self.time_entry.set_size_request(88,-1)
        hbox.pack_start(self.time_entry, True, True, 0)

        store = Gtk.ListStore(GObject.TYPE_STRING)
        self.time_combo = Gtk.ComboBox(model=store)
        cell = Gtk.CellRendererText()
        self.time_combo.pack_start(cell, True)
        self.time_combo.add_attribute(cell,"text",0)
        self.time_combo.connect("changed", self.set_time_cb)
        self.pack_start(self.time_combo, False, False, 0)

        self.connect("realize", self.fill_time_combo)

        if self.gde_flags & GncDateEdit.GNC_DATE_EDIT_SHOW_TIME:
            self.time_entry.show()
            self.time_combo.show()

        self.cal_popup = Gtk.Window(type=Gtk.WindowType.POPUP)
        self.cal_popup.set_name("gnc-date-edit-popup-window")
        self.cal_popup.set_type_hint(Gdk.WindowTypeHint.COMBO)
        self.cal_popup.set_events(self.cal_popup.get_events() | Gdk.EventMask.KEY_PRESS_MASK)

        self.cal_popup.connect("delete-event", self.delete_popup)
        self.cal_popup.connect("key-press-event", self.key_press_popup)
        self.cal_popup.connect("button-press-event", self.button_pressed)
        self.cal_popup.connect("button-release-event", self.button_released)
        self.cal_popup.set_resizable(False)
        self.cal_popup.set_screen(self.get_screen())

        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        self.cal_popup.add(frame)
        frame.show()

        self.calendar = Gtk.Calendar()
        #self.calendar.set_display_options(Gtk.CalendarDisplayOptions.SHOW_DAY_NAMES | Gtk.CalendarDisplayOptions.SHOW_HEADING)
        if (self.gde_flags & GncDateEdit.GNC_DATE_EDIT_WEEK_STARTS_ON_MONDAY):
            self.calendar.set_display_options(Gtk.CalendarDisplayOptions.SHOW_DAY_NAMES | Gtk.CalendarDisplayOptions.SHOW_HEADING | Gtk.CalendarDisplayOptions.WEEK_START_MONDAY)
        else:
            self.calendar.set_display_options(Gtk.CalendarDisplayOptions.SHOW_DAY_NAMES | Gtk.CalendarDisplayOptions.SHOW_HEADING)
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
        self.date_entry.set_text(dtstr)
        if not self.in_selected_handler:
            self.calendar.select_day(1)
            self.calendar.select_month(mydttm.month,mydttm.year)
            self.calendar.select_day(mydttm.day)

        if self.gde_flags & GncDateEdit.GNC_DATE_EDIT_24_HR:
            timstr = mydttm.strftime("%H:%M")
        else:
            timstr = mydttm.strftime("%I:%M %p")
        self.time_entry.set_text(timstr)

        self.emit("date_changed", 0)
        self.emit("time_changed", 0)
        

    def set_time_dt (self, the_time):
        ts = time.mktime(the_time.timetuple())
        self.set_time(ts)

    def set_time_ts (self, the_time):
        self.set_time(the_time)

    def set_time (self, the_time):
        # is this needed??
        # note this must be a timestamp in seconds
        self.initial_time = the_time
        self.set_property("time", the_time)


    def set_time_cb (self, event):
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
             if self.gde_flags & GncDateEdit.GNC_DATE_EDIT_24_HR:
                 bufr = mtmp.strftime("%H:00")
             else:
                 bufr = mtmp.strftime("%I:00")
             model.append((bufr,))
             for j in xrange(0,60,15):
                 mtmp = mtmp.replace(minute=j)
                 if self.gde_flags & GncDateEdit.GNC_DATE_EDIT_24_HR:
                     bufr = mtmp.strftime("%H:%M")
                 else:
                     bufr = mtmp.strftime("%I:%M")
                 model.append((bufr,))


    def gnc_handle_date_accelerator (self,dttm,txtstr):
        pdb.set_trace()

    def scan_date (self, txtstr):
        # re-implement junkily here
        print "scan_date",txtstr

        # bad date formats apparently give ValueError exception
        try:
            # this is format in C - why the Z - because this is the date format
            # we get in linux
            newdt = datetime.datetime.strptime(txtstr, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            try:
                newdt = datetime.datetime.strptime(txtstr, "%Y-%m-%d")
            except ValueError:
                return (False, None)
            else:
                return (True, newdt)
        else:
            return (True, newdt)

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
        if (self.gde_flags & GncDateEdit.GNC_DATE_EDIT_SHOW_TIME):
           timstr = self.time_entry.get_text()
           newtm = None
           try:
               newtm = datetime.datetime.strptime(timstr, "%H:%M:%S %p")
           except ValueError:
               try:
                   newtm = datetime.datetime.strptime(timstr, "%H:%M:%S")
               except ValueError:
                   # not clear what happens if bad time given
                   pass
           if newtm != None:
               dttm = dttm.replace(hour=newtm.hour,minute=newtm.minute,second=newtm.second)

        else:
            dttm = dttm.replace(hour=0,minute=0,second=0,microsecond=0)

        return dttm

    def date_accel_key_press (self, event):
        txtstr = self.get_text()
        dttm = self.get_date_internal()
        if not self.gnc_handle_date_accelerator(dttm,txtstr):
            return False

        # gnc_mktime seems to convert the dttm to seconds from epoch
        # just use python datetime functions
        #self.set_time(self.gnc_mktime(dttm))
        self.set_time(dttm)

        self.emit("time_changed",0)


    def key_press_entry (self, event):

        if not self.date_accel_key_press(event):
            return False

        self.stop_emission_by_name("key-press-event")
        return True

    def focus_out_event (self, event):

        dttm = self.get_date_internal()
        #self.set_time(gnc_mktime(dttm))
        self.set_time(dttm)

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
        # apparently we now need to set a cursor
        cursor = Gdk.Cursor(cursor_type=Gdk.CursorType.ARROW)
        if Gdk.pointer_grab(window, True, Gdk.EventMask.BUTTON_PRESS_MASK | \
                                    Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK,
                                       window, cursor, activate_time) == 0:
            if not grab_keyboard or Gdk.keyboard_grab(window, True, activate_time) == 0:
                print "grab_on_window 1"
                return True
            else:
                Gdk.pointer_ungrab(window,activate_time)
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

        self.calendar.select_day(1)
        self.calendar.select_month(dttm.month, dttm.year)
        self.calendar.select_day(dttm.day)

        toplevel = self.get_toplevel()

        if isinstance(toplevel,Gtk.Window):

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

        Gtk.grab_add(self.cal_popup)

        #LEAVE(" ")

    def edit_popdown (self):
        #pdb.set_trace()
        #ENTER("gde %p", gde)
        Gtk.grab_remove(self.cal_popup)
        self.cal_popup.hide()
        Gdk.pointer_ungrab(0)
        self.date_button.set_active(False)

    def delete_popup (self):
        self.edit_popdown()
        return True

    def key_press_popup (self, widget, event):
        print "key_press_popup", widget, event
        if event.keyval != Gdk.KEY_Return and \
             event.keyval != Gdk.KEY_KP_Enter and \
                event.keyval != Gdk.KEY_Escape:
            return self.date_entry.date_accel_key_press(event)

    def position_popup (self):
        #pdb.set_trace()
        req = Gtk.Requisition()
        self.cal_popup.size_request(req)
        #(x,y) = self.date_button.window.get_origin()
        (ret, x, y) = self.date_button.get_window().get_origin()
        x += self.date_button.allocation.x
        y += self.date_button.allocation.y
        bwidth = self.date_button.allocation.width
        bheight = self.date_button.allocation.height
        print "req",req
        print "x,y",x,y
        print "bw,h",bwidth,bheight
        x += bwidth - req.width
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
        #print "dayselected",dttupl
        dttm = datetime.datetime(year=dttupl[0],month=dttupl[1],day=dttupl[2])
        # where to convert to seconds - which is what the C does - and it stores seconds
        # this is no good - this is a string!!
        # we could convert back to integer I guess
        #dtts = dttm.strftime("%s")
        dtts = time.mktime(dttm.timetuple())
        self.set_time_ts(dtts)
        self.in_selected_handler = False

    def day_selected_double_click (self, event):
        self.edit_popdown()
