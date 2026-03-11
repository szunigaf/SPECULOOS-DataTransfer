# Installation Guide - SPECULOOS Data Transfer Pipeline

## Prerequisites

- SPECULOOS server SSH access
- Anaconda2 at `/home/speculoos/Programs/anaconda2`
- Git installed
- Permissions for `/home/speculoos/ESO_data_transfer/`

## Installation Steps

### 1. Get Latest Code

```bash
cd /home/speculoos/ESO_data_transfer/[Telescope]_Astra
git pull origin main
```

### 2. Create Python 3 Environment

```bash
conda create -n speculoos_py3 python=3.7
conda activate speculoos_py3
pip install -r requirements.txt  # or: pip install astropy numpy

# Verify
python --version
python -c "import astropy, numpy; print('Success')"
```

### 3. Update Python Shebangs

Change first line in all `.py` files from:
```python
#!/opt/anaconda3/envs/speculoos_py3/bin/python
```
To:
```python
#!/home/speculoos/Programs/anaconda2/envs/speculoos_py3/bin/python
```

Quick update:
```bash
sed -i 's|#!/opt/anaconda3/envs/speculoos_py3/bin/python|#!/home/speculoos/Programs/anaconda2/envs/speculoos_py3/bin/python|g' *.py
```

### 4. Make Scripts Executable

```bash
chmod +x *.py *.csh
```

### 5. Configure Credentials

```bash
# Copy template for your telescope
cp .credentials.csh.Io.example .credentials.csh        # or Europa, Ganymede, Callisto

# Edit with actual values
nano .credentials.csh

# Secure
chmod 600 .credentials.csh
```

**Key settings in `.credentials.csh`**:
- `TELESCOPE_NAME`
- `CONTROL_PC_USER`, `CONTROL_PC_PASSWORD`, `CONTROL_PC_IP`
- `ACP_LOCAL_PATH`, `DATA_DIR`, `LOG_DIR`, `ESO_DIR`
- `CAMBRIDGE_SERVER_*`

### 6. Install Astrometry.net (Optional, for Io/Europa/Ganymede)

```bash
# Check if installed
which solve-field

# Install if needed (Ubuntu/Debian)
sudo apt-get install astrometry.net

# Verify
solve-field --version
```

**Note**: Callisto uses `astrometry_spirit.py` (no astrometry.net needed). Script works without astrometry.net installed.
### 7. Test Pipeline

```bash
./transfer_Astra.csh 20260222  # Use date with existing data
```

Expected: Mount → Copy → Astrometry → Fix headers → Transfer to ESO → Logs

### 8. Verify Results

```bash
# Check logs
cat Logs/transfer_log.txt
ls Logs/20260222/non_transferred  # Should be empty or non-existent

# Verify ESO output (individual frames for Io/Europa/Ganymede)
ls -lh [ESO_DIR]/SPECULOOS*.fits
# Verify ESO output (datacubes for Callisto/SPIRIT)
ls -lh [ESO_DIR]/SPECU*_S_*.fits [ESO_DIR]/SPECU*_C_*.fits

# Check headers
conda activate speculoos_py3
python -c "from astropy.io import fits; import glob; f=glob.glob('[ESO_DIR]/SPECULOOS*.fits')[0]; h=fits.getheader(f); print('TELESCOP:', h.get('TELESCOP'), 'INSTRUME:', h.get('INSTRUME'))"
```

### 9. Setup Cron Job

```bash
crontab -e
```

Add (adjust telescope and time):
```cron
45 13 * * * csh /home/speculoos/ESO_data_transfer/[Telescope]_Astra/transfer_Astra.csh > /home/speculoos/ESO_data_transfer/[Telescope]_Astra/cron_logs/`date +\%Y-\%m-\%d_\%H:\%M:\%S`_transfer_cron.log 2>&1
```

Create log directory:
```bash
mkdir -p cron_logs
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Conda not activating | `conda init csh; source ~/.cshrc` |
| Python import errors | `conda activate speculoos_py3; pip install -r requirements.txt` |
| solve-field not found | Script continues without it; check `which solve-field; echo $PATH` |
| Permission denied | `chmod +x *.py *.csh` |
| PYTHONHOME errors | `unset PYTHONHOME; unset PYTHONPATH` or add to `.cshrc` |

## Key Changes from Previous Version

1. **Python 3 Migration**: All scripts now require Python 3.7+
2. **Conda Environment**: Uses `speculoos_py3` environment instead of system Python
3. **Credential Management**: External `.credentials.csh` file (not committed to git)
4. **Telescope-Agnostic**: Same script works for all telescopes
5. **Improved Error Handling**: Better validation and error messages
6. **Flexible Astrometry**: Works with or without astrometry.net installed

---

## File Checklist

After installation, verify these files exist:

- [ ] `transfer_Astra.csh` - Main transfer script (Io/Europa/Ganymede)
- [ ] `transfer_Astra_spirit.csh` - Transfer script for Callisto (SPIRIT)
- [ ] `.credentials.csh` - Telescope-specific credentials (not in git)
- [ ] `mail_alert.py` - Email notification script
- [ ] `astrometry.py` or `astrometry_spirit.py` - Astrometry processing
- [ ] `headerfix.py` - FITS header standardization
- [ ] `create_datacubes.py` - Datacube creator (Callisto/SPIRIT only)
- [ ] `requirements.txt` - Python dependencies list

---

## Post-Installation

Once everything is working:

1. Document any telescope-specific settings
2. Test the cron job runs successfully
3. Monitor logs for the first few automatic runs
4. Verify data arrives at ESO archive
5. Update internal documentation with new procedures

---

## Support

For issues:
1. Check log files in `Logs/` directory
## Key Changes from Previous Version

- Python 3.7+ (was Python 2.7)
- Conda environment `speculoos_py3`
- External credentials file (`.credentials.csh`)
- Telescope-agnostic script
- Optional astrometry.net (auto-detection)
- Better error handling

## Post-Installation Checklist

- [ ] `transfer_Astra.csh` - Main script
- [ ] `.credentials.csh` - Credentials (git-ignored)
- [ ] `.env` - Email config (optional, git-ignored)
- [ ] `mail_alert.py`, `astrometry*.py`, `headerfix.py` - Python scripts
- [ ] Test run successful
- [ ] Cron job configured
- [ ] Monitor first few automatic runs

## Support

1. Check `Logs/` directory
2. Verify conda: `conda activate speculoos_py3`
3. Test scripts individually
4. Review cron logs
5. Contact SPECULOOS data team

---

**Version**: 2.0 (Python 3)  
**Last Updated**: February 2026