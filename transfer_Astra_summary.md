# Data Transfer Pipeline: transfer_Astra.csh

## Overview

Automates data transfer from SPECULOOS telescope control PCs to ESO archive. Handles Io, Europa, Ganymede, and Callisto telescopes.

## Configuration

All telescope-specific settings are in `.credentials.csh`:
- Telescope name and identifiers
- Control PC network path and credentials
- Hub storage paths (mount, work, log, ESO directories)
- Cambridge server credentials

See `.credentials.csh.<Telescope>.example` files for specific values.

## Pipeline Steps

### 1. Mount & Initialize
- Mounts Windows Control PC directory to hub
- Determines date: yesterday (default) or specified argument(s)

### 2. Data Discovery
- Lists all FITS files from control PC for target date(s)
- Tracks files in `filessci.dat`
- Validates folder existence

### 3. Copy to Hub
- Copies FITS files to work directory (`workdir/<date>`)
- Records copied files in `infiles.dat`
- Validates copy completeness (sends email if mismatch)

### 4. Astrometric Processing
**Script**: `astrometry.py` (Io, Europa, Ganymede) or `astrometry_spirit.py` (Callisto)

- Renames `.fts` → `.fits` for compatibility
- Uses multiprocessing for parallel execution
- Creates `infiles_solved.dat`

**Note**: Full astrometric solving (solve-field) is optional - script works with or without astrometry.net installed. WCS information may already be in raw files.

### 5. Header Standardization
**Script**: `headerfix.py`

**For Science Frames**:
- Calculates Position Angle from CD matrix
- Updates WCS transformation matrices
- Converts RA/DEC to decimal degrees (5 decimal places)
- Computes time values: LST, UTC, MJD-OBS, MJD-END, DATE-OBS, DATE-END

**For Calibration Frames** (Bias, Dark, Flat):
- Sets WCS to PIXEL coordinate system
- Identity transformation matrix

**Telescope-Specific Headers**:
| Telescope | INSTRUME | ESO INS NAME | ESO OBS PROG ID |
|-----------|----------|--------------|-----------------|
| Io | SPECULOOS1 | SPECULOOS1 | 60.A-9009(A) |
| Europa | SPECULOOS2 | SPECULOOS2 | 60.A-9009(B) |
| Ganymede | SPECULOOS3 | SPECULOOS3 | 60.A-9009(C) |
| Callisto | SPECULOOS4 | SPECULOOS4 | 60.A-9009(D) |

**Standard ESO Headers**:
- `ORIGIN`: 'SSO-PARANAL'
- `BUNIT`: 'adu'
- `HIERARCH ESO DPR CATG`: SCIENCE or CALIB
- `HIERARCH ESO DPR TYPE`: OBJECT, BIAS, DARK, FLAT
- `HIERARCH ESO DPR TECH`: IMAGE

**File Renaming**:
```
Format: INSTRUMENTNAME.YYYY-MM-DDTHH_MM_SS.mmm.fits
Example: SPECULOOS4.2023-01-15T23_45_12.345.fits
```

### 6. Logging
- `transferred`: Successfully formatted files
- `non_transferred`: Failed files
- `transfer_log.txt`: Global log (date + count)
- Syncs log to Cambridge server

### 7. Transfer to ESO
- Moves `SPECULOOS*.fits` files to ESO directory
- Only successfully processed files transferred

### 8. Error Alerts
**Script**: `mail_alert.py`

Sends email when:
- Files fail to copy from Control PC
- Files fail to transfer to ESO directory

### 9. Cleanup
- Deletes work directory for processed date
- Frees hub storage

### 10. No Data Handling
- If date folder missing, logs count = 0
- Maintains log continuity

## Validation Checkpoints

1. **Copy Verification**: Compare file counts (Control PC vs Hub) → Email on failure
2. **Header Processing**: Successful file renaming to SPECULOOS* pattern
3. **ESO Transfer**: Count non-transferred files → Email + log on failure

## Performance

- Python multiprocessing in `astrometry.py` and `headerfix.py`
- Parallel file processing reduces batch processing time

## Data Flow

```
Control PC (Windows) 
    ↓ Mount
Hub Mount Point
    ↓ Copy
Hub Work Directory
    ↓ Astrometry → Header Fix
ESO Archive Directory
```

## Execution Modes

```bash
# Automatic (yesterday)
./transfer_Astra.csh

# Specific date
./transfer_Astra.csh 20230115

# Multiple dates
./transfer_Astra.csh "20230115 20230116"
```

## Output Files

**Per Night**:
- `filessci.dat` - Source file list
- `infiles.dat` - Copied file list  
- `infiles_solved.dat` - Post-astrometry list
- `transferred` - Success list
- `non_transferred` - Failure list (if any)

**Global**:
- `transfer_log.txt` - Cumulative history

**Final**:
- `SPECULOOS*.fits` - ESO-compliant files in ESO directory

## Key Features

- Automated daily processing (no arguments needed)
- Batch mode for multiple dates
- Multiple validation checkpoints
- Email alerts on failures
- Comprehensive logging with Cambridge sync
- ESO header compliance
- Accurate time/coordinate calculations
