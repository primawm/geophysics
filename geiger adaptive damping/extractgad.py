# Code to extract the output of Geiger Adaptive Damping
# By Prima Widianto

import os
from os import listdir
import pandas as pd
import numpy as np
import utm

def to_lonlat(utmx, utmy):
    '''
    convert dataframe from utm to lonlat
    :param lon:
    :param lat:
    :param depth:
    :return:
    '''

    lon = np.zeros(len(utmx))
    lat = np.zeros(len(utmy))

    for i in range(len(utmx)):
        lon[i],lat[i] = utm.to_latlon(utmx[i], utmy[i], 47, 'N') # change this into your UTM area
    return lon, lat

fileinput = "Results.dat"
fileoutput = 'hipogad.csv'          # main output file
fileoutput2 = 'eventproblem.csv'       # to check problematic event
file = open(fileinput,'r')
baris = file.readlines()
file.close()

# define center point of your field in UTM
centery = 204714    #NIL9
centerx = 505618

x, y, depth, rms, date, tahun1, bulan1, tanggal1, jam1, menit1 = [], [], [], [], [], [], [], [], [], []
tahun, bulan, tanggal, jam, menit, detik = [], [], [], [], [], []
do = 'yes'
for i in range(len(baris)-4):
    if len(baris[i].split()) > 1:
        a = baris[i].split()
        b = baris[i+1].split()
        c = baris[i+4].split()
        t = baris[i+3].split()

        if a[0]=="X":
            d = baris[i - 2]
            if a[1]=="*******" or b[1]=="*******" or c[3][4:8] == "****":
                tahun1.append(d[7:9]), tahun.append(d[7:9])
                bulan1.append(d[10:12]), bulan.append(d[10:12])
                tanggal1.append(d[13:15]), tanggal.append(d[13:15])
                jam1.append(d[23:25]), jam.append(d[23:25])
                menit1.append(d[26:28]), menit.append(d[26:28])
                detik.append(t[1])
                x.append('NaN')
                y.append('NaN')
                depth.append('NaN')
                rms.append('NaN')
                do = 'nothing'
            else:
                x.append(float(a[1])*1000+centerx)
                tahun.append(d[7:9])
                bulan.append(d[10:12])
                tanggal.append(d[13:15])
                jam.append(d[23:25])
                menit.append(d[26:28])
                detik.append(t[1])


        if a[0]=='Y':
            if do == 'nothing':
                do = 'nothing'
            else:
                if a[1]=="*******":
                    do = 'nothing'
                    x.append('NaN')
                    y.append('NaN')
                    depth.append('NaN')
                    rms.append('NaN')
                else:
                    y.append(float(a[1])*1000+centery)

        if a[0]=='Z':
            if do == 'nothing':
                do = 'nothing'
            else:
                if a[1] == "*******":
                    x.append('NaN')
                    y.append('NaN')
                    depth.append('NaN')
                    rms.append('NaN')
                else:
                    depth.append(float(a[1]))
        if a[0]=='Travel':
            if do == 'nothing':
                do = 'yes'
            else:
                if a[3][4:8] == "****":
                    do = 'yes'
                    x.append('NaN')
                    y.append('NaN')
                    depth.append('NaN')
                    rms.append('NaN')
                else:

                    if len(a[3])>8:
                        rms.append(float(a[3][4:8]))
                    else:
                        rms.append(float(a[4][:-4]))

lat, lon = [], []
for i in range(len(x)):
    if x[i] == 'NaN':
        lat.append('NaN'), lon.append('NaN')
    else:
        utmx, utmy = utm.to_latlon(x[i], y[i], 47, 'N')
        lat.append(utmy), lon.append(utmx)

# lat, lon = to_lonlat(x,y)
gad = {'Lon':lon,'Lat':lat,'Depth (km)':depth, 'RMS':rms, 'tahun':tahun, 'bulan':bulan,
       'tanggal':tanggal, 'jam':jam, 'menit':menit, 'detik':detik
       }
problem = {'tahun':tahun1, 'bulan':bulan1, 'tanggal':tanggal1, 'jam':jam1, 'menit':menit1}


# Write the output file
ekstrak = pd.DataFrame(gad)
ekstrak.to_csv(fileoutput, index=False)
masalah = pd.DataFrame(problem)
masalah.to_csv(fileoutput2, index=False)