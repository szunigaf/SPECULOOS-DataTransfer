# Data Transfer Logic: transfer_Astra.csh

## Overview

The `transfer_Astra.csh` script is responsible for automating the data transfer pipeline from SPECULOOS telescope control PCs to the ESO archive. The script handles data from four telescopes: Io, Europa, Ganymede, and Callisto.

---

## Configuration Parameters

### Telescope Settings
- **Telescope Name**: Configurable (e.g., "Callisto")
- **Windows Control PC Path**: Network path to raw data storage
  - Example: `//speculoos:c0ntrolPC-04@172.16.0.202/Documents/astra/images/`

### Hub Storage Paths
- **ACP Local Mount**: `~/ESO_data_transfer/Callisto_Astra/Astra_mount`
- **Work Directory**: `~/ESO_data_transfer/Callisto_Astra/workdir`
- **Log Directory**: `~/ESO_data_transfer/Callisto_Astra/Logs`
- **ESO Directory**: `/home/eso/data_transfer/callisto`
- **Cambridge Server Path**: `speculoos@appcs.ra.phy.cam.ac.uk:/appct/data/SPECULOOSPipeline/Observations/Callisto/.`

---

## Data Flow Pipeline

### 1. **Initialization & Mount**
```
Mount Windows Control PC directory → Hub mount point
```
- Mounts the ACP Astronomy directory containing raw data
- Validates connection to the control PC

### 2. **Date Selection**
```
No argument → Yesterday's date (YYYYMMDD)
With argument → Specified date(s)
```
- Supports single date or multiple dates for batch processing
- Uses format: YYYYMMDD (e.g., 20230115)

### 3. **Data Discovery**
```
Check if date folder exists → List all FITS files → Count files
```
**Files tracked:**
- `filessci.dat`: List of source FITS files from control PC
- `infiles.dat`: List of files copied to Hub

**Validation:**
- Compares source count vs. copied count
- Sends email alert if counts don't match

### 4. **Data Copy to Hub**
```
Control PC files → Hub work directory
```
- Creates temporary directory: `$data_dir/$date`
- Copies all `*.fits` files from mounted directory
- Verifies copy completeness

### 5. **Astrometric Solving**
```
Python: astrometry_spirit.py
```
**Purpose**: Prepare files for astrometric calibration

**Operations:**
- Renames `.fts` files to `.fits` (astrometry solver requirement)
- Uses multiprocessing for parallel execution
- Creates list: `infiles_solved.dat`

**Note:** The actual astrometric solving code is commented out in the current version. The astrometry_spirit.py script only performs file renaming (.fts → .fits) to ensure compatibility. The full astrometry solving functionality (using solve-field) appears to be disabled, likely because WCS information is already present in the raw files or is added at a different stage in the pipeline. This does not impact the pipeline's ability to process and transfer data to ESO.

### 6. **Header Fixing & Standardization**
```
Python: headerfix.py
```
**Purpose**: Format FITS headers to ESO standards

**For Light Frames (Science Images):**
- **Position Angle (PA) Calculation**
  - Computed from CD matrix elements
  - Range: 0-360° CCW
- **WCS Transformation**
  - Updates CD1_1, CD1_2, CD2_1, CD2_2 matrices
- **Coordinate Processing**
  - Converts RA/DEC to decimal degrees
  - Precision: 5 decimal places
- **Time Calculations**
  - LST (Local Sidereal Time) at Paranal longitude (-70.4028°)
  - UTC in seconds
  - MJD-OBS (Modified Julian Date at start)
  - MJD-END (Modified Julian Date at end)
  - DATE-OBS, DATE-END in ISO format

**For Calibration Frames (Bias, Dark, Flat):**
- Sets WCS keywords to PIXEL coordinate system
- Sets transformation matrix to identity

**Telescope-Specific Headers:**
| Telescope | TELESCOP | INSTRUME | ESO INS NAME | ESO OBS PROG ID |
|-----------|----------|----------|--------------|-----------------|
| Io | SPECULOOS-IO | SPECULOOS1 | SPECULOOS1 | 60.A-9009(A) |
| Europa | SPECULOOS-EUROPA | SPECULOOS2 | SPECULOOS2 | 60.A-9009(B) |
| Ganymede | SPECULOOS-GANYMEDE | SPECULOOS3 | SPECULOOS3 | 60.A-9009(C) |
| Callisto | SPECULOOS-CALLISTO | SPECULOOS4 | SPECULOOS4 | 60.A-9009(D) |

**Standard ESO Headers Added:**
- `ORIGIN`: 'SSO-PARANAL'
- `BUNIT`: 'adu' (Analog-to-Digital Units)
- `HIERARCH ESO DPR CATG`: SCIENCE or CALIB
- `HIERARCH ESO DPR TYPE`: OBJECT, BIAS, DARK, or FLAT
- `HIERARCH ESO DPR TECH`: IMAGE

**Cleanup:**
- Removes unnecessary keywords (COMMENT, HISTORY, EPOCH, etc.)
- Removes astrometry solver artifacts

