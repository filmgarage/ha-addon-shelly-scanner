# Changelog

All notable changes to this project will be documented in this file.

## [0.6.0] - 2025-10-26

### Added
- ✨ Converted to official Home Assistant add-on structure with rootfs layout
- 🐛 Extensive debug logging for authentication operations
- 📝 Detailed documentation (README.md and DOCS.md)
- 🔧 Proper s6-overlay service management

### Fixed
- 🐛 Network range configuration now properly read from settings
- 🔐 Gen1 authentication API endpoint corrected (now uses `/settings/login`)
- 🔐 Improved authentication error handling with detailed logging
- 📊 Better response handling for Shelly API calls

### Changed
- 🏗️ Restructured to use rootfs directory layout
- 🐳 Updated to use official Home Assistant Python base images
- 📦 Improved build configuration following HA standards

## [0.5.16] - Previous Version

### Features
- Network scanning for Shelly Gen1 and Gen2+ devices
- Device information display (name, type, IP, MAC, firmware)
- Authentication toggle functionality
- Firmware update triggering
- Web interface with ingress support
- Configurable admin password
- Configurable network range (non-functional in this version)

### Known Issues
- Network range configuration not being applied
- Limited debug information for authentication failures
