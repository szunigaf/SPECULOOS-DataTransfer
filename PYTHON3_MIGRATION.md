# Python 3 Migration Guide

## Overview

All Python scripts have been updated to Python 3 compatibility (Feb 17, 2026).

## Changes Made

### Scripts Updated
- ✅ `astrometry.py` - Updated to Python 3, fixed indentation errors, added error handling
- ✅ `astrometry_spirit.py` - Updated to Python 3
- ✅ `headerfix.py` - Updated to Python 3
- ✅ `mail_alert.py` - Updated to Python 3

### Author Information
All scripts now include:
```python
@author: laetitia
@author: Seba Zuniga-Fernandez
```

## Required Dependencies

### 1. Python 3
```bash
# Check version (must be 3.6 or higher)
python3 --version
```

### 2. Python Packages
Install using the requirements file:
```bash
pip3 install -r requirements.txt
```

Or manually:
```bash
pip3 install astropy>=5.0
pip3 install python-dotenv>=0.19.0
```

### Complete Dependency List

| Package | Version | Purpose |
|---------|---------|---------|
| **Python** | 3.6+ | Runtime environment |
| **astropy** | ≥5.0 | FITS file handling, astronomical coordinates |
| **python-dotenv** | ≥0.19.0 | Environment variable loading from .env |

### System Dependencies

| Dependency | Required For | Installation |
|------------|--------------|--------------|
| **sshpass** | Cambridge server transfers | `apt-get install sshpass` (Linux)<br>`brew install sshpass` (macOS) |
| **mount/cifs-utils** | Windows PC mounting | Usually pre-installed |
| **astrometry.net** | Plate solving (optional) | See [astrometry.net](http://astrometry.net/use.html) |

## Migration Steps for Each Telescope

### Step 1: Verify Python 3 Installation
```bash
python3 --version
# Should show Python 3.6 or higher
```

### Step 2: Install Dependencies
```bash
cd ~/ESO_data_transfer/<Telescope>_Astra

# Install Python packages
pip3 install -r requirements.txt

# Verify installations
python3 -c "import astropy; print('astropy:', astropy.__version__)"
python3 -c "import dotenv; print('python-dotenv: OK')"
```

### Step 3: Update Scripts
```bash
# Copy updated Python scripts
cp /path/to/repo/astrometry.py .
cp /path/to/repo/astrometry_spirit.py .
cp /path/to/repo/headerfix.py .
cp /path/to/repo/mail_alert.py .

# Make executable
chmod +x *.py
```

### Step 4: Test Individual Scripts
```bash
# Test mail alert
python3 mail_alert.py TestTelescope 0

# Test file renaming (with a test file list)
python3 astrometry_spirit.py test_files.dat

# Test header fixing (with test files)
python3 headerfix.py test_files.dat Callisto
```

### Step 5: Test Full Pipeline
```bash
# Run with a specific date to test
./transfer_Astra.csh 20240101
```

### Step 6: Update Cron Jobs (if needed)
The cron jobs should work as-is since the scripts now use `#!/usr/bin/env python3`.

However, you can verify:
```bash
crontab -l
```

If there are explicit `python` or `python2` calls, update them to `python3`.

## Compatibility Notes

### What Changed
- Shebang: `#!/usr/bin/env python2` → `#!/usr/bin/env python3`
- All existing code is Python 3 compatible
- Error handling improved in `astrometry.py`
- Indentation errors fixed

### What Stayed the Same
- Script behavior and functionality
- Command-line arguments
- Input/output file formats
- Environment variable usage
- C shell script (`transfer_Astra.csh`) unchanged

## Verification Checklist

After migration on each telescope:

- [ ] `python3 --version` shows 3.6+
- [ ] `pip3 list` shows `astropy` and `python-dotenv`
- [ ] `python3 mail_alert.py Test 0` sends email successfully
- [ ] `python3 astrometry_spirit.py <file_list>` renames files
- [ ] `python3 headerfix.py <file_list> <telescope>` processes headers
- [ ] Full pipeline test with sample data completes
- [ ] Cron jobs execute successfully
- [ ] Logs show no Python-related errors

## Rollback Plan

If issues occur, you can temporarily revert:

1. **Reinstall Python 2** (not recommended, Python 2 is EOL):
   ```bash
   # Keep Python 3, but use python2 explicitly
   pip2 install astropy python-dotenv
   ```

2. **Revert script shebangs** to `python2`:
   ```bash
   sed -i 's/python3/python2/g' *.py
   ```

3. **Use old scripts** from backup/repository history

## Troubleshooting

### Error: "No module named 'dotenv'"
```bash
pip3 install python-dotenv
```

### Error: "No module named 'astropy'"
```bash
pip3 install astropy
```

### Error: "/usr/bin/env: 'python3': No such file or directory"
```bash
# Install Python 3
# Linux: sudo apt-get install python3
# macOS: brew install python3
```

### Error: "SyntaxError" or "IndentationError"
Ensure you have the latest version of the scripts from the repository.

## Performance Notes

Python 3 is generally **faster** than Python 2, especially for:
- String operations
- Dictionary operations
- I/O operations

You may notice slight performance improvements in the pipeline.

## Future Considerations

### Recommended Python Version
- **Minimum**: Python 3.6
- **Recommended**: Python 3.9+
- **Latest stable**: Python 3.11+

### Virtual Environments (Optional)
For better dependency management:

```bash
# Create virtual environment
python3 -m venv ~/speculoos_venv

# Activate
source ~/speculoos_venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Update cron to use venv Python
# In crontab: /path/to/venv/bin/python3 script.py
```

## Support

For migration issues:
1. Check this migration guide
2. Review `requirements.txt` for dependencies
3. Test scripts individually before full pipeline
4. Check logs for specific error messages
5. Contact: Seba Zuniga-Fernandez

---

**Migration Date**: February 17, 2026  
**Python Version**: 3.6+  
**Status**: Production Ready
