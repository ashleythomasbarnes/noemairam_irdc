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
##

### Initial
# get the gildas command line interpreter to issue commands quickly
sic = pyclass.comm
# get the pyclass.gdict object for easy Gildas variable access
g = pyclass.gdict
# sic('SIC MESSAGE GLOBAL ON') # or OFF for less noise
###

###
inputdir = './../data/'
inputfiles = glob('%s/*.30m' %inputdir)

source = 'cloudh'
freqs = {
        'dcn_10':72.41703000,
        'hc3n_87': 72.7838220,
        'h2co_10': 72.83794800,
        'dnc_10': 76.30572700,
        'n2dp_10': 77.10924330,
        'hcn_10': 88.63160230,
        'hcop_10': 89.18852470,
        'n2hp_10': 93.17339770,
         }

lines = freqs.keys()

# https://publicwiki.iram.es/Iram30mEfficiencies
beff = 0.81

lines = ['hcop_10']
for line in lines:

    print('[INFO] Reducing line: %s' %line)

    #Get frequency
    freq = freqs[line]

    ###Define output
    outputfile = './../data_processed/%s_%s' %(source, line)
    os.system('rm %s.*' %outputfile)
    sic('file out %s.30m m' %outputfile)
    print('[INFO] Removing old output file')
    print('[INFO] Making new output file: %s' %outputfile)
    ####

    ###Loop through files - one file per date
    for inputfile in inputfiles:

        #Load file and det defaults
        sic('file in %s' %inputfile)
        sic('set source %s' %source)
        sic('set tele %s' %'*')
        sic('set line %s' %'*')

        #only take data in range of map - x1 x2 y1 y2
        sic('set range %s %s %s %s' %(-200, 200, '*', '*'))

        #only take good data
        # scan <101 have bad offset
        sic('set scan %s %s' %(101, '*'))

        #Open and check file
        sic('find /frequency %s' %freq) #only obs with refrenecy - in MHz
        if g.found == 0:
            #raise RuntimeError('No data found!')
            continue

        #Loop through spectral, baseline, and output
        inds = g.idx.ind
        sic('sic message class s-i') #! Speed-up long loops by avoiding too many screen informational messages
        for ind in inds:
            sic('get %s' %ind)
            sic('modif freq %s' %freq)
            # sic('@set_apex_beam_efficiency %s' %beff)
            sic('modify beam_eff %s' %beff)
            sic('set unit v')
            sic('extract -10 110 v') #cut out a small part of the spectra
            sic('set mo x 0 100') #only do baseline on this part
            #sic('plot')
            sic('set win 30 60')
            try:
                sic('base 1')
            except:
                continue
            sic('write')
        sic('sic message class s+i') #! Toggle back screen informational messages


    ###Regrid and output to fits file
    sic('file in %s.apex' %outputfile)
    sic('find /all')
    sic('table %s new /RESAMPLE 2000 0 0 0.05 velo /NOCHECK' %outputfile)
    sic('xy_map %s' %outputfile)
    sic('vector\\fits %s.fits from %s.lmv' %(outputfile, outputfile))
    ###
