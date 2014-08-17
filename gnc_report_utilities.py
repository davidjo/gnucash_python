

import gnome_utils_ctypes


# define a function equivalent to N_ for internationalization
def N_(msg):
    return msg


def report_starting (report_name):
  gnome_utils_ctypes.libgnc_gnomeutils.gnc_window_show_progress(N_("Building '%s' report ..."%report_name), 0.0)

def report_render_starting (report_name):
  if report_name == None or report_name == "":
      rptnam = "Untitled"
  else:
      rptnam = report_name
  gnome_utils_ctypes.libgnc_gnomeutils.gnc_window_show_progress(N_("Rendering '%s' report ..."%rptnam), 0)

def report_percent_done (percent):
  if percent > 100.0:
      #(gnc:warn "report more than 100% finished. " percent))
      pass
  gnome_utils_ctypes.libgnc_gnomeutils.gnc_window_show_progress("", percent)

def report_finished():
  gnome_utils_ctypes.libgnc_gnomeutils.gnc_window_show_progress("", -1.0)

