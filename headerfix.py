# #!/opt/anaconda3/envs/speculoos_py3/bin/python
# For server deployment, use:
#!/home/speculoos/Programs/anaconda2/envs/speculoos_py3/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 15:03:30 2018
Revised on Feb 17 2026

@author: laetitia
@author: Seba Zuniga-Fernandez
"""

from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.time import Time
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial

import math
import os 
import sys


inlist = str(sys.argv[1])

telescope = str(sys.argv[2]) #options are 'Io', 'Europa', 'Ganymede', 'Callisto'

# Optional third argument for custom programID
# If not provided, use default values based on telescope
if len(sys.argv) > 3:
    custom_program_id = str(sys.argv[3])
else:
    custom_program_id = None


def apply_correct(filename):
    
        # Default program IDs for each telescope
        default_program_ids = {
            'Io': '60.A-9009(A)',
            'Europa': '60.A-9009(B)',
            'Ganymede': '60.A-9009(C)',
            'Callisto': '60.A-9009(D)'
        }
        
        # Use custom program ID if provided, otherwise use default
        if custom_program_id is not None:
            program_id = custom_program_id
        else:
            program_id = default_program_ids.get(telescope, '60.A-9009(A)')
              
        with fits.open(filename, do_not_scale_image_data=True) as infile:    
        
            #PA computation (not a standard output of the astrometric solving)
            # Raw frames from Astra/PinPoint carry a PCi_j + CDELTi WCS convention.
            # We compute PA from that matrix and must NOT add CDi_j keywords,
            # which would create a forbidden mix of both WCS conventions.
            if infile[0].header['IMAGETYP'] == 'Light Frame':
                # Prefer PCi_j convention (written by Astra/PinPoint and astrometry.net)
                if 'PC1_1' in infile[0].header:
                    cdelt1 = float(infile[0].header.get('CDELT1', 1.0))
                    cdelt2 = float(infile[0].header.get('CDELT2', 1.0))
                    pc11 = infile[0].header['PC1_1'] * cdelt1
                    pc12 = infile[0].header['PC1_2'] * cdelt1
                    pc21 = infile[0].header['PC2_1'] * cdelt2
                    pc22 = infile[0].header['PC2_2'] * cdelt2
                    det = (pc11*pc22) - (pc12*pc21)
                    parity = 1. if det >= 0 else -1.
                    T = parity * pc11 + pc22
                    A = parity * pc21 - pc12
                    orient = 180 - math.degrees(math.atan2(A, T))
                    infile[0].header['PA'] = (orient, '[deg, 0-360 CCW] Position angle of plate')
                # Fall back to CDi_j convention (older solver output)
                elif 'CD1_1' in infile[0].header:
                    cd11 = infile[0].header['CD1_1']
                    cd12 = infile[0].header['CD1_2']
                    cd21 = infile[0].header['CD2_1']
                    cd22 = infile[0].header['CD2_2']
                    det = (cd11*cd22) - (cd12*cd21)
                    parity = 1. if det >= 0 else -1.
                    T = parity * cd11 + cd22
                    A = parity * cd21 - cd12
                    orient = 180 - math.degrees(math.atan2(A, T))
                    infile[0].header['PA'] = (orient, '[deg, 0-360 CCW] Position angle of plate')

            # WCS KWDs for bias, dark and flat frames as requested by ESO.
            # Use PCi_j + CDELTi convention (consistent with science frames from Astra).
            # CDi_j is intentionally NOT used to avoid mixing both conventions.
            if infile[0].header['IMAGETYP'] in ('Bias Frame', 'Dark Frame', 'FLAT', 'Flat Frame'):
                infile[0].header['WCSAXES'] = (2,   'Number of WCS axes')
                infile[0].header['CTYPE1']  = ('PIXEL', 'X-axis coordinate type')
                infile[0].header['CTYPE2']  = ('PIXEL', 'Y-axis coordinate type')
                infile[0].header['CRPIX1']  = (1.0, 'X-axis reference pixel')
                infile[0].header['CRPIX2']  = (1.0, 'Y-axis reference pixel')
                infile[0].header['CRVAL1']  = (1.0, 'X-axis coordinate value')
                infile[0].header['CRVAL2']  = (1.0, 'Y-axis coordinate value')
                infile[0].header['CDELT1']  = (1.0, 'X-axis scale [pixel]')
                infile[0].header['CDELT2']  = (1.0, 'Y-axis scale [pixel]')
                infile[0].header['PC1_1']   = (1.0, 'Transformation matrix element')
                infile[0].header['PC1_2']   = (0.0, 'Transformation matrix element')
                infile[0].header['PC2_1']   = (0.0, 'Transformation matrix element')
                infile[0].header['PC2_2']   = (1.0, 'Transformation matrix element')
                # Remove CDi_j keywords if they were carried over from a previous run
                for _kw in ('CD1_1', 'CD1_2', 'CD2_1', 'CD2_2'):
                    if _kw in infile[0].header:
                        infile[0].header.remove(_kw)
            
            #KWDs that are different for each telescope 
            #The classification based on the TELESCOP KWD does not work for calib images as the TELESCOP KWD is empty in this case, 
            #but this is not an issue as the script will be running independently for each telescope.
            #You just have to set correctly the telescope string at the top of the script for each telescope.
        
            #if infile[0].header['TELESCOP'] == 'Astra->IO' or infile[0].header['TELESCOP'] == 'Astra->Io' or infile[0].header['TELESCOP'] == 'Io':
            if telescope == 'Io':    
                infile[0].header['TELESCOP'] = 'SPECULOOS-IO'
                infile[0].header['INSTRUME'] = 'SPECULOOS1'
                infile[0].header['HIERARCH ESO INS NAME'] = ('SPECULOOS1','Instrument name')
                infile[0].header['HIERARCH ESO OBS PROG ID'] = (program_id,'ESO program identification')
            #if infile[0].header['TELESCOP'] == 'Astra->EUROPA' or infile[0].header['TELESCOP'] == 'Astra->Europa' or infile[0].header['TELESCOP'] == 'Europa':
            if telescope == 'Europa':
                infile[0].header['TELESCOP'] = 'SPECULOOS-EUROPA'
                infile[0].header['INSTRUME'] = 'SPECULOOS2'
                infile[0].header['HIERARCH ESO INS NAME'] = ('SPECULOOS2','Instrument name')
                infile[0].header['HIERARCH ESO OBS PROG ID'] = (program_id,'ESO program identification')
            #if infile[0].header['TELESCOP'] == 'Astra->GANYMEDE' or infile[0].header['TELESCOP'] == 'Astra->Ganymede' or infile[0].header['TELESCOP'] == 'Ganymede':
            if telescope == 'Ganymede':
                infile[0].header['TELESCOP'] = 'SPECULOOS-GANYMEDE' 
                infile[0].header['INSTRUME'] = 'SPECULOOS3'
                infile[0].header['HIERARCH ESO INS NAME'] = ('SPECULOOS3','Instrument name')
                infile[0].header['HIERARCH ESO OBS PROG ID'] = (program_id,'ESO program identification')
            #if infile[0].header['TELESCOP'] == 'Astra->CALLISTO' or infile[0].header['TELESCOP'] == 'Astra->Callisto' or infile[0].header['TELESCOP'] == 'Callisto':
            if telescope == 'Callisto':
                infile[0].header['TELESCOP'] = 'SPECULOOS-CALLISTO'
                infile[0].header['INSTRUME'] = 'SPECULOOS4'
                infile[0].header['HIERARCH ESO INS NAME'] = ('SPECULOOS4','Instrument name')
                infile[0].header['HIERARCH ESO OBS PROG ID'] = (program_id,'ESO program identification')
        
            #KWDs that do not depend on the telescope used
        
            if infile[0].header['IMAGETYP'] == 'Light Frame':
                infile[0].header['HIERARCH ESO DPR CATG'] = ('SCIENCE',' Observation category')
                infile[0].header['HIERARCH ESO DPR TYPE'] = ('OBJECT',' Observation type')
                infile[0].header['HIERARCH ESO DPR TECH'] = ('IMAGE',' Observation technique')
            if infile[0].header['IMAGETYP'] == 'Bias Frame':
                infile[0].header['HIERARCH ESO DPR CATG'] = ('CALIB',' Observation category')
                infile[0].header['HIERARCH ESO DPR TYPE'] = ('BIAS',' Observation type')
                infile[0].header['HIERARCH ESO DPR TECH'] = ('IMAGE',' Observation technique') 
            if infile[0].header['IMAGETYP'] == 'Dark Frame':
                infile[0].header['HIERARCH ESO DPR CATG'] = ('CALIB',' Observation category')
                infile[0].header['HIERARCH ESO DPR TYPE'] = ('DARK',' Observation type')
                infile[0].header['HIERARCH ESO DPR TECH'] = ('IMAGE',' Observation technique') 
            if infile[0].header['IMAGETYP'] == 'FLAT' or infile[0].header['IMAGETYP'] == 'Flat Frame':
                infile[0].header['HIERARCH ESO DPR CATG'] = ('CALIB',' Observation category')
                infile[0].header['HIERARCH ESO DPR TYPE'] = ('FLAT',' Observation type')
                infile[0].header['HIERARCH ESO DPR TECH'] = ('IMAGE',' Observation technique')  
            
            if infile[0].header['IMAGETYP'] == 'Light Frame':
                #doing 3 times try/except to mitigate the fact that the current angle parsing code is not thread safe
                try:
                    #c = SkyCoord(ra=infile[0].header['RA'], dec=infile[0].header['DEC'], unit=(u.hourangle, u.deg), frame='fk5')
                    c = SkyCoord(ra=infile[0].header['RA'], dec=infile[0].header['DEC'], unit=(u.deg, u.deg), frame='fk5')
                except Exception as e1:
                    print(e1)
                    try:
                        #c = SkyCoord(ra=infile[0].header['RA'], dec=infile[0].header['DEC'], unit=(u.hourangle, u.deg), frame='fk5')
                        c = SkyCoord(ra=infile[0].header['RA'], dec=infile[0].header['DEC'], unit=(u.deg, u.deg), frame='fk5')
                    except Exception as e2:
                        print(e2)
                        try:
                            #c = SkyCoord(ra=infile[0].header['RA'], dec=infile[0].header['DEC'], unit=(u.hourangle, u.deg), frame='fk5')
                            c = SkyCoord(ra=infile[0].header['RA'], dec=infile[0].header['DEC'], unit=(u.deg, u.deg), frame='fk5')
                        except Exception as e3:
                            print(e3)
                infile[0].header['RA']=(float('%.*f' % (5, c.ra.degree)),'[deg] Target right ascension')
                infile[0].header['DEC']=(float('%.*f' % (5, c.dec.degree)),'[deg] Target declination')    
        
        
            infile[0].header['ORIGIN'] = ('SSO-PARANAL','SPECULOOS-South')
             
            if 'RADECSYS' in infile[0].header:
                infile[0].header['RADESYS'] = (infile[0].header['RADECSYS'],'Equatorial coordinate system')
                infile[0].header.remove('RADECSYS')
        
            if 'EPOCH' in infile[0].header:
                infile[0].header.remove('EPOCH')
        
            infile[0].header['BUNIT'] = ('adu','Physical unit of array values')
        
            if 'ST' in infile[0].header:
                infile[0].header.remove('ST') #ST is not correct
            dateobs=infile[0].header['DATE-OBS']
            t=Time(dateobs, format='isot', scale='utc')
            t.delta_ut1_utc = 0
            lstsec=((t.sidereal_time('apparent',-70.4028*u.degree).hour)*60)  #Paranal longitude
            infile[0].header['LST']=(float('%.*f' % (3, lstsec)),'LST at start [sec]')
        
            year=t.datetime.year
            month=t.datetime.month
            day=t.datetime.day
            hour=t.datetime.hour
            minute=t.datetime.minute
            second=t.datetime.second
            microsecond=t.datetime.microsecond
            if microsecond == 0:
                infile[0].header['DATE-OBS'] = (t.isot,'UTC date/time of exposure start')
            utcsec=int(hour)*3600 + int(minute)*60 + int(second) + int(microsecond)/1E6
            infile[0].header['UTC']=(float('%.*f' % (8, utcsec)),'UTC at start [sec]')
             
            mjd=t.mjd
            infile[0].header['MJD-OBS'] = (float('%.*f' % (8, mjd)),'Modified Julian Date of start of exposure')
        
            exp=infile[0].header['EXPTIME']
            mjdend=mjd+(exp/86400)
            infile[0].header['MJD-END'] = (float('%.*f' % (8, mjdend)),'Modified Julian Date of end of exposure') 
        
            t2=Time(mjdend, format='mjd', scale='utc')
            infile[0].header['DATE-END'] = (t2.isot,'UTC date/time of end of exposure')
            infile[0].header['DATE'] = (t2.isot,'UTC date/time when this file was written')
        
            #Remove unnecessary KWDs
            if '_CSAXES' in infile[0].header:
                infile[0].header.remove('_CSAXES')
            if '_UNIT1' in infile[0].header:
                infile[0].header.remove('_UNIT1')
            if '_UNIT2' in infile[0].header:
                infile[0].header.remove('_UNIT2')
            if 'CDELT1' in infile[0].header:
                infile[0].header.remove('CDELT1')
            if 'CROTA1' in infile[0].header:    
                infile[0].header.remove('CROTA1')
            if 'CDELT2' in infile[0].header: 
                infile[0].header.remove('CDELT2')
            if 'CROTA2' in infile[0].header:                 
                infile[0].header.remove('CROTA2')
            while ('COMMENT' in infile[0].header):                 
                infile[0].header.remove('COMMENT')
            while ('HISTORY' in infile[0].header):                 
                infile[0].header.remove('HISTORY')
            if '_QUINOX' in infile[0].header:                 
                infile[0].header.remove('_QUINOX')
            if '_TYPE1' in infile[0].header:     
                infile[0].header.remove('_TYPE1')
            if '_RVAL1' in infile[0].header:                 
                infile[0].header.remove('_RVAL1')
            if '_RPIX1' in infile[0].header:                 
                infile[0].header.remove('_RPIX1')
            if '_DELT1' in infile[0].header:                 
                infile[0].header.remove('_DELT1')
            if '_ROTA1' in infile[0].header:                 
                infile[0].header.remove('_ROTA1')
            if '_TYPE2' in infile[0].header:                 
                infile[0].header.remove('_TYPE2')
            if '_RVAL2' in infile[0].header:                 
                infile[0].header.remove('_RVAL2')
            if '_RPIX2' in infile[0].header:                 
                infile[0].header.remove('_RPIX2')
            if '_DELT2' in infile[0].header:                 
                infile[0].header.remove('_DELT2')
            if '_ROTA2' in infile[0].header:                 
                infile[0].header.remove('_ROTA2')
            if '_D1_1' in infile[0].header:                 
                infile[0].header.remove('_D1_1')
            if '_D1_2' in infile[0].header:                 
                infile[0].header.remove('_D1_2')
            if '_D2_1' in infile[0].header:                 
                infile[0].header.remove('_D2_1')
            if '_D2_2' in infile[0].header:                 
                infile[0].header.remove('_D2_2')
            if 'TR1_0' in infile[0].header:                 
                infile[0].header.remove('TR1_0')
            if 'TR1_1' in infile[0].header:                 
                infile[0].header.remove('TR1_1')
            if 'TR1_2' in infile[0].header:     
                infile[0].header.remove('TR1_2')
            if 'TR1_3' in infile[0].header:                 
                infile[0].header.remove('TR1_3')
            if 'TR1_4' in infile[0].header:                 
                infile[0].header.remove('TR1_4')
            if 'TR1_5' in infile[0].header:                 
                infile[0].header.remove('TR1_5')
            if 'TR1_6' in infile[0].header:                 
                infile[0].header.remove('TR1_6')
            if 'TR1_7' in infile[0].header:                 
                infile[0].header.remove('TR1_7')
            if 'TR1_8' in infile[0].header:                 
                infile[0].header.remove('TR1_8')
            if 'TR1_9' in infile[0].header:                 
                infile[0].header.remove('TR1_9')
            if 'TR1_10' in infile[0].header:                 
                infile[0].header.remove('TR1_10')
            if 'TR1_11' in infile[0].header:                 
                infile[0].header.remove('TR1_11')
            if 'TR1_12' in infile[0].header:             
                infile[0].header.remove('TR1_12')
            if 'TR1_13' in infile[0].header:                 
                infile[0].header.remove('TR1_13')
            if 'TR1_14' in infile[0].header:                 
                infile[0].header.remove('TR1_14')
            if 'TR2_0' in infile[0].header:                 
                infile[0].header.remove('TR2_0')
            if 'TR2_1' in infile[0].header:                 
                infile[0].header.remove('TR2_1')
            if 'TR2_2' in infile[0].header:                 
                infile[0].header.remove('TR2_2')
            if 'TR2_3' in infile[0].header:                 
                infile[0].header.remove('TR2_3')
            if 'TR2_4' in infile[0].header:                 
                infile[0].header.remove('TR2_4')
            if 'TR2_5' in infile[0].header:                 
                infile[0].header.remove('TR2_5')
            if 'TR2_6' in infile[0].header:                
                infile[0].header.remove('TR2_6')
            if 'TR2_7' in infile[0].header:                 
                infile[0].header.remove('TR2_7')
            if 'TR2_8' in infile[0].header:                 
                infile[0].header.remove('TR2_8')
            if 'TR2_9' in infile[0].header:                 
                infile[0].header.remove('TR2_9')
            if 'TR2_10' in infile[0].header:                 
                infile[0].header.remove('TR2_10')
            if 'TR2_11' in infile[0].header:                 
                infile[0].header.remove('TR2_11')
            if 'TR2_12' in infile[0].header:                 
                infile[0].header.remove('TR2_12')
            if 'TR2_13' in infile[0].header:                
                infile[0].header.remove('TR2_13')
            if 'TR2_14' in infile[0].header:                
                infile[0].header.remove('TR2_14')
            if '_ATE' in infile[0].header:                 
                infile[0].header.remove('_ATE')
            if 'SWOWNER' in infile[0].header:                 
                infile[0].header.remove('SWOWNER')
            if 'PLTSOLVD' in infile[0].header:                 
                infile[0].header.remove('PLTSOLVD')
            if 'IRAF-TLM' in infile[0].header:     
                infile[0].header.remove('IRAF-TLM')
        
            #Write the new header + image in a new file
        
            path = os.path.dirname(os.path.abspath(filename))
            instrument = infile[0].header['INSTRUME']
            part1 = path + '/' + instrument + '.' + str(year) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2)
            part2 = str(hour).zfill(2) + '_' + str(minute).zfill(2) + '_' + str(second).zfill(2) + '.' + str(int(microsecond)/int(1E3)).zfill(3) + '.fits'
            outfile = part1 + 'T' + part2
            if os.path.exists(outfile):
                os.remove(outfile)
            infile.writeto(outfile)
            
            #Delete the old file
            
            os.remove(filename)

def headerfix():
    
    with open(inlist) as infile:
        filenames = [line.strip() for line in infile]

    pool = ThreadPool()
    fn = partial(apply_correct)        
    pool.map(fn, filenames)

if __name__ == '__main__':
    headerfix()
    
    
