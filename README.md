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

```bash
# Install required Python package
pip install python-dotenv
```

### Setup for a Telescope

1. **Choose your telescope** (Io, Europa, Ganymede, or Callisto)

2. **Copy the appropriate credentials template:**
   ```bash
   cp .credentials.csh.Io.example .credentials.csh       # For Io
   cp .credentials.csh.Europa.example .credentials.csh   # For Europa
   cp .credentials.csh.Ganymede.example .credentials.csh # For Ganymede
   cp .credentials.csh.example .credentials.csh          # For Callisto
   ```

3. **Copy Python environment template:**
   ```bash
   cp .env.example .env
   ```

4. **Edit configuration files with your credentials:**
   ```bash
   nano .credentials.csh
   nano .env
   ```

5. **Secure credential files:**
   ```bash
   chmod 600 .credentials.csh .env
   ```

6. **Run the transfer script:**
   ```bash
   ./transfer_Astra.csh
   ```

## Repository Structure

```
.
├── transfer_Astra.csh           # Main transfer script (telescope-agnostic)
├── astrometry.py                # Astrometric plate solving (Io, Europa, Ganymede)
├── headerfix.py                 # FITS header standardization
├── mail_alert.py                # Email notification system
│
├── .env.example                 # Python credentials template
├── .credentials.csh.example     # C shell credentials template (Callisto)
├── .credentials.csh.Io.example      # Io-specific template
├── .credentials.csh.Europa.example  # Europa-specific template
├── .credentials.csh.Ganymede.example # Ganymede-specific template
│
├── CREDENTIALS_SETUP.md         # Detailed setup instructions
├── DEPLOYMENT_GUIDE.md          # Multi-telescope deployment guide
├── transfer_Astra_summary.md    # Technical documentation
└── README.md                    # This file
```

## Documentation

- **[DEPLOYMENT_GUIDE_TEMPLATE.md](DEPLOYMENT_GUIDE_TEMPLATE.md)**: Template for deploying across multiple telescopes
- **[transfer_Astra_summary.md](transfer_Astra_summary.md)**: Technical overview of the data transfer pipeline

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

Each telescope has specific configuration requirements. Consult your internal documentation for:

- Instrument identifiers (SPECULOOS1-4)
- ESO Program IDs (60.A-9009)
- Control PC network addresses
- ESO archive directories
- Cambridge server paths

See the `.credentials.csh.<Telescope>.example` files for template configurations.

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
- Regularly rotate passwords
- Consider SSH key-based authentication for remote servers

## Monitoring & Logs

### Transfer Logs
```bash
# View transfer history
tail -20 ~/ESO_data_transfer/Callisto_Astra/Logs/transfer_log.txt

# Check for failed transfers
ls ~/ESO_data_transfer/Callisto_Astra/Logs/*/non_transferred
```

### Email Alerts

The system sends automatic email alerts when:
- Files fail to copy from Control PC to Hub
- Files fail to transfer to ESO directory

Configure email settings in `.env` file.

## Troubleshooting

### "Credentials file not found"
Ensure `.credentials.csh` exists in the script directory or `~/.credentials.csh`

### "TELESCOPE_NAME not set"
Edit `.credentials.csh` and verify `TELESCOPE_NAME` is properly set

### Python scripts not found
Check `PYTHON_SCRIPTS_PATH` in `.credentials.csh` points to the correct directory

### Email alerts not working
1. Install python-dotenv: `pip install python-dotenv`
2. Verify email credentials in `.env` file
3. Test SMTP connection manually

## Contributing

When making changes to the scripts:

1. **Test thoroughly** on one telescope before deploying to all
2. **Update documentation** if adding new features
3. **Never commit credential files** (`.env`, `.credentials.csh`)
4. **Use telescope-agnostic code** - avoid hardcoding telescope names

## License

See [LICENSE](LICENSE) file for details.

## Authors

- Original author: Laetitia Delrez 2018
- Revised and updated by Seba Zúñiga-Fernández 2026
- Pipeline architecture: SPECULOOS team

## Support

For issues or questions:
1. Check the documentation in this repository
2. Review log files for error messages
3. Verify credential configuration
4. Contact the SPECULOOS data management team

---

**Last Updated**: February 2026

