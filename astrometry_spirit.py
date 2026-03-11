# #!/opt/anaconda3/envs/speculoos_py3/bin/python
# For server deployment, use:
#!/home/speculoos/Programs/anaconda2/envs/speculoos_py3/bin/python
# -*- coding: utf-8 -*-
"""
Revised on Feb 17 2026

@author: laetitia
@author: Seba Zuniga-Fernandez
"""

from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import sys
import os 
from astropy.io import fits


inlist = str(sys.argv[1])


def is_already_solved(filename):
    """
    Return True if the file already contains a sky WCS solution.

    A frame is considered solved when it has CTYPE1 starting with 'RA'
    together with at least one rotation matrix keyword (PCi_j or CDi_j).
    """
    try:
        with fits.open(filename, memmap=False) as hdul:
            h = hdul[0].header
            ctype1 = str(h.get('CTYPE1', '')).upper()
            has_sky_ctype = ctype1.startswith('RA') or ctype1.startswith('DEC')
            has_pc = any(k.startswith('PC') for k in h.keys())
            has_cd = any(k.startswith('CD') and not k.startswith('CDELT')
                         for k in h.keys())
            return has_sky_ctype and (has_pc or has_cd)
    except Exception:
        return False


def solve_astrometry(filenameold):
    #images have to be fits not fts (otherwise astrometry solving doesn't work)
    
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
        filename = filenameold

    # Skip solve-field if the frame already has a sky WCS (e.g. from Astra/PinPoint)
    if is_already_solved(filename):
        print("Already solved, skipping astrometry: " + os.path.basename(filename))
        return
    # Files with .fits extension or other extensions are left unchanged
#    filenameb=filename
#    with fits.open(filename) as infile_init:
#        if infile_init[0].header['IMAGETYP'] == 'Light Frame':
#            if infile_init[0].header['FILTER'][0] == 'u': #remove ' character from image name (otherwise astrometry solving doesn't work)
#                filenameb=filename[:-6]+'.fits'
#                os.rename(filename,filenameb)
#            if infile_init[0].header['FILTER'][0] == 'g':
#                filenameb=filename[:-6]+'.fits'
#                os.rename(filename,filenameb)
#            if infile_init[0].header['FILTER'][0] == 'r':
#                filenameb=filename[:-6]+'.fits'
#                os.rename(filename,filenameb)
#            if infile_init[0].header['FILTER'][0] == 'i':
#                filenameb=filename[:-6]+'.fits'
#                os.rename(filename,filenameb)
#            if infile_init[0].header['FILTER'][0] == 'z':
#                filenameb=filename[:-6]+'.fits'
#                os.rename(filename,filenameb)
#            RA = infile_init[0].header['RA']
#            str1 = str(RA.replace(" ", ":"))
#            DEC = infile_init[0].header['DEC']
#            str2 = str(DEC.replace(" ", ":"))
#            os.system("/usr/local/astrometry/bin/solve-field --no-plots --no-remove-lines --uniformize 0 --overwrite --ra " + str1 + " --dec " + str2 + " --radius 4 --depth 100 --downsample 2 --scale-low 0.2 --scale-units 'arcsecperpix' --no-tweak " + str(filenameb))
#            filenamebis=filenameb.replace('.fits','.new')
#            dum=filenameb.replace('.fits','-indx.xyls')
#            if os.path.exists(dum):
#                os.remove(dum)
#            dum=filenameb.replace('.fits','.axy')
#            if os.path.exists(dum):
#                os.remove(dum)
#            dum=filenameb.replace('.fits','.corr')
#            if os.path.exists(dum):
#                os.remove(dum)
#            dum=filenameb.replace('.fits','.match')
#            if os.path.exists(dum):
#                os.remove(dum)
#            dum=filenameb.replace('.fits','.rdls')
#            if os.path.exists(dum):
#                os.remove(dum)
#            dum=filenameb.replace('.fits','.solved')
#            if os.path.exists(dum):
#                os.remove(dum)
#            dum=filenameb.replace('.fits','.wcs')
#            if os.path.exists(dum):
#                os.remove(dum)
#            if os.path.exists(filenamebis):
#                if os.path.exists(filenameb):
#                    os.remove(filenameb)
#                os.rename(filenamebis,filenameb)


def astrometry():
    
    with open(inlist) as infile:
        filenames = [line.strip() for line in infile]

    # Parallelization
    pool = ThreadPool()
    fn = partial(solve_astrometry)        
    pool.map(fn, filenames)


if __name__ == '__main__':
    astrometry()
