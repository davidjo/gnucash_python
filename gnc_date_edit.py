

import gnc_date_edit_python

import gnc_date_edit_gnc

# think Ive figured out how can use the C version
# - just need to call gnc_date_edit_get_type which should
# register the GType

# switch between pure python implemenation (very partial)
# and C code - which isnt going to work because cant figure
# out how to access the type structure variables
if True:
    GncDateEdit = gnc_date_edit_python.GncDateEdit
else:
    GncDateEdit = gnc_date_edit_gnc.GncDateEdit
