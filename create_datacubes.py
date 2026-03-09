#!/home/speculoos/Programs/anaconda2/envs/speculoos_py3/bin/python
# -*- coding: utf-8 -*-
"""
create_datacubes.py — SPECULOOS Datacube Creator
=================================================

Stacks individual FITS images from a SPECULOOS telescope night into 3D
datacubes (frame, y, x), organized by observation type and grouped by
the relevant header metadata.

Grouping rules
--------------
    Science frames  : target (OBJECT) + filter (FILTER) + exposure time (EXPTIME)
    Flat frames     : filter (FILTER) + exposure time (EXPTIME)
    Dark frames     : exposure time (EXPTIME)
    Bias frames     : all together in one cube

One datacube is produced per unique group. The output filename uses a compact
format aligned with the ESO archive SPECU# convention:

    {SPECU#}.{YYYYMMDD}T{HHMMSS}_{S|C}_{group_key}.fits

    where S = Science, C = Calibration (Flat/Dark/Bias)

    Example:
        SPECU2.20260223T014741_S_TIC46432937b_i_20s.fits
        SPECU2.20260223T014741_C_flat_i_5s.fits
        SPECU2.20260223T014741_C_dark_300s.fits
        SPECU2.20260223T014741_C_bias.fits

This keeps filenames short enough so that ORIGFILE FITS keyword records
(max 80 characters) are never truncated by the ESO science archive ingestion.

If INSTRUME is absent from the header (e.g. raw files before headerfix.py),
a simplified name is used: S_{group_key}.fits / C_{group_key}.fits

Output file structure
---------------------
Each output FITS file contains two extensions:

    [0] PRIMARY   3D float32 array of shape (N_frames, N_y, N_x)
                  Header includes all keywords from the first frame plus:
                    NFRAMES   Number of frames stacked
                    CUBETYPE  Frame type (SCIENCE, BIAS, DARK, FLAT)
                    CUBEKEY   Grouping key used to build this cube
                    CREATED   Datacube creation timestamp

    [1] METADATA  Binary table with one row per frame:
                    FILENAME  Original filename
                    DATE-OBS  Observation timestamp
                    EXPTIME   Exposure time (s)
                    FILTER    Filter name
                    OBJECT    Target name
                    AIRMASS   Airmass at observation

Header compatibility
--------------------
The script supports both:
  - Raw ACP files     : classified via IMAGETYP keyword
                        (Light Frame, Bias Frame, Dark Frame, Flat Frame / FLAT)
  - ESO-processed files: classified via HIERARCH ESO DPR CATG / TYPE keywords
                        (SCIENCE/OBJECT, CALIB/BIAS, CALIB/DARK, CALIB/FLAT)
ESO keywords take priority if both are present.

Usage
-----
    python create_datacubes.py <input_directory> [output_directory]

    input_directory   Directory containing FITS files (searched recursively)
    output_directory  Where datacubes are saved (default: ./datacubes)

Dependencies
------------
    astropy >= 5.0
    numpy >= 1.20

Created on Feb 17 2026
Revised on Mar 06 2026

@author: Seba Zuniga-Fernandez
"""

from astropy.io import fits
from astropy.table import Table
from astropy.time import Time
import astropy.units as u
import numpy as np
import os
import sys
from collections import defaultdict
from datetime import datetime
import warnings

warnings.filterwarnings('ignore', category=fits.verify.VerifyWarning)



def get_image_type(header):
    """
    Determine image type from FITS header.
    Supports raw ACP headers (IMAGETYP) and ESO-processed headers
    (HIERARCH ESO DPR TYPE / CATG).

    Returns
    -------
    str : 'science', 'bias', 'dark', 'flat', or None
    """
    # Try ESO-processed header first
    dpr_type = header.get('HIERARCH ESO DPR TYPE', '').strip()
    dpr_catg = header.get('HIERARCH ESO DPR CATG', '').strip()

    if dpr_type and dpr_catg:
        if dpr_catg == 'SCIENCE' and dpr_type == 'OBJECT':
            return 'science'
        elif dpr_catg == 'CALIB':
            if dpr_type == 'BIAS':
                return 'bias'
            elif dpr_type == 'DARK':
                return 'dark'
            elif dpr_type == 'FLAT':
                return 'flat'

    # Fall back to raw Astra header
    imagetyp = header.get('IMAGETYP', '').strip()
    if imagetyp == 'Light Frame':
        return 'science'
    elif imagetyp == 'Bias Frame':
        return 'bias'
    elif imagetyp == 'Dark Frame':
        return 'dark'
    elif imagetyp in ('Flat Frame', 'FLAT'):
        return 'flat'

    return None


