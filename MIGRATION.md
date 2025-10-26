# Migration Guide: Moving to Official Add-on Structure

This document explains what changed when converting your add-on to the official Home Assistant add-on structure.

## What Changed?

### Directory Structure

**Old Structure:**
```
ha-addon-shelly-scanner/
├── app/
│   ├── app.py
│   ├── static/
│   └── templates/
├── config.yaml
├── Dockerfile
└── run.sh
```

**New Structure (Official):**
```
ha-addon-shelly-scanner/
├── .github/workflows/
│   └── builder.yml
├── rootfs/
│   ├── app/
│   │   ├── app.py
│   │   ├── static/
│   │   └── templates/
│   └── etc/
│       └── services.d/
│           └── shelly-scanner/
│               ├── run
│               └── finish
├── config.yaml
├── build.yaml
├── Dockerfile
├── README.md
├── DOCS.md
├── CHANGELOG.md
├── apparmor.txt
└── repository.yaml
```

### Key Differences

#### 1. **rootfs/ Directory**
All runtime files now go inside `rootfs/`. This directory is copied into the container at build time.

#### 2. **s6-overlay Service Management**
Instead of a simple `run.sh`, we now use s6-overlay's service directory structure:
- `rootfs/etc/services.d/shelly-scanner/run` - Starts the service
- `rootfs/etc/services.d/shelly-scanner/finish` - Handles shutdown

#### 3. **Base Image**
- **Old:** Custom Python image
- **New:** Official Home Assistant Python base images (`ghcr.io/home-assistant/*-base-python`)

#### 4. **Build Configuration**
Added `build.yaml` with proper base image references per architecture.

#### 5. **Documentation**
- `README.md` - User-facing documentation for add-on store
- `DOCS.md` - Detailed documentation shown in add-on UI
- `CHANGELOG.md` - Version history

#### 6. **Security**
Added `apparmor.txt` for proper security profiling.

## Bug Fixes Included

### 1. Network Range Configuration
**Fixed:** The `network_range` setting now properly exports to the environment variable.

**Location:** `rootfs/etc/services.d/shelly-scanner/run` line 12
```bash
export NETWORK_RANGE="${network_range}"
```

### 2. Authentication Toggle
**Fixed:** Multiple issues with authentication API:
- Gen1 now uses correct endpoint: `/settings/login` with GET parameters
- Added extensive debug logging
- Better error handling

**Location:** `rootfs/app/app.py` in the `toggle_auth()` function

### 3. Debug Logging
**Added:** Comprehensive logging for authentication operations showing:
- Request parameters (passwords hidden)
- Response status codes
- Response bodies
- Error details

## How to Deploy

### Option 1: Replace Your Repository

1. **Backup** your current repository
2. **Delete** all files except:
   - `.git/` directory
   - `README.md` (if you want to keep your custom intro)
3. **Copy** all files from `shelly-scanner-official/` to your repository
4. **Commit** and push:
   ```bash
   git add .
   git commit -m "Convert to official HA add-on structure v0.6.0"
   git push
   ```

### Option 2: Create New Repository

1. Create a new GitHub repository
2. Copy all files from `shelly-scanner-official/`
3. Initialize git and push
4. Update your Home Assistant add-on store URL

### After Deployment

Users will need to:
1. Update the repository in their add-on store (if URL changed)
2. Update the add-on to version 0.6.0
3. Restart the add-on

**Note:** Configuration is preserved during updates.

## Testing Checklist

Before releasing, test:

- [ ] Add-on builds successfully for all architectures
- [ ] Add-on starts without errors
- [ ] Network scan works
- [ ] Custom network range configuration works
- [ ] Authentication toggle works (with logging)
- [ ] Firmware update works
- [ ] Ingress mode works
- [ ] Configuration changes are applied
- [ ] Logs show proper debug information

## Benefits of New Structure

1. ✅ **Standards Compliant** - Follows Home Assistant add-on best practices
2. ✅ **Better Service Management** - s6-overlay handles crashes and restarts
3. ✅ **Improved Security** - AppArmor profiles
4. ✅ **Better Documentation** - Separate user docs and detailed docs
5. ✅ **Easier Maintenance** - Standard structure easier for contributors
6. ✅ **Official Base Images** - Better maintained and updated
7. ✅ **Bug Fixes** - Network range and authentication issues resolved

## Support

If you encounter issues during migration:

1. Check the GitHub Actions build logs
2. Verify file permissions (run and finish scripts must be executable)
3. Test locally using the Home Assistant Add-on Builder
4. Open an issue with logs and configuration details

## References

- [Home Assistant Add-on Development](https://developers.home-assistant.io/docs/add-ons)
- [Add-on Configuration](https://developers.home-assistant.io/docs/add-ons/configuration)
- [s6-overlay Documentation](https://github.com/just-containers/s6-overlay)
