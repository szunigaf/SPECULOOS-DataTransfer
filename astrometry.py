
# #!/opt/anaconda3/envs/speculoos_py3/bin/python
# For server deployment, use:
#!/home/speculoos/Programs/anaconda2/envs/speculoos_py3/bin/python
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
import shutil
from astropy.io import fits

#inlist = 'infiles.dat'
inlist = str(sys.argv[1])

# Check if solve-field is available
SOLVE_FIELD_PATH = shutil.which('solve-field')
if SOLVE_FIELD_PATH is None:
    # Try common installation paths
    common_paths = [
        '/usr/local/astrometry/bin/solve-field',
        '/usr/bin/solve-field',
        '/opt/astrometry/bin/solve-field'
    ]
    for path in common_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            SOLVE_FIELD_PATH = path
            break

if SOLVE_FIELD_PATH is None:
    print("WARNING: solve-field command not found!")
    print("Astrometry.net may not be installed or not in PATH.")
    print("The script will only rename .fts files to .fits without solving astrometry.")
    print("To install astrometry.net, visit: http://astrometry.net/")
    ASTROMETRY_AVAILABLE = False
else:
    print("Found solve-field at: " + SOLVE_FIELD_PATH)
    ASTROMETRY_AVAILABLE = True


def is_already_solved(filename):
    """
    Return True if the file already contains a sky WCS solution.

    A frame is considered solved when it has CTYPE1 starting with 'RA'
    together with at least one rotation matrix keyword (PCi_j or CDi_j).
    This covers both the PCi_j convention (written by Astra/PinPoint and
    astrometry.net) and the older CDi_j convention.
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

    # Skip solve-field if the frame already has a sky WCS (e.g. from Astra/PinPoint)
    if is_already_solved(filename):
        print("Already solved, skipping astrometry: " + os.path.basename(filename))
        return
    
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
                
                # Get RA and DEC, handle both string and numeric formats
                RA = infile_init[0].header['RA']
                DEC = infile_init[0].header['DEC']
                
                # Convert to string format expected by solve-field
                if isinstance(RA, str):
                    str1 = str(RA.replace(" ", ":"))
                else:
                    # RA is already in degrees (float)
                    str1 = str(RA)
                
                if isinstance(DEC, str):
                    str2 = str(DEC.replace(" ", ":"))
                else:
                    # DEC is already in degrees (float)
                    str2 = str(DEC)
                
                # Run astrometry solver only if available
                if ASTROMETRY_AVAILABLE:
                    cmd = SOLVE_FIELD_PATH + " --no-plots --no-remove-lines --uniformize 0 --overwrite --ra " + str1 + " --dec " + str2 + " --radius 4 --depth 100 --downsample 2 --no-tweak " + str(filenameb)
                    result = os.system(cmd)
                    
                    if result != 0:
                        print("Warning: Astrometry solving failed for " + filenameb)
                else:
                    print("Skipping astrometry solving for " + filenameb + " (solve-field not available)")
                
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
