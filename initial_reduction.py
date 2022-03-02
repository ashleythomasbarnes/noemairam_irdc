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
inputdir = './../data'
outputdir = './../data_processed'
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
#lines = ['hcop_10', 'dcop_10', 'n2hp_10']
lines = ['dcn_10']

# Bad data
#array of badscans - check https://tapas.iram.es/
badscans = {'./../data/FTSOdp20220216.30m': [99,100],
            './../data/FTSOdp20220217.30m': [149,150],
            './../data/FTSOdp20220218.30m': [158,159,162],
            './../data/FTSOdp20220219.30m': []}

# Output velocity axis
# https://publicwiki.iram.es/Iram30mEfficiencies
beff = 0.8
nchans = 2000  #number of channels
chan0 = 0      #reference channel
chan0_v = 0    #velocity at reference channel
delta_v = 0.05 #delta velocity
####################################################








####################################################
####################################################
### Initial
# get the gildas command line interpreter to issue commands quickly
sic = pyclass.comm
# get the pyclass.gdict object for easy Gildas variable access
g = pyclass.gdict
# sic('SIC MESSAGE GLOBAL ON') # or OFF for less noise
###
for line in lines:

    print('[INFO] Reducing line: %s' %line)

    #Get frequency
    freq = freqs[line]*1e3

    ###Define output
    outputfile = '%s/%s_%s' %(outputdir, source, line)
    os.system('rm %s.*' %outputfile)
    sic('file out %s.30m s' %outputfile) #Do not use m here - m = multiple version in output, s = single, so s means you can not have two ids that are the same - e.g. if you merge files, a new ID is create instead of overwriting the old one. 
    print('[INFO] Removing old output file')
    print('[INFO] Making new output file: %s' %outputfile)
    ####

    ###Loop through files - one file per date
    for inputfile in inputfiles:
        
        #if inputfile != './../data/FTSOdp20220219.30m':
        #    continue

        # print(badscans[inputfile])
        
        try:
            badscan = badscans[inputfile]
            print('[INFO] Removing bad scans')
            baddata_ = True
        except:
            baddata_ = False #skipping if statement later
            print('[INFO] No bad data info')

        #Load file and det defaults
        sic('file in %s' %inputfile)
        sic('set source %s' %source)
        sic('set tele %s' %'*')
        sic('set line %s' %'*')

        #only take data in range of map - x1 x2 y1 y2
        sic('set range %s %s %s %s' %(-200, 200, '*', '*'))


        #Open and check file
        sic('find /frequency %s' %freq) #only obs with refrenecy
        if g.found == 0:
            #raise RuntimeError('No data found!')
            continue

        try:
            badscan = badscans[inputfile]
            baddata_ = True
        except:
            baddata_ = False #skipping if statement later
            print('[INFO] No bad data info')

        #Loop through spectral, baseline, and output
        inds = g.idx.ind
        sic('sic message class s-i') #! Speed-up long loops by avoiding too many screen informational messages

        for ind in console.ProgressBar(inds):

            sic('get %s' %ind)

            #skip bad data
            scan = g.scan
            if baddata_:
                if scan in badscan:
                    # print('[INFO] Skipping bad scan --> %i' %scan)
                    continue

            sic('modif freq %s' %freq)
            # sic('modify beam_eff %s' %beff) #set manually
            sic('modify beam_eff /ruze') #auto beff determine
            sic('set unit v')
            sic('extract -30 130 v') #cut out a small part of the spectra
            #sic('resample 2000 0 0 0.05 v')
            sic('resample %i %i %f %f v' %(nchans, chan0, chan0_v, delta_v))
            sic('set mo x 0 100') #only do baseline on this part
            #sic('plot')
            sic('set win 30 60')
            try:
                sic('base 1')
            except:
                print('[INFO] No basline fitted.')
                continue
            sic('write')
        sic('sic message class s+i') #! Toggle back screen informational messages

    # Save 30m file
    sic('file in %s.30m' %outputfile)
    
    ## Regrid and output to fits file
    #sic('find /all')
    #sic('table %s new /RESAMPLE %i %i %f %f velo /NOCHECK' %(outputfile, nchans, chan0, chan0_v, delta_v))
    ##sic('table %s new /RESAMPLE 2000 0 0 0.05 velo /NOCHECK' %outputfile)
    #sic('xy_map %s' %outputfile)
    #sic('vector\\fits %s.fits from %s.lmv' %(outputfile, outputfile))
    ###

