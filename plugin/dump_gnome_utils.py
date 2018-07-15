# junk script to dump the variables


import sw_gnome_utils

for clsitm in sw_gnome_utils.__dict__.keys():
    print(clsitm)

print()

for clsitm in vars(sw_gnome_utils):
    print(clsitm)
