from flask import Flask, render_template, jsonify, request
import os
import logging
import requests

from ha_client import HomeAssistantClient
from shelly_gen1 import ShellyGen1Client
from shelly_gen2 import ShellyGen2Client

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Get admin password from environment
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')

# Initialize HA client
ha_client = HomeAssistantClient()

# Log all requests
@app.before_request
def log_request():
    logger.info(f"Request: {request.method} {request.path}")

@app.after_request
def log_response(response):
    logger.info(f"Response: {response.status_code} for {request.path}")
    return response


def detect_generation(ip):
    """Detect if device is Gen1 or Gen2+"""
    try:
        # Try Gen2+ first
        import requests
        response = requests.get(f"http://{ip}/rpc/Shelly.GetDeviceInfo", timeout=2)
        if response.status_code == 200:
            return 2
    except:
        pass
    
    try:
        # Try Gen1
        import requests
        response = requests.get(f"http://{ip}/shelly", timeout=2)
        if response.status_code == 200:
            return 1
    except:
        pass
    
    return None


def get_shelly_client(ip, generation=None):
    """Get the appropriate Shelly client for the device"""
    if generation is None:
        generation = detect_generation(ip)
    
    if generation == 1:
        return ShellyGen1Client(ip, ADMIN_PASSWORD)
    elif generation == 2:
        return ShellyGen2Client(ip, ADMIN_PASSWORD)
    
    return None


