# Deployment Guide: Multi-Telescope Setup

## Overview

The `transfer_Astra.csh` script is now fully telescope-agnostic. All telescope-specific configuration is managed through the `.credentials.csh` file, making it easy to deploy the same script across all four SPECULOOS telescopes.

## Directory Structure

Each telescope should have its own directory with the following structure:

```
~/ESO_data_transfer/
├── <Telescope>_Astra/
│   ├── transfer_Astra.csh          # Generic script (same for all)
│   ├── astrometry_spirit.py        # Python scripts
│   ├── headerfix.py
│   ├── mail_alert.py
│   ├── .credentials.csh            # Telescope-specific configuration
│   ├── .env                        # Python environment variables
│   ├── Astra_mount/                # Mount point
│   ├── workdir/                    # Temporary storage
│   └── Logs/                       # Log files
```

## Quick Deployment Steps

### 1. For Each Telescope

#### Step 1: Create Directory Structure
```bash
TELESCOPE="Io"  # Change to Europa, Ganymede, or Callisto
mkdir -p ~/ESO_data_transfer/${TELESCOPE}_Astra/{Astra_mount,workdir,Logs}
cd ~/ESO_data_transfer/${TELESCOPE}_Astra
```

#### Step 2: Copy Script Files
```bash
# Copy the generic scripts (same for all telescopes)
cp /path/to/repo/transfer_Astra.csh .
cp /path/to/repo/astrometry_spirit.py .
cp /path/to/repo/headerfix.py .
cp /path/to/repo/mail_alert.py .

# Make executable
chmod +x transfer_Astra.csh
chmod +x astrometry_spirit.py
chmod +x headerfix.py
chmod +x mail_alert.py
```

#### Step 3: Create Telescope-Specific Configuration
```bash
# Copy the appropriate template for this telescope
cp /path/to/repo/.credentials.csh.${TELESCOPE}.example .credentials.csh

# Copy Python environment template
cp /path/to/repo/.env.example .env
```

#### Step 4: Edit Configuration Files
```bash
# Edit C shell credentials
nano .credentials.csh

# Edit Python environment variables
nano .env
```

**Important:** Consult your internal telescope configuration documentation for the correct values for:
- Control PC IP addresses
- Control PC passwords
- ESO directory paths
- Cambridge server paths

#### Step 5: Secure Credential Files
```bash
chmod 600 .credentials.csh
chmod 600 .env
```

### 2. Configuration Guidelines

Each telescope requires specific configuration values. Refer to your internal documentation for:

- `TELESCOPE_NAME`: Telescope identifier (Io, Europa, Ganymede, or Callisto)
- `TELESCOPE_BASE_DIR`: Base directory for telescope operations
- `ESO_DIR`: ESO archive directory path
- `CAMBRIDGE_SERVER_PATH`: Path on Cambridge server
- `CONTROL_PC_IP`: Control PC network address
- `CONTROL_PC_PASSWORD`: Control PC authentication

## Testing

### Test Configuration Loading
```bash
cd ~/ESO_data_transfer/Io_Astra  # or any telescope directory
./transfer_Astra.csh
```

The script should:
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

Create `deploy_telescope.sh` for easier deployment:

```bash
#!/bin/bash
# deploy_telescope.sh - Deploy transfer script to a telescope

if [ $# -ne 1 ]; then
    echo "Usage: $0 <Io|Europa|Ganymede|Callisto>"
    exit 1
fi

TELESCOPE=$1
BASE_DIR="$HOME/ESO_data_transfer/${TELESCOPE}_Astra"

# Create directory structure
echo "Creating directory structure for $TELESCOPE..."
mkdir -p "$BASE_DIR"/{Astra_mount,workdir,Logs}

# Copy scripts
echo "Copying scripts..."
cp transfer_Astra.csh "$BASE_DIR/"
cp astrometry_spirit.py "$BASE_DIR/"
cp headerfix.py "$BASE_DIR/"
cp mail_alert.py "$BASE_DIR/"

# Make executable
chmod +x "$BASE_DIR"/*.{csh,py}

# Copy configuration templates
echo "Setting up configuration files..."
cp ".credentials.csh.${TELESCOPE}.example" "$BASE_DIR/.credentials.csh"
cp .env.example "$BASE_DIR/.env"

# Secure credentials
chmod 600 "$BASE_DIR/.credentials.csh"
chmod 600 "$BASE_DIR/.env"

echo ""
echo "✅ Deployment complete for $TELESCOPE!"
echo ""
echo "Next steps:"
echo "  1. cd $BASE_DIR"
echo "  2. Edit .credentials.csh with actual credentials"
echo "  3. Edit .env with actual credentials"
echo "  4. Test: ./transfer_Astra.csh"
```

