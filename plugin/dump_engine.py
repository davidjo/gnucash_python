# junk script to dump the variables


import sw_engine

for clsitm in sw_engine.__dict__.keys():
    print(clsitm)

print()

for clsitm in vars(sw_engine):
    print(clsitm)