def enrich_device_info(ha_device):
    """Enrich HA device info with live Shelly data"""
    ip = ha_device.get('ip')
    if not ip:
        logger.warning(f"No IP found for device {ha_device.get('name')}")
        return ha_device
    
    # Detect generation and get detailed info
    generation = detect_generation(ip)
    
    if generation:
        client = get_shelly_client(ip, generation)
        if client:
            device_info = client.get_device_info()
            if device_info:
                # Merge info
                ha_device.update({
                    'generation': device_info.get('generation'),
                    'auth': device_info.get('auth', False),
                    'fw': device_info.get('fw', ha_device.get('sw_version')),
                    'type': device_info.get('type', ha_device.get('model'))
                })
    
    return ha_device


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint for Home Assistant"""
    return jsonify({'status': 'ok'}), 200


@app.route('/api/debug')
def debug():
    """Debug endpoint to check HA API connection and show sample data"""
    logger.info("=== DEBUG: Testing HA API Connection ===")
    
    result = {
        'supervisor_token_present': bool(os.environ.get('SUPERVISOR_TOKEN')),
        'ha_api_reachable': False,
        'total_entities': 0,
        'shelly_entities_count': 0,
        'sample_shelly_entities': []
    }
    
    try:
        # Test basic connection
        result['ha_api_reachable'] = ha_client.test_connection()
        
        # NEW: Test WebSocket device registry access
        try:
            logger.info("Testing WebSocket device registry access...")
            device_registry = ha_client.ws_client.get_device_registry()
            result['websocket_device_registry_accessible'] = True
            result['total_devices_in_registry'] = len(device_registry)
            
            # Find Shelly devices and show their configuration_url
            shelly_devices_raw = []
            for device in device_registry[:50]:  # Check first 50 devices
                manufacturer = device.get('manufacturer', '').lower()
                if 'shelly' in manufacturer:
                    shelly_devices_raw.append(device)
            
            result['shelly_devices_in_registry'] = len(shelly_devices_raw)
            
            # Show first 3 Shelly devices with full details
            result['sample_shelly_devices_raw'] = []
            for device in shelly_devices_raw[:3]:
                result['sample_shelly_devices_raw'].append({
                    'id': device.get('id'),
                    'name': device.get('name'),
                    'manufacturer': device.get('manufacturer'),
                    'model': device.get('model'),
                    'configuration_url': device.get('configuration_url'),  # ← KEY ATTRIBUTE!
                    'sw_version': device.get('sw_version'),
                    'identifiers': device.get('identifiers'),
                    'config_entries': device.get('config_entries'),
                    'all_keys': list(device.keys())  # Show all available keys
                })
            
        except Exception as e:
            result['websocket_error'] = str(e)
            result['websocket_device_registry_accessible'] = False
        
        # Get all states
        try:
            response = requests.get(
                f'{ha_client.ha_url}/api/states',
                headers=ha_client.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                entities = response.json()
                result['total_entities'] = len(entities)
                
                # Find Shelly entities
                shelly_entities = []
                for entity in entities:
                    entity_id = entity.get('entity_id', '')
                    attributes = entity.get('attributes', {})
                    
                    if 'shelly' in entity_id.lower() or 'shelly' in attributes.get('friendly_name', '').lower():
                        shelly_entities.append(entity)
                
                result['shelly_entities_count'] = len(shelly_entities)
                
                # Show up to 3 sample entities with their full structure
                for i, entity in enumerate(shelly_entities[:3]):
                    result['sample_shelly_entities'].append({
                        'entity_id': entity.get('entity_id'),
                        'friendly_name': entity.get('attributes', {}).get('friendly_name'),
                        'state': entity.get('state'),
                        'attributes_keys': list(entity.get('attributes', {}).keys()),
                        'full_attributes': entity.get('attributes', {})
                    })
                
        except Exception as e:
            result['entities_error'] = str(e)
        
        # Try discovery
        try:
            devices = ha_client.get_shelly_devices()
            result['discovered_devices'] = len(devices)
            result['discovered_with_ip'] = sum(1 for d in devices if d.get('ip'))
            result['discovered_without_ip'] = sum(1 for d in devices if not d.get('ip'))
            
            # Show sample discovered devices
            result['sample_discovered'] = [
                {
                    'name': d.get('name'),
                    'ip': d.get('ip'),
                    'id': d.get('id'),
                    'entities': d.get('entities', [])
                }
                for d in devices[:3]
            ]
        except Exception as e:
            result['discovery_error'] = str(e)
        
    except Exception as e:
        result['error'] = str(e)
    
    logger.info(f"Debug result: {result}")
    return jsonify(result)


@app.route('/api/scan')
def scan():
    """Get Shelly devices from Home Assistant"""
    logger.info("=== SCANNING FOR DEVICES FROM HOME ASSISTANT ===")
    
    try:
        # First, test HA API connection
        if not ha_client.test_connection():
            logger.error("❌ Cannot connect to Home Assistant API")
            return jsonify({
                'error': 'Cannot connect to Home Assistant API',
                'details': 'Check add-on logs for more information'
            }), 500
        
        # Get devices from HA (now includes IP addresses from config entries)
        devices = ha_client.get_shelly_devices()
        
        logger.info(f"Found {len(devices)} devices from Home Assistant")
        
        # If we found devices, enrich them with live data
        if devices:
            enriched_devices = []
            for device in devices:
                ip = device.get('ip')
                name = device.get('name', 'Unknown')
                
                if ip:
                    logger.info(f"Enriching device: {name} at {ip}")
                    enriched = enrich_device_info(device)
                    enriched_devices.append(enriched)
                else:
                    logger.warning(f"Device {name} has no IP address - skipping enrichment")
                    # Still add it, but mark as no IP
                    device['error'] = 'No IP address found'
                    device['type'] = device.get('model', 'Unknown')
                    device['fw'] = device.get('sw_version', 'Unknown')
                    enriched_devices.append(device)
            
            logger.info(f"Returning {len(enriched_devices)} devices")
            logger.info(f"  - With IP: {sum(1 for d in enriched_devices if d.get('ip'))}")
            logger.info(f"  - Enriched: {sum(1 for d in enriched_devices if d.get('generation'))}")
            return jsonify(enriched_devices)
        else:
            logger.warning("No Shelly devices found in Home Assistant")
            return jsonify([])
        
    except Exception as e:
        logger.error(f"Error scanning devices: {e}", exc_info=True)
        return jsonify({
            'error': str(e),
            'details': 'Check add-on logs for more information'
        }), 500


@app.route('/api/device/<ip>')
def device_info(ip):
    """Get detailed info for specific device"""
    try:
        client = get_shelly_client(ip)
        if not client:
            return jsonify({'error': 'Could not detect device generation'}), 404
        
        device_info = client.get_device_info()
        if device_info:
            # Get additional info
            if hasattr(client, 'get_settings'):
                settings = client.get_settings()
                if settings and 'error' not in settings:
                    device_info['settings'] = settings
            
            status = client.get_status()
            if status:
                device_info['status'] = status
            
            return jsonify(device_info)
        
        return jsonify({'error': 'Device not found'}), 404
        
    except Exception as e:
        logger.error(f"Error getting device info for {ip}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/update/<ip>', methods=['POST'])
def update_device(ip):
    """Trigger firmware update on device"""
    logger.info("=" * 60)
    logger.info(f"FIRMWARE UPDATE REQUEST for {ip}")
    logger.info("=" * 60)
    
    try:
        client = get_shelly_client(ip)
        if not client:
            return jsonify({'error': 'Could not detect device generation'}), 404
        
        generation = client.get_device_info().get('generation') if client.get_device_info() else None
        logger.info(f"✓ Device generation: Gen{generation}")
        
        result = client.update_firmware()
        
        if result.get('success'):
            logger.info(f"✅ SUCCESS: Firmware update started")
            return jsonify(result)
        else:
            logger.error(f"❌ FAILED: {result.get('error')}")
            return jsonify(result), 500
        
    except Exception as e:
        logger.error(f"❌ EXCEPTION: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
    finally:
        logger.info("=" * 60)


@app.route('/api/auth/<ip>', methods=['POST'])
def toggle_auth(ip):
    """Toggle authentication on device with extensive debugging"""
    logger.info("=" * 60)
    logger.info(f"AUTH TOGGLE REQUEST for {ip}")
    logger.info("=" * 60)
    
    try:
        if not ADMIN_PASSWORD:
            logger.error("❌ No admin password configured in add-on settings")
            return jsonify({'error': 'Password not configured in app settings'}), 400
        
        logger.info(f"✓ Admin password is configured")
        
        data = request.get_json()
        enable = data.get('enable', False)
        logger.info(f"📝 Request: {'ENABLE' if enable else 'DISABLE'} authentication")
        
        client = get_shelly_client(ip)
        if not client:
            logger.error(f"❌ Could not detect device generation at {ip}")
            return jsonify({'error': 'Could not detect device generation'}), 404
        
        device_info = client.get_device_info()
        generation = device_info.get('generation') if device_info else None
        current_auth = device_info.get('auth', False) if device_info else False
        
        logger.info(f"✓ Device: Gen{generation}")
        logger.info(f"✓ Current auth status: {'ENABLED' if current_auth else 'DISABLED'}")
        
        result = client.set_auth(enable, ADMIN_PASSWORD)
        
        if result.get('success'):
            logger.info(f"✅ SUCCESS: Auth {'enabled' if enable else 'disabled'}")
            return jsonify({'success': True, 'auth_enabled': enable, 'response': result.get('response')})
        else:
            logger.error(f"❌ FAILED: {result.get('error')}")
            return jsonify({'error': result.get('error')}), 500
        
    except Exception as e:
        logger.error(f"❌ UNEXPECTED ERROR: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
    finally:
        logger.info("=" * 60)


@app.route('/api/reboot/<ip>', methods=['POST'])
def reboot_device(ip):
    """Reboot device"""
    try:
        client = get_shelly_client(ip)
        if not client:
            return jsonify({'error': 'Could not detect device generation'}), 404
        
        success = client.reboot()
        
        if success:
            return jsonify({'success': True, 'message': 'Device reboot initiated'})
        else:
            return jsonify({'error': 'Reboot failed'}), 500
        
    except Exception as e:
        logger.error(f"Error rebooting device {ip}: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    import sys
    
    # Get port from environment (for ingress mode) or use default
    port = int(os.environ.get('INGRESS_PORT', os.environ.get('PORT', 8099)))
    
    print("=" * 50, file=sys.stderr)
    print("Shelly HA Manager v1.0.0", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    print(f"Host: 0.0.0.0", file=sys.stderr)
    print(f"Port: {port}", file=sys.stderr)
    print(f"Admin Password: {'Configured' if ADMIN_PASSWORD else 'Not set'}", file=sys.stderr)
    print(f"Data Source: Home Assistant", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    sys.stderr.flush()
    
    # Enable debug mode for troubleshooting
    app.run(host='0.0.0.0', port=port, debug=True)
