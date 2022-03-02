## Source gildas installation - outside of python
# source /vol/software/software/astro/gildas/initgildas-nov18a.sh
## Add gildas installation to python path
# export PYTHONPATH=$PYTHONPATH:/vol/software/software/astro/gildas/gildas-exe-nov18a/x86_64-ubuntu18.04-gfortran/python
##

## Import  pygildas  modeules
import pygildas
import pyclass
##

## General imports
from glob import glob
import numpy as np
import os
import astropy.utils.console as console
##

####################################################
###### User inputs
# Dirs
inputdir = './../data_processed'
outputdir = './../figures/'
inputfiles = glob('%s/*.30m' %inputdir)

# Source
source = 'cloudh'

# Lines
freqs = {
        'dcop_10': 72.03931220,
        'dcn_10': 72.41703000,
        'hc3n_87': 72.7838220,
        'h2co_10': 72.83794800,
        'dnc_10': 76.30572700,
        'n2dp_10': 77.10924330,
        'hcn_10': 88.63160230,
        'hcop_10': 89.18852470,
        'n2hp_10': 93.17339770,
         }
lines = freqs.keys()

obs_dates = ['16-Feb-2022', '17-Feb-2022', '18-Feb-2022']

#####################################################

####################################################
####################################################
### Initial
# get the gildas command line interpreter to issue commands quickly
# sic = pyclass.comm
# get the pyclass.gdict object for easy Gildas variable access
# g = pyclass.gdict
# sic('SIC MESSAGE GLOBAL ON') # or OFF for less noise
###
for line in lines:

    inputfile = None
    for file in inputfiles:
        if line in file:
            inputfile = file
            continue

    if inputfile == None:
        continue

    print('[INFO] Making RMS plot for line: %s' %line)
    print(inputfile)

    #Get frequency
    freq = freqs[line]*1e3

    ###Define output
    outputfile = '%s/%s_%s' %(outputdir, source, line)
    os.system('rm %s.*' %outputfile)
    sic('file out %s.30m m' %outputfile)
    print('[INFO] Removing old output file')
    print('[INFO] Making new output file: %s' %outputfile)
    ####

    #Load file and det defaults
    sic('file in %s' %inputfile)
    sic('set source %s' %source)
    sic('set tele %s' %'*')
    sic('set line %s' %'*')
    sic('set nomatch')

    for obs_date in obs_dates:

        sic('set observed %s %s' %(obs_date,obs_date))
        sic('find')

        scans = g.idx.scan

        for scan in scans:

            sic('set scan %s %s' %(scan scan))
            sic('find')
            sic('ave /resample')
            sic('hardcopy %s/%s_%s_%s.pdf /device pdf \overwrite' %(outputfile, obs_date, scan))
