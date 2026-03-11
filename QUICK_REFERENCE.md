# Quick Reference

## Installation

```bash
# 1. Create conda environment
conda create -n speculoos_py3 python=3.7
conda activate speculoos_py3
pip install astropy numpy

# 2. Copy credentials template
cp .credentials.csh.Io.example .credentials.csh      # or Europa, Ganymede, Callisto

# 3. Edit with your credentials
nano .credentials.csh
chmod 600 .credentials.csh

# 4. Update Python script shebangs (server only)
# Change: #!/opt/anaconda3/envs/speculoos_py3/bin/python
# To: #!/home/speculoos/Programs/anaconda2/envs/speculoos_py3/bin/python
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

## Monitoring

```bash
# View recent transfers
tail -20 Logs/transfer_log.txt

# Check for failures
cat Logs/YYYYMMDD/non_transferred

# Check cron log
tail -50 cron_logs/*_transfer_cron.log
```

## Common Issues

| Problem | Solution |
|---------|----------|
| Credentials not found | Copy `.credentials.csh.example` to `.credentials.csh` |
| Python import error | `conda activate speculoos_py3; pip install -r requirements.txt` |
| Permission denied | `chmod 600 .credentials.csh` |
| solve-field not found | Install astrometry.net or script continues without it |
| PYTHONHOME error | `unset PYTHONHOME` |

## Cron Setup

```cron
45 13 * * * csh /home/speculoos/ESO_data_transfer/Callisto_Astra/transfer_Astra.csh > /home/speculoos/ESO_data_transfer/Callisto_Astra/cron_logs/`date +\%Y-\%m-\%d_\%H:\%M:\%S`_transfer_cron.log 2>&1
```

## Emergency Procedures

```bash
# Stop transfer
ps aux | grep transfer_Astra
kill <PID>

# Clear stuck work directory
rm -rf ~/ESO_data_transfer/Callisto_Astra/workdir/*

# Reprocess specific date
./transfer_Astra.csh 20240215
```

## Support

- `INSTALLATION_GUIDE.md` - Full server deployment guide
- `DEPLOYMENT_GUIDE_TEMPLATE.md` - Multi-telescope setup
- `README.md` - Complete documentation
- `requirements.txt` - Python dependencies