def format_exptime(exptime):
    """
    Format exposure time for use in filenames.
    Rounds to 3 decimal places and strips trailing zeros and unnecessary
    decimal point (e.g. 20.0 -> '20', 0.500 -> '0.5', 1.234567 -> '1.235').
    """
    rounded = round(float(exptime), 3)
    # Use fixed-point with 3 decimals then strip trailing zeros
    s = f"{rounded:.3f}".rstrip('0').rstrip('.')
    return s


def get_group_key(image_type, header):
    """
    Build a grouping key from header keywords.

    Grouping rules:
        science : OBJECT + FILTER + EXPTIME
        flat    : FILTER + EXPTIME
        dark    : EXPTIME
        bias    : all together

    Returns
    -------
    str : group key
    """
    if image_type == 'science':
        target  = header.get('OBJECT',  'UNKNOWN').strip().replace(' ', '_')
        filt    = header.get('FILTER',  'UNKNOWN').strip().replace(' ', '_')
        exptime = format_exptime(header.get('EXPTIME', 0))
        return f"{target}__{filt}__{exptime}s"

    elif image_type == 'flat':
        filt    = header.get('FILTER',  'UNKNOWN').strip().replace(' ', '_')
        exptime = format_exptime(header.get('EXPTIME', 0))
        return f"flat__{filt}__{exptime}s"

    elif image_type == 'dark':
        exptime = format_exptime(header.get('EXPTIME', 0))
        return f"dark__{exptime}s"

    elif image_type == 'bias':
        return 'bias'

    return None


def classify_fits_file(filepath):
    """
    Classify a single FITS file and return its type and group key.

    Returns
    -------
    tuple : (image_type, group_key, header) or (None, None, None) on error
    """
    try:
        with fits.open(filepath) as hdul:
            header = hdul[0].header.copy()

        image_type = get_image_type(header)

        if image_type is None:
            raw = header.get('IMAGETYP', header.get('HIERARCH ESO DPR TYPE', 'UNKNOWN'))
            print(f"  Warning: unknown image type '{raw}' in {os.path.basename(filepath)}")
            return None, None, None

        group_key = get_group_key(image_type, header)
        return image_type, group_key, header

    except Exception as e:
        print(f"  Error reading {os.path.basename(filepath)}: {e}")
        return None, None, None


def scan_directory(input_dir):
    """
    Recursively scan a directory and classify all FITS files.

    Each file is opened once (header only) to determine its type and group.
    Chronological sorting by DATE-OBS is done inside create_datacube at
    stacking time, where the full header is already being read for pixel data,
    avoiding a second round of file opens.

    Returns
    -------
    dict : {group_key: {'type': str, 'files': [str]}}
    """
    print(f"Scanning: {input_dir}")

    fits_files = []
    for root, _, files in os.walk(input_dir):
        for f in files:
            if f.lower().endswith(('.fits', '.fit', '.fts')):
                fits_files.append(os.path.join(root, f))

    print(f"Found {len(fits_files)} FITS files\n")

    groups = defaultdict(lambda: {'type': None, 'files': []})

    for filepath in fits_files:
        image_type, group_key, _ = classify_fits_file(filepath)
        if image_type is None:
            continue
        groups[group_key]['type'] = image_type
        groups[group_key]['files'].append(filepath)

    # Print summary
    print("=== Classification Summary ===")
    science_groups = {k: v for k, v in groups.items() if v['type'] == 'science'}
    calib_groups   = {k: v for k, v in groups.items() if v['type'] != 'science'}

    print(f"Science groups ({len(science_groups)}):")
    for key, val in sorted(science_groups.items()):
        print(f"  {key}: {len(val['files'])} frames")

    print(f"\nCalibration groups ({len(calib_groups)}):")
    for key, val in sorted(calib_groups.items()):
        print(f"  {key}: {len(val['files'])} frames")
    print()

    return groups


