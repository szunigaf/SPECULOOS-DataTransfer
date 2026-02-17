# DEPLOYMENT_GUIDE.md - Important Notice

## ⚠️ This File Contains Sensitive Information

The `DEPLOYMENT_GUIDE.md` file contains telescope-specific configuration values including:

- Control PC IP addresses
- Control PC passwords  
- ESO archive directory paths
- Cambridge server paths
- Network configuration details

## For Repository Users

**This file is intentionally excluded from the repository** for security reasons.

Instead, please refer to:
- **`DEPLOYMENT_GUIDE_TEMPLATE.md`** - Generic deployment procedures (safe for version control)
- **Internal telescope documentation** - Specific configuration values for your installation
- **`.credentials.csh.<Telescope>.example`** - Template configuration files

## For System Administrators

If you need to create a deployment guide with actual configuration values for internal use:

1. Copy `DEPLOYMENT_GUIDE_TEMPLATE.md` to `DEPLOYMENT_GUIDE.md`
2. Fill in the telescope-specific values from your internal documentation
3. **DO NOT commit this file to version control** (it's git-ignored)
4. Store it securely on your internal systems only
5. Restrict access to authorized personnel

## Creating Your Internal Deployment Guide

```bash
# Copy the template
cp DEPLOYMENT_GUIDE_TEMPLATE.md DEPLOYMENT_GUIDE.md

# Edit with your actual values
nano DEPLOYMENT_GUIDE.md

# Verify it's git-ignored
git status  # Should not show DEPLOYMENT_GUIDE.md

# Store securely (examples)
# - Internal wiki/documentation system
# - Secure network drive
# - Password-protected documentation repository
```

## Security Reminder

✅ **Safe for version control:**
- `DEPLOYMENT_GUIDE_TEMPLATE.md`
- `.credentials.csh.<Telescope>.example` files
- `.env.example`

❌ **Never commit to version control:**
- `DEPLOYMENT_GUIDE.md` (with actual values)
- `.credentials.csh` (with actual credentials)
- `.env` (with actual credentials)

---

For questions about obtaining the correct configuration values for your telescope installation, consult your local system administrator or internal documentation.
