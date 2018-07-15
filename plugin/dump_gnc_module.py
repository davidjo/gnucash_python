# junk script to dump the variables


import sw_gnc_module

for clsitm in sw_gnc_module.__dict__.keys():
    print(clsitm)

print()

for clsitm in vars(sw_gnc_module):
    print(clsitm)
