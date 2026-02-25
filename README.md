# SPECULOOS-DataTransfer

Automated data transfer pipeline for SPECULOOS South observations from telescope control PCs to ESO archive.

## Overview

This repository contains scripts to automate the transfer and formatting of astronomical data from the four SPECULOOS telescopes (Io, Europa, Ganymede, Callisto) to the ESO archive. The pipeline handles:

- 🔄 Automated data transfer from Windows control PCs
- 🔭 Astrometric calibration preparation
- 📝 FITS header standardization to ESO requirements
- ✅ Data validation and error reporting
- 📧 Email alerts for transfer issues
- 📊 Comprehensive logging

## Key Features

✨ **Telescope-Agnostic Architecture**: Single script works across all four telescopes  
🔐 **Secure Credential Management**: Environment-based configuration keeps secrets safe  
⚡ **Parallel Processing**: Multi-threaded Python scripts for performance  
📈 **Comprehensive Logging**: Detailed tracking of all transfers  
🛡️ **Multiple Validation Points**: Ensures data integrity throughout pipeline  

## Quick Start

### Prerequisites

- Python 3.7+ with conda environment
- Packages: `astropy`, `python-dotenv`, `numpy` (see `requirements.txt`)

### Setup

1. **Create conda environment:**
   ```bash
   conda create -n speculoos_py3 python=3.7
   conda activate speculoos_py3
   pip install -r requirements.txt
   ```

2. **Copy credentials template:**
   ```bash
   # Choose your telescope: Io, Europa, Ganymede, or Callisto
   cp .credentials.csh.Io.example .credentials.csh
   cp .env.example .env
   ```

3. **Edit credentials:**
   ```bash
   nano .credentials.csh
   nano .env
   chmod 600 .credentials.csh .env
   ```

4. **Run transfer:**
   ```bash
   ./transfer_Astra.csh
   ```

## Repository Structure

```
.
├── transfer_Astra.csh                    # Main transfer script
├── astrometry.py                         # Astrometric solving (Io, Europa, Ganymede)
├── astrometry_spirit.py                  # File renaming (Callisto)
├── headerfix.py                          # FITS header standardization
├── mail_alert.py                         # Email notifications
├── requirements.txt                      # Python dependencies
│
├── .env.example                          # Email credentials template
├── .credentials.csh.example              # Shell credentials (Callisto)
├── .credentials.csh.Io.example           # Io-specific template
├── .credentials.csh.Europa.example       # Europa-specific template
├── .credentials.csh.Ganymede.example     # Ganymede-specific template
│
├── INSTALLATION_GUIDE.md                 # Server deployment guide
├── DEPLOYMENT_GUIDE_TEMPLATE.md          # Multi-telescope setup
├── QUICK_REFERENCE.md                    # Daily operations reference
├── CHANGES_SUMMARY.md                    # Complete changelog
├── transfer_Astra_summary.md             # Technical documentation
└── README.md                             # This file
```

## Documentation

- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)**: Server deployment and setup guide
- **[DEPLOYMENT_GUIDE_TEMPLATE.md](DEPLOYMENT_GUIDE_TEMPLATE.md)**: Multi-telescope deployment template
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)**: Quick reference for daily operations
- **[transfer_Astra_summary.md](transfer_Astra_summary.md)**: Technical pipeline documentation
- **[CHANGES_SUMMARY.md](CHANGES_SUMMARY.md)**: Complete changelog of all updates

## Pipeline Workflow

```
┌─────────────────────────────────────────────────────────────┐
│              Windows Control PC (Raw Data)                  │
└───────────────────────────┬─────────────────────────────────┘
                            │ Mount & Copy
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Hub Work Directory                        │
│  [Copy Files] → [Astrometry Solving] → [Fix Headers]       │
└───────────────────────────┬─────────────────────────────────┘
                            │ Transfer
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    ESO Archive Directory                    │
│              (Final SPECULOOS*.fits files)                   │
└─────────────────────────────────────────────────────────────┘
```

## Telescope Configuration

Each telescope requires specific credentials. See `.credentials.csh.<Telescope>.example` files for templates with telescope-specific values.

## Usage

### Automatic Mode (Process Yesterday's Data)
```bash
./transfer_Astra.csh
```

### Manual Mode (Specify Date)
```bash
./transfer_Astra.csh 20240215
```

### Multiple Dates
```bash
./transfer_Astra.csh "20240215 20240216 20240217"
```

## Automated Scheduling

Set up cron jobs for automated daily transfers:

```bash
env EDITOR=nano crontab -e
```

Add entry (example for Callisto):
```cron
45 13 * * * csh /home/speculoos/ESO_data_transfer/Callisto_Astra/transfer_Astra.csh > /home/speculoos/ESO_data_transfer/Callisto_Astra/cron_logs/`date +\%Y-\%m-\%d_\%H:\%M:\%S`_transfer_cron.log 2>&1
```

## Security

⚠️ **Important Security Notes:**

- `.env` and `.credentials.csh` contain sensitive information
- These files are **git-ignored** and should NEVER be committed
- Use `.example` template files for reference
- Set restrictive permissions: `chmod 600` on credential files


## Monitoring

```bash
# View transfer history
tail -20 Logs/transfer_log.txt

# Check failures
ls Logs/*/non_transferred

# View cron logs
tail -50 cron_logs/*_transfer_cron.log
```

Email alerts are sent automatically when transfers fail (configure in `.env`).
### "Credentials file not found"
Ensure `.credentials.csh` exists in the script directory or `~/.credentials.csh`

### "TELESCOPE_NAME not set"
Edit `.credentials.csh` and verify `TELESCOPE_NAME` is properly set
## Troubleshooting

| Issue | Solution |
|-------|----------|
| Credentials not found | Copy `.credentials.csh.example` to `.credentials.csh` |
| TELESCOPE_NAME not set | Verify setting in `.credentials.csh` |
| Python import error | `conda activate speculoos_py3; pip install -r requirements.txt` |
| Email not working | Install `python-dotenv`, verify `.env` credentials |

See `INSTALLATION_GUIDE.md` for detailed troubleshooting.dding new features
3. **Never commit credential files** (`.env`, `.credentials.csh`)
4. **Use telescope-agnostic code** - avoid hardcoding telescope names

## Contributing

Test thoroughly before deploying. Never commit credential files. Keep code telescope-agnostic.
- Pipeline architecture: SPECULOOS team

## Support

For issues or questions:
1. Check the documentation in this repository
2. Review log files for error messages
3. Verify credential configuration
4. Contact the SPECULOOS data management team

---

## Support

Check documentation in this repository and log files. Contact SPECULOOS data management team for issues.

---

**Authors**: Original by Laetitia Delrez (2018), revised by Seba Zúñiga-Fernández (2026)  
**Last Updated**: February 2026