def create_datacube(file_list, image_type, group_key, output_path):
    """
    Stack FITS files into a 3D datacube [frame, y, x] and save to disk.

    The output file has two extensions:
      [0] PRIMARY   : 3D float32 array (datacube)
      [1] METADATA  : BinTable with per-frame header values

    Parameters
    ----------
    file_list   : list of str
    image_type  : str
    group_key   : str
    output_path : str

    Returns
    -------
    bool : True on success
    """
    n = len(file_list)
    if n == 0:
        print(f"  Warning: no files for {group_key}, skipping.")
        return False, '', ''

    print(f"  {group_key}  ({n} frames)...")

    # ------------------------------------------------------------------
    # Single-pass approach — one fits.open() per file, no pre-allocation:
    #
    #   • memmap=False is mandatory: raw FITS files carry BZERO/BSCALE/BLANK
    #     which astropy cannot apply lazily over a memory-map.  On a local
    #     disk this raises an immediate exception; on NFS-mounted storage it
    #     can block indefinitely (observed hang of several hours).
    #
    #   • Frames are appended to a plain Python list and stacked with
    #     np.stack() at the end.  This avoids pre-allocating the full
    #     (N, Y, X) array up-front — at ~8 MB/frame × 300+ frames that
    #     would require >2 GB of contiguous RAM before a single frame is
    #     read, potentially triggering swap on the server.
    #
    #   • DATE-OBS is collected in the same loop, so no second round of
    #     file-opens is needed.  Chronological sorting is done once in
    #     memory after all frames are collected.
    #
    #   • The reference header comes from the first successfully read frame,
    #     also inside this loop — no separate preliminary open required.
    # ------------------------------------------------------------------

    frames_list = []          # list of 2-D ndarray, one per valid frame
    filenames, dates, exptimes, filters_, objects_, airmasses = [], [], [], [], [], []
    ref_header  = None        # header of the first valid frame
    ny = nx = None            # reference shape, determined on first valid frame
    cube_dtype  = None        # native dtype,   determined on first valid frame
    skipped_shape = 0

    for fpath in file_list:
        try:
            with fits.open(fpath, memmap=False) as hdul:
                data   = hdul[0].data
                header = hdul[0].header.copy()
        except Exception as e:
            print(f"    Error reading {os.path.basename(fpath)}: {e}")
            continue

        if data is None:
            print(f"    Warning: no data in {os.path.basename(fpath)}, skipping")
            continue

        # Establish reference dimensions from the first valid frame
        if ref_header is None:
            ref_header = header
            ny, nx     = data.shape
            # Preserve native dtype:
            #   raw ACP  → uint16  (BITPIX=16)
            #   ESO-proc → float32 (BITPIX=-32)
            cube_dtype = data.dtype

        if data.shape != (ny, nx):
            print(f"    Warning: shape mismatch {data.shape} vs {(ny, nx)} "
                  f"in {os.path.basename(fpath)}, skipping")
            skipped_shape += 1
            continue

        frames_list.append(data.astype(cube_dtype))
        filenames.append(os.path.basename(fpath))
        dates.append(str(header.get('DATE-OBS', '')))
        exptimes.append(float(header.get('EXPTIME', 0)))
        filters_.append(str(header.get('FILTER', '')))
        objects_.append(str(header.get('OBJECT', '')))
        airmasses.append(float(header.get('AIRMASS', 0) or 0))

    if skipped_shape > 0:
        print(f"    Warning: {skipped_shape} frame(s) skipped due to shape mismatch "
              f"(expected {ny}x{nx})")
    if not frames_list:
        print(f"  Error: no valid frames for {group_key}")
        return False, '', ''

    # Sort all collected data chronologically by DATE-OBS — purely in memory,
    # no additional file I/O.
    order       = sorted(range(len(dates)), key=lambda i: dates[i])
    frames_list = [frames_list[i] for i in order]
    filenames   = [filenames[i]   for i in order]
    dates       = [dates[i]       for i in order]
    exptimes    = [exptimes[i]    for i in order]
    filters_    = [filters_[i]    for i in order]
    objects_    = [objects_[i]    for i in order]
    airmasses   = [airmasses[i]   for i in order]

    # ----------------------------------------------------------------
    # Streaming write: avoid building the full cube in RAM.
    #
    # np.stack() + PrimaryHDU(data=cube) requires TWO full-cube
    # allocations — one for the native-dtype cube and one for the
    # big-endian byteswap that astropy performs during writeto().
    # For ~2800 frames × 1280×1024 int16 that is 2 × 7 GB = 14 GB.
    #
    # Instead we:
    #   1. Write a header-only stub (data=None) to create the file.
    #   2. Memory-map the data region and fill it one frame at a time.
    # Peak RAM is one frame (~2.6 MB) rather than the full cube.
    # ----------------------------------------------------------------
    valid = len(frames_list)
    n_frames = valid

    # Build and patch the header before opening the file
    primary_hdu = fits.PrimaryHDU(data=None, header=ref_header)
    h = primary_hdu.header
    # Set correct NAXIS/BITPIX for the 3-D cube we are about to write
    bitpix_map = {np.dtype('int16'): 16, np.dtype('uint16'): 16,
                  np.dtype('int32'): 32, np.dtype('float32'): -32,
                  np.dtype('float64'): -64}
    h['BITPIX'] = bitpix_map.get(np.dtype(cube_dtype), 16)
    h['NAXIS']  = 3
    h['NAXIS1'] = nx
    h['NAXIS2'] = ny
    h['NAXIS3'] = n_frames

    # --- WCS axes -------------------------------------------------------------
    # WCSAXES must match the actual number of array dimensions (3 for a cube).
    # The value carried over from a 2D frame header is wrong (usually 0 or 2).
    h['WCSAXES'] = (3, 'Number of WCS axes')

    # --- WCS pixel units (CUNIT1/2 = spatial axes, CUNIT3 = frame axis) ------
    h['CUNIT1'] = ('pixel', 'Axis 1 units')
    h['CUNIT2'] = ('pixel', 'Axis 2 units')
    h['CUNIT3'] = ('frame', 'Axis 3 units (one layer per frame)')

    # --- BLANK is only valid for integer arrays (BITPIX > 0) -----------------
    # Remove it if the cube is floating-point; keep it for integer cubes.
    if 'BLANK' in h and not np.issubdtype(cube_dtype, np.integer):
        del h['BLANK']

    # --- DATE-OBS: truncate to restricted ISO 8601 (YYYY-MM-DDThh:mm:ss.sss) -
    # Raw ACP files have 6 sub-second digits; the standard requires exactly 3.
    if 'DATE-OBS' in h:
        h['DATE-OBS'] = h['DATE-OBS'][:23]

    # --- DATE-END: last frame DATE-OBS + EXPTIME ------------------------------
    # ISO 8601 restricted: YYYY-MM-DDThh:mm:ss.sss  (exactly 3 decimal digits)
    try:
        last_exptime = exptimes[-1] if exptimes else float(ref_header.get('EXPTIME', 0))
        t_end = Time(dates[-1]) + last_exptime * u.second
        h['DATE-END'] = (t_end.isot[:23], 'End of last frame (DATE-OBS + EXPTIME)')
    except Exception:
        pass  # leave DATE-END as-is if we cannot compute it

    # --- Float precision ------------------------------------------------------
    # Sensor / engineering quantities: 3 decimal places is sufficient.
    _kw_3dp = ('ALTITUDE', 'AZIMUTH', 'FW-POS', 'WINDSPD', 'CCD-TEMP',
               'CAM-STAT', 'SKYTEMP', 'DOMESTAT', 'SLEWING', 'TRACKING',
               'DOMPARK', 'FOCUSTEM', 'DOMEAZ', 'OBJCTAZ', 'OBJCTALT',
               'AIRMASS', 'FOCUSPOS', 'AMBTEMP', 'HUMIDITY', 'DEWPOINT',
               'LAT-OBS', 'LONG-OBS')
    for kw in _kw_3dp:
        if kw in h:
            try:
                h[kw] = round(float(h[kw]), 3)
            except (ValueError, TypeError):
                pass

    # Celestial coordinates and WCS solution: 6 decimal places.
    _kw_6dp = ('RA', 'DEC', 'CRPIX1', 'CRPIX2', 'CRVAL1', 'CRVAL2',
               'LONPOLE', 'LATPOLE', 'PC1_1', 'PC1_2', 'PC2_1', 'PC2_2')
    for kw in _kw_6dp:
        if kw in h:
            try:
                h[kw] = round(float(h[kw]), 6)
            except (ValueError, TypeError):
                pass

    # Time keywords: 6 decimal places (preserves ~0.1 s precision for MJD/JD).
    _kw_time_6dp = ('MJD-OBS', 'MJD-END', 'JD-OBS', 'JD-END',
                    'HJD-OBS', 'BJD-OBS', 'LST')
    for kw in _kw_time_6dp:
        if kw in h:
            try:
                h[kw] = round(float(h[kw]), 6)
            except (ValueError, TypeError):
                pass

    # --- Integer keywords -----------------------------------------------------
    for kw in ('PIERSIDE', 'TELPARK'):
        if kw in h:
            try:
                h[kw] = int(h[kw])
            except (ValueError, TypeError):
                pass

    # --- Cube metadata --------------------------------------------------------
    h['CUBETYPE'] = (image_type.upper(), 'Frame type: SCIENCE, BIAS, DARK, FLAT')
    h['CUBEKEY']  = (group_key,          'Grouping key')
    h['COMMENT']  = 'Datacube created by create_datacubes.py'

    # Metadata table HDU
    meta_table = Table({
        'FILENAME': filenames,
        'DATE-OBS': dates,
        'EXPTIME':  exptimes,
        'FILTER':   filters_,
        'OBJECT':   objects_,
        'AIRMASS':  airmasses,
    })
    table_hdu = fits.BinTableHDU(meta_table, name='METADATA')

    # DATE = file-write timestamp, set just before writeto so it is meaningful.
    # Format: YYYY-MM-DDThh:mm:ss.sss
    write_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.') + \
                 f"{datetime.utcnow().microsecond // 1000:03d}"
    h['DATE'] = (write_time, 'File creation date (UTC)')

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Write header-only stub + metadata table first (no pixel data yet)
    fits.HDUList([primary_hdu, table_hdu]).writeto(
        output_path, overwrite=True, output_verify='silentfix')

    # Memory-map the pixel data region and fill frame by frame
    # numpy uses native byte order; FITS requires big-endian, so byteswap
    # each frame individually (tiny allocation: one frame at a time).
    with fits.open(output_path, mode='update') as hdul:
        # Re-open to get the correct data offset, then mmap the file
        data_offset = hdul[0]._data_offset

    fits_dtype = np.dtype(cube_dtype).newbyteorder('>')
    mm = np.memmap(output_path, dtype=fits_dtype, mode='r+',
                   offset=data_offset, shape=(n_frames, ny, nx))
    for i, frame in enumerate(frames_list):
        mm[i] = frame.astype(fits_dtype)
    mm.flush()
    del mm  # release memmap before re-opening

    size_mb = os.path.getsize(output_path) / 1024**2
    print(f"    ✓ Saved: {output_path}  shape=({n_frames}, {ny}, {nx})  ({size_mb:.1f} MB)")

    # Return instrument name and date of first frame for filename construction
    instrume   = ref_header.get('INSTRUME', '').strip()
    first_date = dates[0] if dates else ''
    return True, instrume, first_date


