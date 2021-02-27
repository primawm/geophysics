# Code to write input file for Geiger Adaptive Damping software
# By Prima Widianto

import os
import pandas as pd
from os import listdir

def remove_at(e,s):
    return s[:e] + s[e+2:]

fileinput = 'catalog.csv' # catalog information
fileoutput = 'arrival.dat' # output
fileoutput = open(fileoutput,'w')
file = open(fileinput,'r')
baris = file.readlines()
file.close()
dummy = 1
line_split=[]

for i in range(1,len(baris)):
    baris[i].split(' ')
    a = baris[i].split(",",10)
    id = int(a[0])
    stasiun = remove_at(1,a[1])
    tgl = a[2].split("/",3)
    tahun = tgl[2][2:4]
    bulan = "{0:0=2d}".format(int(tgl[0]))
    hari = "{0:0=2d}".format(int(tgl[1]))
    jam = "{0:0=2d}".format(int(a[3]))
    menit = "{0:0=2d}".format(int(a[4]))
    tp = float(a[5])
    if a[6]!='NaN':
        ts = float(a[6])
        tstp = a[7]
        ws = a[9]
        if ts<tp:
            ts = ts-60

    else:
        ts = 99.990
        ws = "I"
    ts = (('%.3f') % ts).zfill(6)
    tp = (('%.3f') % tp).zfill(6)
    if id>dummy:
        tahun = str("\n"+tahun)
        dummy = id

    wp = a[8]
    motion = a[10][0:1]

    fileoutput.write(
        tahun + bulan + hari + jam + menit + ',' + stasiun + ',' + str(tp) + ',' + motion
        + ',' + wp + ',' + str(ts) + ',' + ws + '\n'
    )

    print('working on event {}'.format(id))

print('done')
fileoutput.write("\n"+"9999999999"+'\n')
fileoutput.close()