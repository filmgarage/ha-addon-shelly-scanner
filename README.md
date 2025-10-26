# Shelly Device Scanner Add-on for Home Assistant

WARNING: This is an early development version with basic funcionality.

⚠️ LIKELY TO BREAK FROM TIME TO TIME - USE AT OWN RISK ⚠️

This add-on scans your local network for Shelly devices and displays detailed information about each discovered device.

## Installation

1. Add this repository to your Home Assistant add-on stores:
   - Go to **Supervisor** → **Add-on Store** → **⋮** (three dots menu) → **Repositories**
   - Add: `https://github.com/filmgarage/ha-addon-shelly-scanner`
2. Install the "Shelly Device Scanner" add-on
3. Configure the add-on (optional)
4. Start the add-on
5. Open the web UI via the sidebar

## Configuration

```yaml
admin_password: "your_password"
```

### Option: `admin_password`

The admin password configured on your Shelly devices. This is required to read the device settings. If you don't set a password, the add-on can only retrieve basic information.

**Note:** Leave empty (`""`) if your Shelly devices don't have password protection enabled.

### Option: Network Range Configuration

By default, the add-on scans your local network with a /24 subnet mask (e.g., 192.168.1.0/24).

To scan a different network range:

1. Go to Settings → Add-ons → Shelly Device Scanner → Configuration
2. Enter the network range in CIDR notation, for example:
   - `192.168.10.0/24` - Scan 192.168.10.0 to 192.168.10.255
   - `192.168.10.0/22` - Scan 192.168.8.0 to 192.168.11.255 (1024 addresses)
   - `10.0.0.0/8` - Scan entire 10.x.x.x network (not recommended, very slow)

3. Leave empty to use auto-detection (default)

Examples:
- Home network: `192.168.1.0/24`
- Larger subnet: `192.168.0.0/22`
- Different IP range: `10.10.20.0/24`

## Usage

1. Open the add-on via the Home Assistant sidebar (look for the "Shelly Scanner" icon)
2. Click "Scan Network" to start scanning
3. The add-on scans the entire /24 subnet where Home Assistant is running
4. Discovered Shelly devices are displayed with their information

## Displayed Information

For each discovered Shelly device, the following information is shown:

- Device name
- Device type (e.g., SHSW-25, SHPLG-S, etc.)
- IP address
- MAC address
- Firmware version
- Authentication status

## Technical Details

- The add-on runs on port 8099
- Uses Python 3 with Flask for the web interface
- Scans all IP addresses in the /24 subnet in parallel for fast results
- Communicates with Shelly devices via their HTTP API
- Supports both Gen1 and Gen2 Shelly devices

## Troubleshooting

**No devices found?**
- Make sure your Shelly devices are powered on and connected to the same network
- Check if your network allows device discovery (some networks block inter-device communication)
- Verify that Home Assistant and your Shelly devices are on the same subnet

**Can't read device settings?**
- Make sure you've entered the correct admin password in the configuration
- Verify that the password is set correctly on your Shelly devices

## Support

For issues or questions, please open an issue on [GitHub](https://github.com/filmgarage/ha-addon-shelly-scanner/issues).

## License

MIT License
