# Deployment Checklist

Use this checklist when deploying the transfer scripts to a new telescope or updating existing installations.

## Pre-Deployment

### Repository Preparation
- [ ] Latest code pulled from repository
- [ ] All scripts tested locally
- [ ] Documentation reviewed and up-to-date
- [ ] Template files verified (`.example` files)

### System Requirements
- [ ] Python 2.7+ installed
- [ ] `python-dotenv` package installed (`pip install python-dotenv`)
- [ ] C shell (csh) available
- [ ] Mount utilities available
- [ ] sshpass installed (for Cambridge server transfers)
- [ ] Network access to:
  - [ ] Windows Control PC
  - [ ] ESO archive directory
  - [ ] Cambridge server
  - [ ] SMTP server

## Telescope Setup

### Directory Structure
- [ ] Base directory created: `~/ESO_data_transfer/<Telescope>_Astra/`
- [ ] Subdirectories created:
  - [ ] `Astra_mount/`
  - [ ] `workdir/`
  - [ ] `Logs/`

### Script Files
- [ ] `transfer_Astra.csh` copied and executable (`chmod +x`)
- [ ] `astrometry_spirit.py` copied and executable (`chmod +x`)
- [ ] `headerfix.py` copied and executable (`chmod +x`)
- [ ] `mail_alert.py` copied and executable (`chmod +x`)

### Configuration Files

#### C Shell Configuration (.credentials.csh)
- [ ] Appropriate template copied for telescope:
  - [ ] `.credentials.csh.Io.example` → `.credentials.csh` (for Io)
  - [ ] `.credentials.csh.Europa.example` → `.credentials.csh` (for Europa)
  - [ ] `.credentials.csh.Ganymede.example` → `.credentials.csh` (for Ganymede)
  - [ ] `.credentials.csh.example` → `.credentials.csh` (for Callisto)
- [ ] Edited with actual credentials
- [ ] Verified telescope-specific settings:
  - [ ] `TELESCOPE_NAME` correct
  - [ ] `TELESCOPE_BASE_DIR` correct
  - [ ] `ESO_DIR` matches telescope (lowercase)
  - [ ] `CAMBRIDGE_SERVER_PATH` includes correct telescope name
  - [ ] `CONTROL_PC_IP` correct for telescope
  - [ ] `CONTROL_PC_PASSWORD` correct for telescope
- [ ] File permissions set: `chmod 600 .credentials.csh`

#### Python Configuration (.env)
- [ ] `.env.example` copied to `.env`
- [ ] Edited with actual credentials:
  - [ ] SMTP server configured
  - [ ] Email credentials set
  - [ ] Sender/recipient emails configured
- [ ] File permissions set: `chmod 600 .env`

## Testing

### Configuration Testing
- [ ] Script loads credentials without errors:
  ```bash
  ./transfer_Astra.csh
  ```
- [ ] Environment variables correctly set:
  ```bash
  echo $TELESCOPE_NAME
  echo $ESO_DIR
  echo $ACP_LOCAL_PATH
  ```
- [ ] Telescope name displays correctly in script output

### Connectivity Testing
- [ ] Control PC mount successful
  ```bash
  mount ${ACP_LOCAL_PATH}
  ls ${ACP_LOCAL_PATH}
  ```
- [ ] ESO directory accessible
  ```bash
  ls -la ${ESO_DIR}
  ```
- [ ] Cambridge server accessible
  ```bash
  ssh ${CAMBRIDGE_SERVER_USER}@${CAMBRIDGE_SERVER_HOST}
  ```

### Email Testing
- [ ] Email alert sends successfully:
  ```bash
  python mail_alert.py TestTelescope 0
  ```
- [ ] Email received at configured address

### Data Transfer Testing
- [ ] Test with old/sample data:
  ```bash
  ./transfer_Astra.csh YYYYMMDD
  ```
- [ ] Verify steps complete:
  - [ ] Files copied from control PC
  - [ ] Astrometry processing runs
  - [ ] Headers fixed correctly
  - [ ] Files appear in ESO directory
  - [ ] Logs created properly
  - [ ] Work directory cleaned up

## Production Deployment

### Cron Job Setup
- [ ] Crontab entry created
- [ ] Correct time scheduled (stagger across telescopes)
- [ ] Log file path correct
- [ ] Test cron job runs successfully

### Monitoring Setup
- [ ] Log rotation configured (if applicable)
- [ ] Alert recipient list verified
- [ ] Monitoring script/dashboard updated (if applicable)

### Documentation
- [ ] Local README created (if needed)
- [ ] Operations team notified
- [ ] Contact information updated
- [ ] Troubleshooting guide accessible

## Post-Deployment

### First Week Monitoring
- [ ] Day 1: Check transfer completed successfully
- [ ] Day 2: Verify logs are updating
- [ ] Day 3: Confirm files in ESO archive
- [ ] Day 7: Review weekly statistics

### Verification Checklist
- [ ] No non-transferred files in logs
- [ ] Email alerts working correctly
- [ ] Cambridge server receiving logs
- [ ] ESO archive receiving data
- [ ] Disk space sufficient in work directories

## Security Audit

### Credentials
- [ ] `.credentials.csh` NOT in version control
- [ ] `.env` NOT in version control
- [ ] `.credentials.csh` has mode 600
- [ ] `.env` has mode 600
- [ ] Passwords documented in secure location
- [ ] Access restricted to authorized personnel only

### File Permissions
- [ ] Script directory permissions appropriate
- [ ] Log directory permissions appropriate
- [ ] Mount point permissions appropriate
- [ ] ESO directory permissions appropriate

## Rollback Plan

### Issues Encountered
If deployment fails, follow these steps:

1. **Stop automated transfers**
   ```bash
   crontab -e  # Comment out the line
   ```

2. **Preserve logs**
   ```bash
   cp -r Logs Logs.backup.$(date +%Y%m%d)
   ```

3. **Revert to previous version** (if applicable)
   ```bash
   git checkout <previous-commit>
   ```

4. **Document issues**
   - Error messages
   - Failed steps
   - System state

5. **Notify team**
   - Operations team
   - Data management team
   - PI (if necessary)

## Sign-Off

### Deployed By
- Name: ________________
- Date: ________________
- Telescope: ________________

### Verified By
- Name: ________________
- Date: ________________

### Additional Notes
```
[Space for deployment notes, issues encountered, or special configurations]






```

---

## Reference: Telescope-Specific Values

For telescope-specific configuration values, consult:

1. **Internal telescope documentation** - Contains sensitive values like:
   - Control PC IP addresses
   - Control PC passwords
   - ESO archive directories
   - Cambridge server paths

2. **Template files in repository**:
   - `.credentials.csh.<Telescope>.example` - Configuration templates
   - `DEPLOYMENT_GUIDE_TEMPLATE.md` - Deployment procedures

**Note:** These values are considered sensitive and should not be committed to version control.
