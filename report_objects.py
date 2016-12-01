
import sys

import traceback
import pdb

# NOTA BENE - at the moment the pregi and gi version are identical
#           - not clear there will be a difference!!

#try:
#    from gi.repository import GObject
#    import report_objects_gi
#except ImportError:
#    import gobject
#    import report_objects_pregi

try:
    from gi.repository import GObject
    import report_objects_gi
    from report_objects_gi import Report
    from report_objects_gi import ReportTemplate
    from report_objects_gi import OptionsDB
    from report_objects_gi import load_python_reports

    python_reports_by_name = report_objects_gi.python_reports_by_name
    python_reports_by_guid = report_objects_gi.python_reports_by_guid

except Exception, errexc:
    traceback.print_exc()
    print >> sys.stderr, "Failed to import!!"
    pdb.set_trace()

