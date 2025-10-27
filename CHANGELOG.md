# Changelog

## [0.0.7] - 2025-10-27

### 🔍 Debug Enhancement

Added detailed WebSocket device registry debugging to `/api/debug` endpoint:

- ✅ **WebSocket Device Registry Access** - Shows if WebSocket can access device registry
- ✅ **Configuration URL Visibility** - Displays `configuration_url` attribute for sample Shelly devices
- ✅ **Raw Device Data** - Shows all available attributes from device registry
- ✅ **Better Diagnostics** - Helps verify if configuration_url is accessible

### What's New in Debug Endpoint

The `/api/debug` endpoint now shows:
```json
{
  "websocket_device_registry_accessible": true/false,
  "total_devices_in_registry": 89,
  "shelly_devices_in_registry": 12,
  "sample_shelly_devices_raw": [
    {
      "id": "...",
      "name": "Living Room Light",
      "configuration_url": "http://192.168.1.100",  ← KEY!
      "manufacturer": "Allterco Robotics",
      "model": "SNSW-001X16EU",
      "all_keys": [...]  ← All available attributes
    }
  ]
}
```

This helps verify:
1. Can we access device registry via WebSocket? ✅
2. Does `configuration_url` exist? ✅
3. What other attributes are available? ✅

**Use this to diagnose if v0.0.6's approach will work!**

## [0.0.6] - 2025-10-27

### 🎯 The Real Fix: configuration_url

**What was wrong in v0.0.5**: Tried to match devices with config entries, but the matching wasn't reliable.

**The actual solution**: Device registry already has a `configuration_url` attribute that contains the full URL to each device (e.g., `http://192.168.1.100`). We just extract the IP from that!

### What's New
- ✅ **Simplified IP Extraction** - Extract IP directly from `device.configuration_url`
- ✅ **No Config Entry Matching** - Don't need to match with config entries anymore
- ✅ **More Reliable** - Uses data that's already in the device registry
- ✅ **Regex Extraction** - Robust IP pattern matching from URLs

### How It Works Now
```
1. Get device registry via WebSocket
2. For each Shelly device:
   - Get configuration_url (e.g., "http://192.168.1.100")
   - Extract IP using regex: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
   - Done! ✅
```

### Technical Details
- Removed config entries fetching (not needed)
- Simplified code significantly
- More reliable IP extraction
- Better logging for debugging

**This should finally get all 104 device IPs!** 🎉

## [0.0.5] - 2025-10-27

### 🚀 Major Change: WebSocket API Implementation

**The Problem**: In v0.0.4, 19 out of 104 devices had no IP addresses because the REST API endpoints for device registry didn't exist or weren't accessible.

**The Solution**: Switched to **WebSocket API** - the official and proper way to access Home Assistant's device registry!

### What's New
- ✅ **WebSocket Client** - New `ha_websocket.py` module for HA WebSocket API
- ✅ **Device Registry Access** - Proper access via `config/device_registry/list`
- ✅ **Config Entries Access** - Proper access via `config_entries/list`
- ✅ **Reliable Connection** - Uses the same API that Home Assistant itself uses

**Note**: v0.0.5 had the right approach (WebSocket) but wrong method (config entry matching). v0.0.6 fixes this!

## [0.0.3] - 2025-10-26

### Fixed
- 🎯 **IP Address Discovery** - Now properly retrieves IP addresses via config entries
- 📊 **Config Entries API** - Added /api/config/config_entries/list support
- 🔗 **Device Matching** - Match devices with their config entries to get IP
- 📝 **Better Logging** - Shows which devices have/don't have IP addresses

### How it works now
1. Fetch all config entries from HA
2. Filter for Shelly entries (domain: 'shelly')
3. Fetch device registry
4. Match each device with its config entry
5. Extract IP from config entry data (host field)
6. Enrich device info with live Shelly API data

This should fix the "No IP address" issue!

## [0.0.2] - 2025-10-26

### Fixed
- 🔧 **HA API Connection** - Improved Home Assistant API integration
- 📊 **Better Logging** - Extensive debug logging for troubleshooting
- 🔍 **Debug Endpoint** - Added `/api/debug` to test HA API connectivity

## [0.0.1] - 2025-10-26

### 🎉 Initial Release
- Gen1 + Gen2+ support
- Home Assistant integration
- Beautiful UI
