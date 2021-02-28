import os
import obspy
from obspy import read
from obspy.signal.cross_correlation import xcorr_pick_correction
import matplotlib.pyplot as plt
import glob
import numpy as np
import pandas as pd
from wccfunction import *

def readcatalog(catalogfile):
    katalog = pd.ExcelFile(catalogfile)
    katalog = katalog.parse('sampel')
    katalog = katalog.replace('NaN', np.nan)
    katalog = katalog.replace(np.nan, 9999)  # to ease filtering blank S information
    return katalog

def pair(dtct):
    """
    make pair of event and station based on dt.ct

    """

    f = open(dtct)
    f = f.readlines()
    evpair, stpair, dt1, dt2, phase, dt = [], [], [], [], [], []
    for i in range(len(f)):
        if f[i][0] == '#':
            id1 = f[i].split()[1]
            id2 = f[i].split()[2]
            evpair.append([id1, id2])  # make event pair array
            j = 1
            st, ph = [], []
            while f[i + j][0] != '#' and i + j < len(f) - 1:  # make station pair array
                st.append(f[i + j].split()[0])
                dt1.append(f[i + j].split()[1])
                dt2.append(f[i + j].split()[2])
                ph.append(f[i + j].split()[4])
                j = j + 1
            # st = np.unique(st)
            stpair.append(st)
            dt.append([dt1, dt2])
            phase.append(ph)
    return(evpair,stpair,dt,phase)


def arrival_master(katalog, evpair, stpair, i, j):
    """
    read event information and then assign arrival p and s in obspy UTM format

    """

    tahun = 2020
    bulan = int(katalog['Bulan'][(katalog['ID'] == int(evpair[i][0])) & (katalog['Stasiun'] == stpair[i][j])])
    hari = int(katalog['Hari'][(katalog['ID'] == int(evpair[i][0])) & (katalog['Stasiun'] == stpair[i][j])])
    jam = int(katalog['Jam'][(katalog['ID'] == int(evpair[i][0])) & (katalog['Stasiun'] == stpair[i][j])])
    menitp = int(katalog['Menit'][(katalog['ID'] == int(evpair[i][0])) & (katalog['Stasiun'] == stpair[i][j])])
    menits = int(katalog['Menit S'][(katalog['ID'] == int(evpair[i][0])) & (katalog['Stasiun'] == stpair[i][j])])
    detikp = float(katalog['tp'][(katalog['ID'] == int(evpair[i][0])) & (katalog['Stasiun'] == stpair[i][j])])
    detiks = float(katalog['ts'][(katalog['ID'] == int(evpair[i][0])) & (katalog['Stasiun'] == stpair[i][j])])

    tp = obspy.UTCDateTime("{0}-{1}-{2}T{3}:{4}:{5}Z".format(tahun, bulan, hari, jam, menitp, detikp))
    if detiks != 9999:
        ts = obspy.UTCDateTime("{0}-{1}-{2}T{3}:{4}:{5}Z".format(tahun, bulan, hari, jam, int(menits), float(detiks)))
    else:
        ts = 9999
    return tp, ts


def arrival_pair(katalog, evpair, stpair, i, j):
    """
    read event information and then assign arrival p and s in obspy UTM format

    """

    tahun = 2020
    bulan = int(katalog['Bulan'][(katalog['ID'] == int(evpair[i][1])) & (katalog['Stasiun'] == stpair[i][j])])
    hari = int(katalog['Hari'][(katalog['ID'] == int(evpair[i][1])) & (katalog['Stasiun'] == stpair[i][j])])
    jam = int(katalog['Jam'][(katalog['ID'] == int(evpair[i][1])) & (katalog['Stasiun'] == stpair[i][j])])
    menitp = int(katalog['Menit'][(katalog['ID'] == int(evpair[i][1])) & (katalog['Stasiun'] == stpair[i][j])])
    menits = int(katalog['Menit S'][(katalog['ID'] == int(evpair[i][1])) & (katalog['Stasiun'] == stpair[i][j])])
    detikp = float(katalog['tp'][(katalog['ID'] == int(evpair[i][1])) & (katalog['Stasiun'] == stpair[i][j])])
    detiks = float(katalog['ts'][(katalog['ID'] == int(evpair[i][1])) & (katalog['Stasiun'] == stpair[i][j])])

    tp = obspy.UTCDateTime("{0}-{1}-{2}T{3}:{4}:{5}Z".format(tahun, bulan, hari, jam, menitp, detikp))
    if detiks != 9999:
        ts = obspy.UTCDateTime("{0}-{1}-{2}T{3}:{4}:{5}Z".format(tahun, bulan, hari, jam, int(menits), float(detiks)))
    else:
        ts = 9999
    return tp, ts


def waveform_z(evpair, stpair, i, j):
    """
    extract vertical-component waveform of master and pair event

    """

    stream1 = read("sample\\*{0}*\\*{1}*".format(evpair[i][0], stpair[i][j]))  # read event master waveform
    master = stream1.select(component="Z")[0]
    stream2 = read("sample\\*{0}*\\*{1}*".format(evpair[i][1], stpair[i][j]))  # read event pair waveform
    pair = stream2.select(component="Z")[0]
    return master, pair


def waveform_n(evpair, stpair, i, j):
    """
    extract horizontal-component waveform of master and pair event

    """

    stream1 = read("sample\\*{0}*\\*{1}*".format(evpair[i][0], stpair[i][j]))  # read event master waveform
    master = stream1.select(component="N")[0]
    stream2 = read("sample\\*{0}*\\*{1}*".format(evpair[i][1], stpair[i][j]))  # read event pair waveform
    pair = stream2.select(component="N")[0]
    return master, pair


def write_head(file,index,wcc):
    """
    write line consisting #, master ID, pair ID, and code

    """
    file.write('#' + ' ' + str(wcc['master'][index]) + ' ' + str(wcc['pair'][index]) +
              ' ' + '0.0' + '\n')

def write_content(file,index,wcc):
    """
    write line consisting station, lagtime, coefficient, and phase

    """
    file.write(wcc['station'][index] + ' ' + str(wcc['lagtime'][index]) + ' ' +
                   str(wcc['coefficient'][index]) + ' ' + wcc['phase'][index] + '\n')