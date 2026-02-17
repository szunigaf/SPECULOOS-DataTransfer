#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 10:47:51 2018
Revised on Feb 17 2026

@author: laetitia
@author: Seba Zuniga-Fernandez
"""

from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import sys
import os 
from astropy.io import fits

#inlist = 'infiles.dat'
inlist = str(sys.argv[1])


def solve_astrometry(filenameold):
    #images have to be fits not fts (otherwise astrometry not working)
    
    # Check if file exists first
    if not os.path.exists(filenameold):
        print("Warning: File not found: " + filenameold)
        return
    
    # Only rename if it has .fts extension
    if filenameold.endswith('.fts'):
        filename = filenameold.replace('.fts', '.fits')
        try:
            os.rename(filenameold, filename)
            print("Renamed: " + filenameold + " -> " + filename)
        except OSError as e:
            print("Error renaming file " + filenameold + ": " + str(e))
            return
    else:
        # File already has .fits extension or other extension
        filename = filenameold
    
    filenameb=filename
    try:
        with fits.open(filename) as infile_init:                
            if infile_init[0].header['IMAGETYP'] == 'Light Frame':
                if infile_init[0].header['FILTER'][0] == 'u':
                    filenameb=filename[:-6]+'.fits'
                    os.rename(filename,filenameb)
                if infile_init[0].header['FILTER'][0] == 'g':
                    filenameb=filename[:-6]+'.fits'
                    os.rename(filename,filenameb)
                if infile_init[0].header['FILTER'][0] == 'r':
                    filenameb=filename[:-6]+'.fits'
                    os.rename(filename,filenameb)
                if infile_init[0].header['FILTER'][0] == 'i':
                    filenameb=filename[:-6]+'.fits'
                    os.rename(filename,filenameb)
                if infile_init[0].header['FILTER'][0] == 'z':
                    filenameb=filename[:-6]+'.fits'
                    os.rename(filename,filenameb)
                RA = infile_init[0].header['RA']
                str1 = str(RA.replace(" ", ":"))
                DEC = infile_init[0].header['DEC']
                str2 = str(DEC.replace(" ", ":"))
                
                # Run astrometry solver
                cmd = "/usr/local/astrometry/bin/solve-field --no-plots --no-remove-lines --uniformize 0 --overwrite --ra " + str1 + " --dec " + str2 + " --radius 4 --depth 100 --downsample 2 --no-tweak " + str(filenameb)
                result = os.system(cmd)
                
                if result != 0:
                    print("Warning: Astrometry solving failed for " + filenameb)
                
                filenamebis=filenameb.replace('.fits','.new')
                
                # Clean up temporary files
                dum=filenameb.replace('.fits','-indx.xyls')
                if os.path.exists(dum):
                    os.remove(dum)
                dum=filenameb.replace('.fits','.axy')
                if os.path.exists(dum):
                    os.remove(dum)
                dum=filenameb.replace('.fits','.corr')
                if os.path.exists(dum):
                    os.remove(dum) 
                dum=filenameb.replace('.fits','.match')
                if os.path.exists(dum):
                    os.remove(dum)
                dum=filenameb.replace('.fits','.rdls')
                if os.path.exists(dum):
                    os.remove(dum)
                dum=filenameb.replace('.fits','.solved')
                if os.path.exists(dum):
                    os.remove(dum)
                dum=filenameb.replace('.fits','.wcs')
                if os.path.exists(dum):
                    os.remove(dum)
                
                # Replace original with solved version if it exists
                if os.path.exists(filenamebis):
                    if os.path.exists(filenameb):
                        os.remove(filenameb)
                    os.rename(filenamebis,filenameb)
                    print("Astrometry solved: " + filenameb)
    except Exception as e:
        print("Error processing file " + filename + ": " + str(e))


def astrometry():
    
    with open(inlist) as infile:
        filenames = [line.strip() for line in infile]

    pool = ThreadPool()
    fn = partial(solve_astrometry)        
    pool.map(fn, filenames)


if __name__ == '__main__':
    astrometry()
