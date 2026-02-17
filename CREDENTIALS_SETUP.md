# Credentials Setup Guide

## Overview

This repository now uses environment variables to manage sensitive credentials instead of hardcoding them in scripts. This improves security and makes it easier to manage different configurations.

## Setup Instructions

### For Python Scripts (mail_alert.py)

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your actual credentials:**
   ```bash
   nano .env  # or use your preferred editor
   ```

3. **Update the following values:**
   - `SMTP_LOGIN`: Your email username
   - `SMTP_PASSWORD`: Your email password
   - `EMAIL_FROM`: Your sender email address
   - `EMAIL_TO`: Recipient email address
   - `CAMBRIDGE_SERVER_PASSWORD`: SSH password for Cambridge server

### For C Shell Scripts (transfer_Astra.csh)

1. **Choose the appropriate template for your telescope:**
   ```bash
   # For Io telescope:
   cp .credentials.csh.Io.example .credentials.csh
   
   # For Europa telescope:
   cp .credentials.csh.Europa.example .credentials.csh
   
   # For Ganymede telescope:
   cp .credentials.csh.Ganymede.example .credentials.csh
   
   # For Callisto telescope:
   cp .credentials.csh.example .credentials.csh
   ```

2. **Edit `.credentials.csh` and add your actual credentials:**
   ```bash
   nano .credentials.csh  # or use your preferred editor
   ```
   
   **Important:** Verify that `TELESCOPE_NAME`, `ESO_DIR`, and `CAMBRIDGE_SERVER_PATH` match your telescope.

3. **Make the file readable only by you:**
   ```bash
   chmod 600 .credentials.csh
   ```

4. **The script automatically loads credentials** - no manual changes needed to `transfer_Astra.csh`!

## Security Best Practices

### ✅ DO:
- Keep `.env` and `.credentials.csh` files **local only**
- Use `.env.example` and `.credentials.csh.example` as templates (these can be committed)
- Set restrictive file permissions: `chmod 600 .env .credentials.csh`
- Regularly rotate passwords
- Use different credentials for development and production

### ❌ DON'T:
- **NEVER** commit `.env` or `.credentials.csh` to version control
- **NEVER** share these files via email or messaging
- **NEVER** store credentials in plaintext in scripts

## File Permissions

Set appropriate permissions after creating your credential files:

```bash
chmod 600 .env
chmod 600 .credentials.csh
chmod 644 .env.example
chmod 644 .credentials.csh.example
```

## Migration Guide

### Python: mail_alert.py

**Before:**
```python
sendemail(from_addr='lcd44@cam.ac.uk',
          to_addr_list=['lcd44@cam.ac.uk'],
          cc_addr_list=[],
          subject=str("Issue..."),
          message=str(num_bad_files + "..."),
          login='lcd44',
          password='noelia207')
```

**After:**
```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sendemail(from_addr=os.getenv('EMAIL_FROM'),
          to_addr_list=[os.getenv('EMAIL_TO')],
          cc_addr_list=[],
          subject=str("Issue..."),
          message=str(num_bad_files + "..."),
          login=os.getenv('SMTP_LOGIN'),
          password=os.getenv('SMTP_PASSWORD'))
```

**Install python-dotenv:**
```bash
pip install python-dotenv
```

### C Shell: transfer_Astra.csh

**Add at the beginning of the script (after shebang):**
```csh
#!/bin/csh

# Load credentials
if (-f ~/.credentials.csh) then
    source ~/.credentials.csh
else if (-f ./.credentials.csh) then
    source ./.credentials.csh
else
    echo "ERROR: Credentials file not found!"
    echo "Please copy .credentials.csh.example to .credentials.csh and configure it."
    exit 1
endif

# Rest of the script...
```

**Then replace hardcoded values with environment variables:**

```csh
# Before:
set acp_control_pc_path="//speculoos:c0ntrolPC-04@172.16.0.202/Documents/astra/images/"

# After:
set acp_control_pc_path="//${CONTROL_PC_USER}:${CONTROL_PC_PASSWORD}@${CONTROL_PC_IP}${CONTROL_PC_PATH}"
```

