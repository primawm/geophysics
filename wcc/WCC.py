# Waveform Cross-Correlation program by Prima Widianto
# November 2020
# Correlate event pair based on dt.ct (HypoDD input data) and catalog information.
# Output : lag time, correlation coefficient
# Run using python 3
# Note: There's a little bit modification i did in the obspy xcorr_pick_correction library so that it can bypass
# the pair of event that doesn't have maximum value of correlation coefficient (this kind of event pair makes the
# program stops so i bypass it and i'd just give an information that this pair has an error in the output table)

from obspy.signal.cross_correlation import xcorr_pick_correction
import numpy as np
import pandas as pd
from wccfunction import *
import warnings
warnings.filterwarnings("ignore") #ignore warnings such as low coefficient value or lack of number of sample

# define input file
catalogfile = 'sample catalog.xlsx'
dtct = 'dt.ct'
low_bp = 1.5   # define bandpass filter boundary
high_bp = 15   # define bandpass filter boundary

# define output file
outputfile = 'wcc result.csv'

# read input file
katalog = readcatalog(catalogfile)       # read catalog
evpair, stpair, dt, phase = pair(dtct)   # read dt.ct to make an array of event pair and station pair

# preparing the variable
tp_master, ts_master, tp_pair, ts_pair, lagtime, coeff = [], [], [], [], [], []
station, event, fase, dtpair = [], [], [], []

# correlate waveform in each paired station of paired event
for i in range(len(evpair)):
    for j in range(len(stpair[i])):
        tp1, ts1 = arrival_master(katalog, evpair, stpair, i, j)
        tp2, ts2 = arrival_pair(katalog, evpair, stpair, i, j)
        tp_master.append(tp1), ts_master.append(ts1), tp_pair.append(tp2), ts_pair.append(ts2)

        if phase[i][j] == 'P':
            print('Correlating p-wave for event {0} and {1} ...'.format(evpair[i][0], evpair[i][1]))
            master, pair = waveform_z(evpair, stpair, i, j)
            lag, c = xcorr_pick_correction(tp1, master, tp2, pair, -0.05, 0.2, 0.2,
                                           filter="bandpass", filter_options={'freqmin': low_bp, 'freqmax': high_bp})

        else:
            if ts1 != 9999 and ts2 != 9999:
                print('Correlating s-wave for event {0} and {1} ...'.format(evpair[i][0], evpair[i][1]))
                master, pair = waveform_n(evpair, stpair, i, j)
                lag, c = xcorr_pick_correction(ts1, master, ts2, pair, -0.05, 0.2, 0.2,
                                               filter="bandpass", filter_options={'freqmin': low_bp, 'freqmax': high_bp})
            else:
                lag, c = np.nan, np.nan

        # assign the informations to an array
        station.append(stpair[i][j]), lagtime.append(lag)
        coeff.append(c), fase.append(phase[i][j])
        event.append([evpair[i][0], evpair[i][1]])
        dtpair.append([dt[i][0][j], dt[i][1][j]])
print('Done\n')

# make dataframe to tabulate data
print('Making data table ...')
df = pd.DataFrame({'master':[i[0] for i in event], 'pair':[i[1] for i in event],
                   'station':station,'lagtime':lagtime, 'coefficient':coeff,
                   'phase':fase, 'ttmaster':[i[0] for i in dtpair],
                   'ttpair':[i[1] for i in dtpair],
                   'dt':[float(i[1])-float(i[0]) for i in dtpair]})
print('Done\n')
df.to_csv(outputfile, index=False)
