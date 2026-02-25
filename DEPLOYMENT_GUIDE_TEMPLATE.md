# Deployment Guide: Multi-Telescope Setup

## Overview

`transfer_Astra.csh` is telescope-agnostic. All telescope-specific configuration is managed through `.credentials.csh`.

## Directory Structure

```
~/ESO_data_transfer/
├── <Telescope>_Astra/
│   ├── transfer_Astra.csh          # Same for all telescopes
│   ├── astrometry_spirit.py        # Python scripts
│   ├── headerfix.py
│   ├── mail_alert.py
│   ├── .credentials.csh            # Telescope-specific
│   ├── .env                        # Email credentials
│   ├── Astra_mount/                # Mount point
│   ├── workdir/                    # Temporary storage
│   └── Logs/                       # Log files
```

## Deployment Steps

### 1. Create Structure
```bash
TELESCOPE="Io"  # Change to Europa, Ganymede, or Callisto
mkdir -p ~/ESO_data_transfer/${TELESCOPE}_Astra/{Astra_mount,workdir,Logs,cron_logs}
cd ~/ESO_data_transfer/${TELESCOPE}_Astra
```

### 2. Copy Scripts
```bash
cp /path/to/repo/transfer_Astra.csh .
cp /path/to/repo/astrometry.py .      # or astrometry_spirit.py for Callisto
cp /path/to/repo/headerfix.py .
cp /path/to/repo/mail_alert.py .
chmod +x *.{csh,py}
```

### 3. Configure Credentials
```bash
cp /path/to/repo/.credentials.csh.${TELESCOPE}.example .credentials.csh
cp /path/to/repo/.env.example .env
nano .credentials.csh  # Edit with actual values
nano .env              # Edit email settings
chmod 600 .credentials.csh .env
```

### 4. Test
```bash
./transfer_Astra.csh
```
1. ✅ Successfully load `.credentials.csh`
2. ✅ Display the correct telescope name
3. ✅ Attempt to mount the correct control PC path

### Verify Environment Variables
After running the script, check that variables are set correctly:
```bash
echo $TELESCOPE_NAME
echo $ESO_DIR
echo $ACP_LOCAL_PATH
```

## Automated Deployment Script

```bash
#!/bin/bash
# deploy_telescope.sh

TELESCOPE=$1
[ -z "$TELESCOPE" ] && { echo "Usage: $0 <Io|Europa|Ganymede|Callisto>"; exit 1; }

BASE_DIR="$HOME/ESO_data_transfer/${TELESCOPE}_Astra"
mkdir -p "$BASE_DIR"/{Astra_mount,workdir,Logs,cron_logs}
cp transfer_Astra.csh astrometry*.py headerfix.py mail_alert.py "$BASE_DIR/"
chmod +x "$BASE_DIR"/*.{csh,py}
cp ".credentials.csh.${TELESCOPE}.example" "$BASE_DIR/.credentials.csh"
cp .env.example "$BASE_DIR/.env"
chmod 600 "$BASE_DIR"/{.credentials.csh,.env}

echo "✅ Deployed $TELESCOPE. Edit credentials in $BASE_DIR"
```

## Updating Scripts

When you update the generic scripts, you only need to copy them to each telescope directory:

```bash
#!/bin/bash
# update_all_telescopes.sh

for TELESCOPE in Io Europa Ganymede Callisto; do
    echo "Updating $TELESCOPE..."
    cp transfer_Astra.csh ~/ESO_data_transfer/${TELESCOPE}_Astra/
    cp astrometry_spirit.py ~/ESO_data_transfer/${TELESCOPE}_Astra/
    cp headerfix.py ~/ESO_data_transfer/${TELESCOPE}_Astra/
    cp mail_alert.py ~/ESO_data_transfer/${TELESCOPE}_Astra/
    chmod +x ~/ESO_data_transfer/${TELESCOPE}_Astra/*.{csh,py}
done

echo "✅ All telescopes updated!"
```

## Cron Setup

```bash
crontab -e
```

Example (adjust time and telescope):
```cron
45 13 * * * csh /home/speculoos/ESO_data_transfer/Callisto_Astra/transfer_Astra.csh > /home/speculoos/ESO_data_transfer/Callisto_Astra/cron_logs/`date +\%Y-\%m-\%d_\%H:\%M:\%S`_transfer_cron.log 2>&1
```

## Maintenance

### Check Transfer Status
## Updating Scripts
## Monitoring

```bash
# Recent transfers (all telescopes)
for T in Io Europa Ganymede Callisto; do
    echo "=== $T ==="
    tail -5 ~/ESO_data_transfer/${T}_Astra/Logs/transfer_log.txt
done

# Check failures
for T in Io Europa Ganymede Callisto; do
    [ -s ~/ESO_data_transfer/${T}_Astra/Logs/*/non_transferred ] && \
        echo "⚠️ $T has failed transfers"
done
```hon: can't open file 'astrometry_spirit.py'
```
**Solution:** Ensure `PYTHON_SCRIPTS_PATH` in `.credentials.csh` points to the correct directory

## Benefits of This Architecture

✅ **Single Source of Truth**: One `transfer_Astra.csh` script for all telescopes  
✅ **Easy Updates**: Update script once, deploy to all telescopes  
✅ **Isolated Configuration**: Each telescope has its own credentials  
✅ **Version Control Friendly**: Generic scripts can be committed, credentials cannot  
## Troubleshooting

| Issue | Solution |
|-------|----------|
| Credentials not found | Ensure `.credentials.csh` exists in telescope directory |
| Wrong telescope data | Check `TELESCOPE_NAME` in `.credentials.csh` |
| Python scripts not found | Verify `PYTHON_SCRIPTS_PATH` in `.credentials.csh` |

## Benefits

- Single script for all telescopes
- Easy updates (one place to change)
- Isolated credentials per telescope
- Version control friendly
- Scalable for new telescopes## Security

- Never commit `.credentials.csh` or `.env`
- Always use `chmod 600` on credentials
- Keep backups in secure location
- Rotate passwords regularly