
import sys

from gi.repository import Gtk


import pdb



# define a function equivalent to N_ for internationalization
def N_(msg):
    return msg



class GncFileDialog(object):


    GNC_FILE_DIALOG_OPEN = 0
    GNC_FILE_DIALOG_IMPORT = 1
    GNC_FILE_DIALOG_SAVE = 2
    GNC_FILE_DIALOG_EXPORT = 3


    def __init__ (self):
        pass


    def gnc_gtk_dialog_add_button (self, dialog, label, stock_id, response):

        #button = Gtk.Button(label=label)
        button = Gtk.Button(label)

        if stock_id:

            image = Gtk.Image()
            image.set_from_stock(stock_id, Gtk.IconSize.BUTTON)

            button.set_image(image)

        button.set_property("can-default", True)

        button.show_all()

        dialog.add_action_widget(button, response)


    def gnc_file_dialog (self, title, filters, starting_dir, dialog_type):

        okbutton = Gtk.STOCK_OPEN
        ok_icon = None
        action = Gtk.FileChooserAction.OPEN

        if dialog_type == GncFileDialog.GNC_FILE_DIALOG_OPEN:

            action = Gtk.FileChooserAction.OPEN
            okbutton = Gtk.STOCK_OPEN
            if title == None:
                title = N_("Open")

        elif dialog_type == GncFileDialog.GNC_FILE_DIALOG_IMPORT:

            action = Gtk.FileChooserAction.OPEN
            okbutton = N_("_Import")
            if title == None:
                title = N_("Import")

        elif dialog_type == GncFileDialog.GNC_FILE_DIALOG_SAVE:

            action = Gtk.FileChooserAction.SAVE
            okbutton = Gtk.STOCK_SAVE
            if title == None:
                title = N_("Save")

        elif dialog_type == GncFileDialog.GNC_FILE_DIALOG_EXPORT:

            action = Gtk.FileChooserAction.SAVE
            okbutton = N_("_Export")
            ok_icon = Gtk.STOCK_CONVERT
            if title == None:
                title = N_("Export")

        print >> sys.stderr, "doing dialog type",dialog_type,okbutton


        #file_box = Gtk.FileChooserDialog(title=title, parent=None, action=action, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), backend=None)
        file_box = Gtk.FileChooserDialog(title, None, action, (Gtk.STOCK_CANCEL, Gtk.RESPONSE_CANCEL), None)

        if ok_icon:
            self.gnc_gtk_dialog_add_button(file_box, okbutton, ok_icon, Gtk.ResponseType.ACCEPT)
        else:
            file_box.add_button(okbutton, Gtk.ResponseType.ACCEPT)

        if starting_dir:
            file_box.set_current_folder(starting_dir)

        file_box.set_modal(True)

        # file_box.set_transient_for(gnc_ui_get_toplevel())

        if filters != None:

            pass

        response = file_box.run()

        if response == Gtk.ResponseType.ACCEPT:

            internal_name = file_box.get_uri()

            if internal_name.startswith("file://"):
                internal_name = file_box.get_filename()

            file_name = internal_name

        file_box.destroy()

        if file_name == "":
           file_name = "(null)"


        return file_name