Usage:
```bash
chmod +x deploy_telescope.sh
./deploy_telescope.sh Io
./deploy_telescope.sh Europa
./deploy_telescope.sh Ganymede
./deploy_telescope.sh Callisto
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

## Cron Job Setup

Set up automated data transfer for each telescope:

```bash
crontab -e
```

Add entries for each telescope (adjust times as needed):
```cron
# Io - Run at 2 AM daily
0 2 * * * cd ~/ESO_data_transfer/Io_Astra && ./transfer_Astra.csh >> ~/ESO_data_transfer/Io_Astra/Logs/cron.log 2>&1

# Europa - Run at 3 AM daily
0 3 * * * cd ~/ESO_data_transfer/Europa_Astra && ./transfer_Astra.csh >> ~/ESO_data_transfer/Europa_Astra/Logs/cron.log 2>&1

# Ganymede - Run at 4 AM daily
0 4 * * * cd ~/ESO_data_transfer/Ganymede_Astra && ./transfer_Astra.csh >> ~/ESO_data_transfer/Ganymede_Astra/Logs/cron.log 2>&1

# Callisto - Run at 5 AM daily
0 5 * * * cd ~/ESO_data_transfer/Callisto_Astra && ./transfer_Astra.csh >> ~/ESO_data_transfer/Callisto_Astra/Logs/cron.log 2>&1
```

## Maintenance

### Check Transfer Status
```bash
# View recent transfers for all telescopes
for T in Io Europa Ganymede Callisto; do
    echo "=== $T ==="
    tail -5 ~/ESO_data_transfer/${T}_Astra/Logs/transfer_log.txt
done
```

### Check for Failed Transfers
```bash
# Check for non-transferred files
for T in Io Europa Ganymede Callisto; do
    LATEST=$(ls -t ~/ESO_data_transfer/${T}_Astra/Logs/*/non_transferred 2>/dev/null | head -1)
    if [ -f "$LATEST" ] && [ -s "$LATEST" ]; then
        echo "⚠️  $T has failed transfers:"
        cat "$LATEST"
    fi
done
```

### Backup Configuration
```bash
# Backup all telescope configurations
mkdir -p ~/backups/speculoos_configs
for T in Io Europa Ganymede Callisto; do
    cp ~/ESO_data_transfer/${T}_Astra/.credentials.csh \
       ~/backups/speculoos_configs/${T}_credentials.csh.backup
    cp ~/ESO_data_transfer/${T}_Astra/.env \
       ~/backups/speculoos_configs/${T}_env.backup
done
```

## Troubleshooting

### Script Can't Find Credentials
```
ERROR: Credentials file not found!
```
**Solution:** Ensure `.credentials.csh` exists in the telescope directory or in `~/.credentials.csh`

### Wrong Telescope Data Being Transferred
**Solution:** Check that `TELESCOPE_NAME` in `.credentials.csh` matches the intended telescope

### Python Scripts Not Found
```
python: can't open file 'astrometry_spirit.py'
```
**Solution:** Ensure `PYTHON_SCRIPTS_PATH` in `.credentials.csh` points to the correct directory

## Benefits of This Architecture

✅ **Single Source of Truth**: One `transfer_Astra.csh` script for all telescopes  
✅ **Easy Updates**: Update script once, deploy to all telescopes  
✅ **Isolated Configuration**: Each telescope has its own credentials  
✅ **Version Control Friendly**: Generic scripts can be committed, credentials cannot  
✅ **Reduced Errors**: Less duplication means fewer places for bugs  
✅ **Scalable**: Easy to add new telescopes in the future  

## Security Best Practices

1. **Never commit `.credentials.csh` or `.env` files**
2. **Always use `chmod 600` on credential files**
3. **Keep backups of credentials in a secure location**
4. **Regularly rotate passwords**
5. **Use different credentials for test and production environments**
6. **Consider SSH key-based authentication instead of passwords for Cambridge server**
7. **Consult internal documentation for sensitive configuration values**

## For More Information

- See `CREDENTIALS_SETUP.md` for detailed credential configuration
- See `DEPLOYMENT_CHECKLIST.md` for step-by-step deployment verification
- See `QUICK_REFERENCE.md` for daily operations reference
- Consult your internal telescope documentation for specific configuration values
