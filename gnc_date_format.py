
# special date widget

import gobject

import gtk

from datetime import datetime

import pdb


import qof_ctypes


from gnc_builder import GncBuilder

class GncDateFormat(gtk.HBox):

    # ah - this is something I think Ive missed - we can name the GType here
    __gtype_name__ = 'GncDateFormat'

    # OK Im now thinking gobject warning messages were happening previously but just did not get the message

    cmnt = """
    __gproperties__ = {
                       'report-id' : (gobject.TYPE_INT,                       # type
                                      N_('The numeric ID of the report.'),    # nick name
                                      N_('The numeric ID of the report.'),    # description
                                      -1,                                     # min value
                                      gobject.G_MAXINT,                       # max value
                                      -1,                                     # default value
                                      gobject.PARAM_READWRITE),               # flags
                                      #gobject.PARAM_CONSTRUCT_ONLY | gobject.PARAM_READWRITE),      # flags
                      }
    """

    __gsignals__ = {
                   'format_changed' : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (int,))
                   }


    def __init__ (self):

        super(GncDateFormat,self).__init__()

        builder = GncBuilder()
        builder.add_from_file("gnc-date-format.glade", "format-liststore")
        builder.add_from_file("gnc-date-format.glade", "GNC Date Format")

        # junkily we need to list all signals here
        # the gnucash code somehow figures all signals
        # turns out only one callback is actually defined
        self.builder_handlers = { \
                                'gnc_ui_date_format_changed_cb' : self.changed_cb
                                }

        # another way to do this is to use self as the argument - which I assume means
        # will look for the function in the current object
        # unfortunately to use the blocking I need the handler_id which is not available
        # when using this method
        #builder.connect_signals(self)
        builder.connect_signals(self.builder_handlers)

        self.label = builder.get_object("widget_label")
        self.format_combobox = builder.get_object("format_combobox")
        self.months_label = builder.get_object("months_label")
        self.month_number = builder.get_object("month_number_button")
        self.month_abbrev = builder.get_object("month_abbrev_button")
        self.month_name = builder.get_object("month_name_button")
        self.years_label = builder.get_object("years_label")
        self.years_button = builder.get_object("years_button")
        self.custom_label = builder.get_object("format_label")
        self.custom_entry = builder.get_object("format_entry")
        self.sample_label = builder.get_object("sample_label")

        self.custom_entry.handler_block_by_func(self.changed_cb)
        self.set_format(qof_ctypes.qof_date_format_get())
        self.custom_entry.handler_unblock_by_func(self.changed_cb)

        dialog = builder.get_object("GNC Date Format")
        table = builder.get_object("date_format_table")

        dialog.remove(table)
        self.add(table)

        dialog.destroy()


    def enable_month (self, sensitive):
        self.months_label.set_sensitive(sensitive)
        self.month_number.set_sensitive(sensitive)
        self.month_abbrev.set_sensitive(sensitive)
        self.month_name.set_sensitive(sensitive)

    def enable_year (self, sensitive):
        self.years_label.set_sensitive(sensitive)
        self.years_button.set_sensitive(sensitive)

    def enable_format (self, sensitive):
        self.custom_label.set_sensitive(sensitive)
        self.custom_entry.set_sensitive(sensitive)


    def refresh (self):

        sel_option = self.format_combobox.get_active()

        if sel_option == qof_ctypes.QofDateFormat.QOF_DATE_FORMAT_CUSTOM:
            format = self.custom_entry.get_text()
            enable_year = False
            enable_month = False
            check_modifiers = False
            enable_custom = True
        elif sel_option == qof_ctypes.QofDateFormat.QOF_DATE_FORMAT_LOCALE or \
             sel_option == qof_ctypes.QofDateFormat.QOF_DATE_FORMAT_UTC:
            format = qof_ctypes.qof_date_format_get_string(sel_option)
            enable_year = False
            enable_month = False
            check_modifiers = False
            enable_custom = False
        elif sel_option == qof_ctypes.QofDateFormat.QOF_DATE_FORMAT_ISO:
            self.month_number.set_active(True)
            enable_year = True
            enable_month = False
            check_modifiers = True
            enable_custom = False
        else:
            enable_year = True
            enable_month = True
            check_modifiers = True
            enable_custom = False

        self.enable_year(enable_year)
        self.enable_month(enable_month)
        self.enable_format(enable_custom)

        if check_modifiers:
            if self.month_number.get_active():
                format = qof_ctypes.qof_date_format_get_string(sel_option)
            else:
                format = qof_ctypes.qof_date_text_format_get_string(sel_option)
                if self.month_name.get_active():
                    indx = format.find('b')
                    if indx >= 0:
                        format = format[0:indx]+'B'+format[indx+1:]
            if self.years_button.get_active():
                indx = format.find('y')
                if indx >= 0:
                    format = format[0:indx]+'Y'+format[indx+1:]

        #self.custom_entry.signal_handler_block()
        self.custom_entry.handler_block_by_func(self.changed_cb)
        self.custom_entry.set_text(format)
        #self.custom_entry.signal_handler_unblock()
        self.custom_entry.handler_unblock_by_func(self.changed_cb)

        #secs_now = datetime.now()
        #today = datetime.localtime(secs_now)
        today = datetime.now()
        date_string = qof_ctypes.qof_strftime(format, today)

        self.sample_label.set_text(date_string)


    def set_format (self, format):
        self.format_combobox.set_active(format)
        self.compute_format()

    def get_format (self):
        return self.format_combobox.get_active()

    def compute_format (self):
        print "compute_format"
        self.refresh()
        #pdb.set_trace()
        #self.emit("format_changed",0)

    def changed_cb (self, *args):
        print "changed_cb", args
        #pdb.set_trace()
        self.compute_format()