def build_output_name(image_type, group_key, instrume='', first_date=''):
    """
    Build a compact output filename aligned with the ESO archive SPECU# convention.

    Format:
        {SPECU#}.{YYYYMMDD}T{HHMMSS}_{S|C}_{group_key}.fits

    - INSTRUME 'SPECULOOS2' -> 'SPECU2'  (drops 'LOOS', keeps the digit)
    - Date compacted from '2026-02-23T01:47:41' -> '20260223T014741'
    - Type code: 'S' for science, 'C' for calibration
    - Double underscores in group_key collapsed to single

    Examples
    --------
    science  SPECULOOS2  2026-02-23T01:47:41  TIC46432937b__i'__20s
        -> SPECU2.20260223T014741_S_TIC46432937b_i'_20s.fits  (49 chars)

    calib    SPECULOOS2  2026-02-23T01:47:41  flat__i'__5s
        -> SPECU2.20260223T014741_C_flat_i'_5s.fits  (40 chars)

    If INSTRUME or date are not available a minimal fallback name is used.
    """
    clean = group_key.replace('__', '_')
    label = 'S' if image_type == 'science' else 'C'

    if instrume and first_date:
        # Shorten SPECULOOS# -> SPECU#  (e.g. SPECULOOS2 -> SPECU2)
        short_instr = instrume.replace('SPECULOOS', 'SPECU')
        # Compact date: '2026-02-23T01:47:41.123' -> '20260223T014741'
        dt = first_date.split('.')[0]          # strip sub-seconds
        date_part, time_part = dt.split('T')
        compact_date = date_part.replace('-', '') + 'T' + time_part.replace(':', '')
        return f"{short_instr}.{compact_date}_{label}_{clean}.fits"

    # Fallback (no instrument info in header)
    return f"{label}_{clean}.fits"


