# Quick Reference Card

## Installation

```bash
# 1. Install Python dependency
pip install python-dotenv

# 2. Copy credentials for your telescope
cp .credentials.csh.Io.example .credentials.csh      # or Europa, Ganymede, Callisto

# 3. Copy Python environment
cp .env.example .env

# 4. Edit with your credentials
nano .credentials.csh
nano .env

# 5. Secure files
chmod 600 .credentials.csh .env
```

## Running Transfers

```bash
# Automatic (yesterday's data)
./transfer_Astra.csh

# Specific date
./transfer_Astra.csh 20240215

# Multiple dates
./transfer_Astra.csh "20240215 20240216"
```

## Configuration Files

### .credentials.csh (C Shell Variables)
```csh
TELESCOPE_NAME           # Io, Europa, Ganymede, or Callisto
TELESCOPE_BASE_DIR       # ~/ESO_data_transfer/<Telescope>_Astra
ACP_LOCAL_PATH          # Mount point
DATA_DIR                # Work directory
LOG_DIR                 # Log directory
ESO_DIR                 # /home/eso/data_transfer/<telescope>
PYTHON_SCRIPTS_PATH     # Path to Python scripts
CAMBRIDGE_SERVER_*      # Cambridge server credentials
CONTROL_PC_*           # Windows PC credentials
```

### .env (Python Variables)
```bash
SMTP_SERVER            # smtp.hermes.cam.ac.uk:587
SMTP_LOGIN            # Your username
SMTP_PASSWORD         # Your password
EMAIL_FROM            # Sender email
EMAIL_TO              # Recipient email
```

## Telescope-Specific Values

Refer to your internal documentation and the `.credentials.csh.<Telescope>.example` files for:

- Control PC IP addresses
- ESO archive directories  
- Cambridge server paths
- Control PC passwords
- Other telescope-specific configuration

## Monitoring Commands

```bash
# View recent transfers
tail -20 Logs/transfer_log.txt

# Check for failures
cat Logs/YYYYMMDD/non_transferred

# View successful transfers
cat Logs/YYYYMMDD/transferred

# Check cron log
tail -50 Logs/cron.log
```

## Common Issues

| Problem | Solution |
|---------|----------|
| Credentials not found | Copy `.credentials.csh.example` to `.credentials.csh` |
| Python module error | `pip install python-dotenv` |
| Permission denied | `chmod 600 .credentials.csh .env` |
| Wrong telescope data | Check `TELESCOPE_NAME` in `.credentials.csh` |
| Email not sent | Verify SMTP credentials in `.env` |

## File Locations

```
~/ESO_data_transfer/<Telescope>_Astra/
├── transfer_Astra.csh          # Main script
├── .credentials.csh            # Configuration (NEVER commit!)
├── .env                        # Python config (NEVER commit!)
├── Astra_mount/                # Control PC mount point
├── workdir/                    # Temporary storage
└── Logs/                       # Transfer logs
    ├── transfer_log.txt        # Global log
    ├── YYYYMMDD/
    │   ├── transferred         # Success list
    │   └── non_transferred     # Failure list
    └── cron.log               # Automated run log
```

## Cron Setup

```bash
crontab -e
```

```cron
# Run at 13:45 daily
45 13 * * * csh /home/speculoos/ESO_data_transfer/Callisto_Astra/transfer_Astra.csh > /home/speculoos/ESO_data_transfer/Callisto_Astra/cron_logs/`date +\%Y-\%m-\%d_\%H:\%M:\%S`_transfer_cron.log 2>&1
```

## Pipeline Steps

1. 📁 Mount Control PC directory
2. 📋 List FITS files
3. 📥 Copy to work directory
4. 🔄 Rename .fts → .fits
5. 📝 Fix FITS headers
6. ✅ Validate transfers
7. 📤 Move to ESO directory
8. 📊 Log results
9. 🧹 Cleanup work directory

## Emergency Procedures

### Stop All Transfers
```bash
# Find and kill running transfers
ps aux | grep transfer_Astra
kill <PID>
```

### Manual Cleanup
```bash
# Clear stuck work directory
rm -rf ~/ESO_data_transfer/Callisto_Astra/workdir/*
```

### Reprocess Specific Date
```bash
./transfer_Astra.csh 20240215
```

## Security Checklist

- [ ] `.credentials.csh` has mode 600
- [ ] `.env` has mode 600
- [ ] Credentials NOT in version control
- [ ] Using template files (`.example`) for reference
- [ ] Passwords rotated regularly
- [ ] Backups of credentials stored securely

## Quick Tests

```bash
# Test configuration loading
./transfer_Astra.csh

# Verify environment variables loaded
echo $TELESCOPE_NAME
echo $ESO_DIR

# Test email (requires configured .env)
python mail_alert.py TestTelescope 0
```

## Support Resources

- 📖 [CREDENTIALS_SETUP.md](CREDENTIALS_SETUP.md) - Detailed setup
- 🚀 [DEPLOYMENT_GUIDE_TEMPLATE.md](DEPLOYMENT_GUIDE_TEMPLATE.md) - Multi-telescope deployment
- 📋 [transfer_Astra_summary.md](transfer_Astra_summary.md) - Technical details
- 📘 [README.md](README.md) - Full documentation
- 🔒 Internal telescope documentation - Specific configuration values
