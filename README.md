# Home Assistant Add-on: Shelly Device Scanner

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armv7 Architecture][armv7-shield]

Scan and manage Shelly devices on your network.

## About

This add-on scans your local network for Shelly devices and displays detailed information about each discovered device. It supports both Gen1 and Gen2+ Shelly devices and provides a user-friendly web interface to view and manage your devices.

## Features

- 🔍 **Network Scanning**: Automatically discovers Shelly devices on your network
- 📊 **Device Information**: Shows device name, type, IP, MAC, firmware version, and authentication status
- 🔐 **Authentication Management**: Enable/disable authentication on your Shelly devices
- 🔄 **Firmware Updates**: Trigger firmware updates directly from the interface
- 🌐 **Multi-Generation Support**: Works with both Gen1 and Gen2+ Shelly devices
- 🎯 **Custom Network Ranges**: Scan specific IP ranges using CIDR notation
- 🐛 **Debug Logging**: Extensive logging for troubleshooting

## Installation

1. Add this repository to your Home Assistant add-on stores:
   - Go to **Settings** → **Add-ons** → **Add-on Store** → **⋮** (three dots menu) → **Repositories**
   - Add: `https://github.com/filmgarage/ha-addon-shelly-scanner`

2. Install the "Shelly Device Scanner" add-on

3. Configure the add-on (see Configuration section)

4. Start the add-on

5. Open the web UI via the sidebar or Ingress

## Configuration

### `admin_password`

The admin password configured on your Shelly devices. This is required to:
- Read detailed device settings
- Enable/disable authentication
- Trigger firmware updates

Leave empty (`""`) if your Shelly devices don't have password protection enabled.

**Example:**
```yaml
admin_password: "your_secure_password"
```

### `network_range`

The network range to scan in CIDR notation. Leave empty for auto-detection (scans the /24 subnet where Home Assistant is running).

**Examples:**
```yaml
network_range: "192.168.1.0/24"     # Scan 192.168.1.0 to 192.168.1.255
network_range: "192.168.10.0/22"    # Scan 192.168.8.0 to 192.168.11.255
network_range: "10.0.0.0/24"        # Scan 10.0.0.0 to 10.0.0.255
network_range: ""                   # Auto-detect (default)
```

## Usage

1. Open the add-on via the Home Assistant sidebar (look for the "Shelly Scanner" icon)
2. Click **"Scan Network"** to start scanning
3. View discovered devices with their information
4. Use the action buttons to:
   - 🔐 Toggle authentication
   - 🔄 Update firmware
   - 📋 View device details

## Troubleshooting

### No devices found?

- Make sure your Shelly devices are powered on and connected to the same network
- Check if your network allows device discovery (some networks block inter-device communication)
- Verify that Home Assistant and your Shelly devices are on the same subnet
- Try configuring a specific network range if auto-detection doesn't work

### Can't read device settings?

- Make sure you've entered the correct admin password in the configuration
- Verify that the password is set correctly on your Shelly devices
- Check the add-on logs for detailed error messages

### Authentication toggle not working?

- Ensure the admin password is configured in the add-on settings
- Check the add-on logs for detailed debug information
- Verify that the Shelly device is reachable
- For Gen1 devices, ensure they're running recent firmware

## Support

For issues or questions, please open an issue on [GitHub](https://github.com/filmgarage/ha-addon-shelly-scanner/issues).

## License

MIT License - see LICENSE file for details

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
