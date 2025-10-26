# Home Assistant Add-on: Shelly Device Scanner

## Installation

Follow these steps to install the add-on:

1. Navigate in your Home Assistant frontend to **Settings** → **Add-ons** → **Add-on Store**
2. Click the menu icon (⋮) in the top right corner and select **Repositories**
3. Add the repository URL: `https://github.com/filmgarage/ha-addon-shelly-scanner`
4. Find "Shelly Device Scanner" in the add-on store and click it
5. Click on the "INSTALL" button

## Configuration

The add-on can be configured through the Configuration tab:

```yaml
admin_password: "your_password"
network_range: "192.168.1.0/24"
```

### Option: `admin_password` (optional)

The admin password configured on your Shelly devices. This password is used to authenticate when:
- Reading detailed device configuration
- Enabling/disabling authentication
- Triggering firmware updates

If your Shelly devices don't have a password set, leave this field empty.

**Note:** For Gen1 devices, the username is always "admin". Gen2+ devices only use a password without username.

### Option: `network_range` (optional)

The IP address range to scan in CIDR notation. If left empty, the add-on will automatically detect your network and scan a /24 subnet.

**Examples:**

| Network Range | Description |
|---------------|-------------|
| `192.168.1.0/24` | Scan 256 addresses (192.168.1.0 to 192.168.1.255) |
| `192.168.10.0/22` | Scan 1024 addresses (192.168.8.0 to 192.168.11.255) |
| `10.0.0.0/24` | Scan 256 addresses in 10.0.0.x range |
| (empty) | Auto-detect your network (recommended) |

**Warning:** Scanning large networks (e.g., /16 or /8) can take a very long time. Start with smaller ranges.

## How to Use

### Scanning for Devices

1. Click on "Shelly Scanner" in your Home Assistant sidebar
2. Click the **"Scan Network"** button
3. Wait for the scan to complete (usually 10-30 seconds)
4. All discovered Shelly devices will be displayed in a table

### Managing Devices

For each discovered device, you can:

- **View Details**: See device type, firmware version, IP address, MAC address, and authentication status
- **Toggle Authentication**: Enable or disable password protection (requires admin_password to be configured)
- **Update Firmware**: Trigger a firmware update to the latest stable version

### Understanding Device Information

| Field | Description |
|-------|-------------|
| Name | Device name (customizable in Shelly settings) |
| Type | Model number (e.g., SHSW-25, Shelly Plus 1PM) |
| Generation | Gen1 or Gen2+ |
| IP Address | Current IP address on your network |
| MAC Address | Hardware MAC address |
| Firmware | Current firmware version |
| Auth Status | Whether password protection is enabled |

## Network Configuration

The add-on requires `host_network: true` to properly scan your local network. This means it has access to your network interfaces, which is necessary for device discovery.

## Supported Devices

The add-on supports all Shelly devices:

### Gen1 Devices (HTTP API)
- Shelly 1, 1PM, 1L
- Shelly 2.5
- Shelly Plug, Plug S
- Shelly RGBW2
- Shelly Dimmer, Dimmer 2
- Shelly EM
- And all other Gen1 models

### Gen2+ Devices (RPC API)
- Shelly Plus 1, 1PM
- Shelly Plus 2PM
- Shelly Plus Plug S
- Shelly Pro series
- And all other Gen2+ models

## Troubleshooting

### The scan doesn't find any devices

**Possible causes:**
1. Your Shelly devices are on a different network/VLAN
2. Your network blocks multicast/broadcast traffic
3. The configured network range is incorrect

**Solutions:**
- Make sure Home Assistant and your Shelly devices are on the same network
- Try configuring a specific network range
- Check your router/firewall settings for device isolation

### Authentication toggle fails

**Possible causes:**
1. Admin password not configured in add-on settings
2. Wrong password configured
3. Device is unreachable
4. Firmware too old (Gen1 devices)

**Solutions:**
- Configure the admin password in add-on settings
- Verify the password matches what's set on the device
- Check the add-on logs for detailed error messages
- Update device firmware if using old Gen1 firmware

### Viewing the Logs

To see detailed debug information:

1. Go to **Settings** → **Add-ons** → **Shelly Device Scanner**
2. Click on the **"Log"** tab
3. Look for messages starting with:
   - `AUTH TOGGLE REQUEST` - Authentication operations
   - `ERROR` or `❌` - Error messages
   - `✓` - Successful operations

The logs show detailed information about:
- What requests are being sent
- What responses are received
- Any errors that occur

## Known Limitations

- The scan is done by checking every IP address individually, which can be slow for large networks
- Devices must be reachable over HTTP (some networks block this)
- Very old Gen1 firmware versions might not support all features
- Authentication changes require the correct admin password

## Support

If you encounter issues:

1. Check the add-on logs for error messages
2. Verify your configuration (especially admin_password and network_range)
3. Make sure your Shelly devices are reachable from Home Assistant
4. Open an issue on [GitHub](https://github.com/filmgarage/ha-addon-shelly-scanner/issues) with:
   - Your configuration (remove any passwords)
   - Relevant log excerpts
   - Device models and firmware versions