def create_all_datacubes(groups, output_dir):
    """
    Create one datacube per group.
    """
    print("=== Creating Datacubes ===\n")

    science_groups = {k: v for k, v in groups.items() if v['type'] == 'science'}
    calib_groups   = {k: v for k, v in groups.items() if v['type'] != 'science'}

    success, failed = 0, 0

    print("Science datacubes:")
    for key, val in sorted(science_groups.items()):
        # Use a temporary path; rename after we know instrume and first_date
        tmp_path = os.path.join(output_dir, f'_tmp_{key}.fits')
        ok, instrume, first_date = create_datacube(
            val['files'], val['type'], key, tmp_path)
        if ok:
            fname = build_output_name(val['type'], key, instrume, first_date)
            final_path = os.path.join(output_dir, fname)
            os.replace(tmp_path, final_path)
            print(f"    → Renamed to: {fname}")
        success += ok
        failed  += not ok

    print("\nCalibration datacubes:")
    for key, val in sorted(calib_groups.items()):
        tmp_path = os.path.join(output_dir, f'_tmp_{key}.fits')
        ok, instrume, first_date = create_datacube(
            val['files'], val['type'], key, tmp_path)
        if ok:
            fname = build_output_name(val['type'], key, instrume, first_date)
            final_path = os.path.join(output_dir, fname)
            os.replace(tmp_path, final_path)
            print(f"    → Renamed to: {fname}")
        success += ok
        failed  += not ok

    print(f"\n=== Done: {success} datacubes created, {failed} failed ===")


def main():
    if len(sys.argv) < 2:
        print("Usage: python create_datacubes.py <input_dir> [output_dir]")
        print("\nGrouping rules:")
        print("  Science : target + filter + exptime")
        print("  Flat    : filter + exptime")
        print("  Dark    : exptime")
        print("  Bias    : all together")
        sys.exit(1)

    input_dir  = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './datacubes'

    if not os.path.exists(input_dir):
        print(f"Error: input directory not found: {input_dir}")
        sys.exit(1)

    print("=== SPECULOOS Datacube Creator ===")
    print(f"Input  : {input_dir}")
    print(f"Output : {output_dir}\n")

    groups = scan_directory(input_dir)
    create_all_datacubes(groups, output_dir)


if __name__ == '__main__':
    main()