```csh
# Before:
sshpass -p 'eij7iaXi' scp $logfile $appcg_path

# After:
sshpass -p "${CAMBRIDGE_SERVER_PASSWORD}" scp $logfile $appcg_path
```

## Environment Variables Reference

### Python (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `SMTP_SERVER` | SMTP server and port | `smtp.hermes.cam.ac.uk:587` |
| `SMTP_LOGIN` | Email login username | `lcd44` |
| `SMTP_PASSWORD` | Email password | `***` |
| `EMAIL_FROM` | Sender email address | `lcd44@cam.ac.uk` |
| `EMAIL_TO` | Recipient email address | `lcd44@cam.ac.uk` |
| `EMAIL_CC` | CC recipients (optional) | `user1@cam.ac.uk,user2@cam.ac.uk` |
| `CAMBRIDGE_SERVER_PASSWORD` | SSH password | `***` |

### C Shell (.credentials.csh)

| Variable | Description | Example |
|----------|-------------|---------|
| `TELESCOPE_NAME` | Telescope name | `Io`, `Europa`, `Ganymede`, or `Callisto` |
| `TELESCOPE_BASE_DIR` | Base directory for telescope | `~/ESO_data_transfer/Io_Astra` |
| `ACP_LOCAL_PATH` | Mount point for control PC | `${TELESCOPE_BASE_DIR}/Astra_mount` |
| `DATA_DIR` | Work directory for temp storage | `${TELESCOPE_BASE_DIR}/workdir` |
| `LOG_DIR` | Log directory | `${TELESCOPE_BASE_DIR}/Logs` |
| `ESO_DIR` | ESO archive directory | `/home/eso/data_transfer/io` |
| `PYTHON_SCRIPTS_PATH` | Path to Python scripts | `${TELESCOPE_BASE_DIR}` |
| `CAMBRIDGE_SERVER_USER` | Cambridge server username | `speculoos` |
| `CAMBRIDGE_SERVER_HOST` | Cambridge server hostname | `appcs.ra.phy.cam.ac.uk` |
| `CAMBRIDGE_SERVER_PASSWORD` | SSH password | `***` |
| `CAMBRIDGE_SERVER_PATH` | Remote path on Cambridge server | `/appct/data/.../Io/.` |
| `CONTROL_PC_USER` | Windows control PC username | `speculoos` |
| `CONTROL_PC_PASSWORD` | Windows control PC password | `c0ntrolPC-01` (varies by telescope) |
| `CONTROL_PC_IP` | Control PC IP address | `172.16.0.201` (varies by telescope) |
| `CONTROL_PC_PATH` | Path on control PC | `/Documents/astra/images/` |
| `SMTP_*` and `EMAIL_*` | Email configuration | (same as Python) |

## Troubleshooting

### "Credentials file not found"
- Ensure you've copied `.credentials.csh.example` to `.credentials.csh`
- Check the file is in the correct directory (script directory or home directory)

### "Permission denied"
- Run: `chmod 600 .credentials.csh`

### Python can't load .env
- Install python-dotenv: `pip install python-dotenv`
- Ensure `.env` is in the same directory as the Python script

### Variables not being loaded
- C Shell: Ensure you're using `source .credentials.csh`, not running it directly
- Python: Ensure `load_dotenv()` is called before accessing variables

## Additional Security Considerations

### Alternative: SSH Key-Based Authentication
For Cambridge server access, consider using SSH keys instead of passwords:

```bash
ssh-keygen -t ed25519 -C "speculoos@cambridge"
ssh-copy-id speculoos@appcs.ra.phy.cam.ac.uk
```

Then remove the password from `sshpass` and use direct `scp` commands.

### Password Manager Integration
Consider using a password manager or secrets management tool like:
- HashiCorp Vault
- AWS Secrets Manager
- 1Password CLI
- Pass (the standard Unix password manager)

## Support

If you encounter issues with credential setup, please:
1. Check file permissions
2. Verify environment variable names match exactly
3. Ensure no extra whitespace in credential files
4. Test with example values first