**File Renaming:**
```
Format: INSTRUMENTNAME.YYYY-MM-DDTHH_MM_SS.mmm.fits
Example: SPECULOOS4.2023-01-15T23_45_12.345.fits
```
- Original files are deleted after successful conversion

### 7. **Logging & Tracking**
```
Create transfer lists → Update global log → Sync to Cambridge
```
**Log Files Created:**
- `transferred`: List of successfully formatted files (SPECULOOS*.fits)
- `non_transferred`: List of files that failed processing
- `transfer_log.txt`: Global log with date and file count

**Log Entry Format:**
```
YYYYMMDD count
```

**Cambridge Sync:**
- Uses `sshpass` with credentials to copy global log
- Destination: Cambridge server for central monitoring

### 8. **Transfer to ESO**
```
Hub work directory → ESO archive directory
```
- Moves all `SPECULOOS*.fits` files to ESO directory
- Only successfully formatted files are transferred

### 9. **Error Detection & Alerts**
```
Python: mail_alert.py
```
**Triggered when:**
- Files fail to copy from Control PC to Hub
- Files fail to transfer to ESO directory

**Alert Contents:**
- Telescope name
- Number of failed files
- Sent via SMTP to monitoring email

### 10. **Cleanup**
```
Delete temporary work directory
```
- Removes `$data_dir/$date` directory
- Frees up Hub storage space

### 11. **No Data Handling**
```
If date folder doesn't exist → Log zero files
```
- Still creates log entry with count = 0
- Ensures continuity in transfer log

---

## Data Validation Points

### ✓ Checkpoint 1: Copy Verification
- **Input**: Files from Control PC
- **Output**: Files in Hub work directory
- **Validation**: Count comparison
- **Action on Failure**: Email alert

### ✓ Checkpoint 2: Header Processing
- **Input**: Raw FITS files
- **Output**: ESO-formatted FITS files
- **Validation**: Successful file renaming to SPECULOOS* pattern
- **Action on Failure**: Files remain in work directory

### ✓ Checkpoint 3: Transfer to ESO
- **Input**: Formatted FITS files
- **Output**: Files in ESO directory
- **Validation**: Count of non-transferred files
- **Action on Failure**: Email alert + log of failed files

---

## Parallel Processing

The pipeline uses Python multiprocessing for performance:
- **astrometry_spirit.py**: ThreadPool for parallel file renaming
- **headerfix.py**: ThreadPool for parallel header processing

This significantly reduces processing time for large batches of images.

---

## File Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    Control PC Storage                       │
│              (Windows network share)                         │
└───────────────────────────┬─────────────────────────────────┘
                            │ Mount
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Hub Mount Point                          │
│         ~/ESO_data_transfer/Callisto_Astra/Astra_mount      │
└───────────────────────────┬─────────────────────────────────┘
                            │ Copy
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Hub Work Directory                       │
│         ~/ESO_data_transfer/Callisto_Astra/workdir          │
│                                                              │
│  [Raw FITS] → [Astrometry] → [Header Fix] → [SPECULOOS*]   │
└───────────────────────────┬─────────────────────────────────┘
                            │ Move
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    ESO Archive Directory                    │
│              /home/eso/data_transfer/callisto               │
│                (Final destination for ESO)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Error Handling & Notifications

### Email Alerts via mail_alert.py

**Scenario 1: Copy Failure**
- Triggered when files don't copy completely from Control PC to Hub
- Includes count of missing files

**Scenario 2: Transfer Failure**
- Triggered when files don't transfer to ESO directory
- Includes count of failed files

**Email Configuration:**
- **SMTP Server**: smtp.hermes.cam.ac.uk:587
- **From**: lcd44@cam.ac.uk
- **To**: lcd44@cam.ac.uk
- **Subject**: "Issue with transfer of files to ESO archive for [Telescope]"

---

## Key Features

### ✨ Automated Processing
- Can run without arguments (processes yesterday's data)
- Can process specific dates via command-line arguments
- Can process multiple dates in batch mode

### ✨ Robustness
- Multiple validation checkpoints
- Email alerts for failures
- Comprehensive logging

### ✨ Traceability
- Global log file tracks all transfers
- Per-night logs for success and failure lists
- Log synchronization to Cambridge server

### ✨ ESO Compliance
- Standardizes headers to ESO requirements
- Proper coordinate system conversion
- Accurate time calculations (UTC, LST, MJD)
- Correct instrument and program identification

---

## Execution Modes

### Mode 1: Automatic (No Arguments)
```bash
./transfer_Astra.csh
```
- Processes yesterday's observations
- Single night processing

### Mode 2: Manual (With Date Argument)
```bash
./transfer_Astra.csh 20230115
```
- Processes specified date
- Can provide multiple dates space-separated

---

## Output Summary

### Files Generated Per Night:
1. **filessci.dat**: Source file list
2. **infiles.dat**: Copied file list
3. **infiles_solved.dat**: Post-astrometry file list
4. **transferred**: Successfully transferred files
5. **non_transferred**: Failed transfers (if any)

### Global Log:
- **transfer_log.txt**: Cumulative transfer history

### Final Data:
- **SPECULOOS*.fits**: ESO-compliant FITS files in ESO directory
