from flask import Flask, render_template, jsonify, request
import socket
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress
import logging
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')

# ============================================================================
# CRITICAL: Home Assistant Ingress Support
# ============================================================================

# 1. ProxyFix - Trust headers from Home Assistant (reverse proxy)
# This MUST be applied before any request processing
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,        # X-Forwarded-For
    x_proto=1,      # X-Forwarded-Proto (http/https)
    x_host=1,       # X-Forwarded-Host
    x_prefix=1,     # X-Forwarded-Prefix (ingress path)
    x_port=1        # X-Forwarded-Port
)

# 2. Request handler for Ingress
@app.before_request
def handle_ingress_request():
    """
    Handle Home Assistant Ingress by reading X-Ingress-Path header.
    
    When accessed via ingress, Home Assistant adds:
    - X-Ingress-Path: /api/hassio_ingress/[addon-id]/
    - X-Hass-Source: ingress
    
    ProxyFix converts this to SCRIPT_NAME, which Flask uses for
    url_for() and request.script_root
    """
    ingress_path = request.headers.get('X-Ingress-Path')
    hass_source = request.headers.get('X-Hass-Source')
    
    if ingress_path:
        logger.info(f"Ingress request detected - Path: {ingress_path}")
        logger.debug(f"  Source: {hass_source}")
        logger.debug(f"  Script Root: {request.script_root}")
        logger.debug(f"  Path: {request.path}")

# 3. After request logging for debugging
@app.after_request
def log_response(response):
    """Log all responses for debugging"""
    if request.path != '/debug':  # Don't spam the log for debug endpoint
        logger.debug(f"Response: {response.status_code} {request.method} {request.path}")
    return response

# ============================================================================
# Configuration from Environment
# ============================================================================

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')
INGRESS_PORT = int(os.environ.get('INGRESS_PORT', os.environ.get('PORT', 8099)))

logger.info(f"Configuration loaded:")
logger.info(f"  Port: {INGRESS_PORT}")
logger.info(f"  Admin Password: {'Set' if ADMIN_PASSWORD else 'Not set'}")

# ============================================================================
# Shelly Device Discovery Functions
# ============================================================================

def get_local_ip():
    """Get local IP address to determine network range for scanning"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a non-routable address to determine local IP
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
        logger.info(f"Local IP detected: {ip}")
        return ip
    except Exception as e:
        logger.warning(f"Error getting local IP: {e}")
        return '127.0.0.1'
    finally:
        s.close()

def get_network_range():
    """Get network range based on local IP (assumes /24 subnet)"""
    local_ip = get_local_ip()
    network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
    logger.info(f"Scanning network range: {network}")
    return network

def check_shelly_device(ip):
    """
    Check if IP is a Shelly device and retrieve info.
    Supports both Gen1 (HTTP REST) and Gen2+ (RPC) devices.
    """
    try:
        # Try Gen2+ API (RPC-based)
        gen2_url = f"http://{ip}/rpc/Shelly.GetDeviceInfo"
        try:
            response = requests.get(gen2_url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Found Gen2 device at {ip}: {data.get('model', 'Unknown')}")
                
                device_info = {
                    'ip': ip,
                    'type': data.get('model', 'Unknown'),
                    'mac': data.get('mac', 'Unknown'),
                    'auth': data.get('auth_en', False),
                    'fw': data.get('fw_id', data.get('ver', 'Unknown')),
                    'name': data.get('name', f"Shelly {data.get('model', 'Device')}"),
                    'generation': 2
                }
                
                # Try to get additional config if authentication is needed
                if ADMIN_PASSWORD and device_info['auth']:
                    try:
                        config_url = f"http://{ip}/rpc/Shelly.GetConfig"
                        config_response = requests.get(
                            f"{config_url}?password={ADMIN_PASSWORD}",
                            timeout=2
                        )
                        if config_response.status_code == 200:
                            config = config_response.json()
                            if 'sys' in config and 'device' in config['sys']:
                                device_info['name'] = config['sys']['device'].get('name', device_info['name'])
                    except Exception as e:
                        logger.debug(f"Could not retrieve Gen2 config from {ip}: {e}")
                
                return device_info
        except Exception as e:
            logger.debug(f"Gen2 check failed for {ip}: {e}")
        
        # Try Gen1 API (HTTP-based)
        gen1_url = f"http://{ip}/shelly"
        response = requests.get(gen1_url, timeout=2)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Found Gen1 device at {ip}: {data.get('type')}")
            
            device_info = {
                'ip': ip,
                'type': data.get('type', 'Unknown'),
                'mac': data.get('mac', 'Unknown'),
                'auth': data.get('auth', False),
                'fw': data.get('fw', 'Unknown'),
                'generation': 1
            }
            
            # Try to get device name from settings
            try:
                settings_url = f"http://{ip}/settings"
                if ADMIN_PASSWORD:
                    settings_response = requests.get(
                        settings_url,
                        auth=('admin', ADMIN_PASSWORD),
                        timeout=2
                    )
                else:
                    settings_response = requests.get(settings_url, timeout=2)
                
                if settings_response.status_code == 200:
                    settings = settings_response.json()
                    device_info['name'] = settings.get('name', settings.get('device', {}).get('hostname', f"Shelly-{data.get('mac', 'Unknown')[-6:]}"))
                elif settings_response.status_code == 401:
                    device_info['name'] = '🔒 Password Required'
                else:
                    device_info['name'] = f"Shelly {data.get('type', 'Device')}"
            except Exception as e:
                logger.debug(f"Could not retrieve Gen1 settings from {ip}: {e}")
                device_info['name'] = f"Shelly {data.get('type', 'Device')}"
            
            return device_info
            
    except Exception as e:
        logger.debug(f"Device check failed for {ip}: {e}")
    
    return None

def scan_network():
    """Scan network for Shelly devices using thread pool"""
    devices = []
    network = get_network_range()
    
    logger.info(f"Starting scan of {network.num_addresses} IP addresses...")
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(check_shelly_device, str(ip)): ip 
                   for ip in network.hosts()}
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                devices.append(result)
    
    logger.info(f"Scan complete. Found {len(devices)} device(s)")
    return sorted(devices, key=lambda x: x['ip'])

# ============================================================================
# Flask Routes
# ============================================================================

@app.route('/')
def index():
    """Main page - serves the Shelly Scanner UI"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for Home Assistant"""
    return jsonify({'status': 'ok'}), 200

@app.route('/debug')
def debug_info():
    """Debug endpoint to diagnose ingress issues"""
    return jsonify({
        'status': 'ok',
        'mode': 'ingress' if request.headers.get('X-Ingress-Path') else 'direct',
        'request_info': {
            'script_root': request.script_root,
            'path': request.path,
            'base_url': request.base_url,
            'url_root': request.url_root,
            'host': request.host,
            'remote_addr': request.remote_addr,
        },
        'headers': {
            'X-Ingress-Path': request.headers.get('X-Ingress-Path', 'Not set'),
            'X-Hass-Source': request.headers.get('X-Hass-Source', 'Not set'),
            'X-Forwarded-For': request.headers.get('X-Forwarded-For', 'Not set'),
            'X-Forwarded-Proto': request.headers.get('X-Forwarded-Proto', 'Not set'),
            'X-Forwarded-Host': request.headers.get('X-Forwarded-Host', 'Not set'),
            'X-Forwarded-Prefix': request.headers.get('X-Forwarded-Prefix', 'Not set'),
        },
        'endpoints': {
            'scan': request.base_url.rstrip('/') + request.script_root.rstrip('/') + '/api/scan',
        }
    }), 200

@app.route('/api/scan')
def scan():
    """Scan network and return found Shelly devices"""
    try:
        devices = scan_network()
        return jsonify(devices), 200
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/device/<ip>')
def device_info(ip):
    """Get detailed info for a specific device"""
    try:
        device = check_shelly_device(ip)
        if device:
            return jsonify(device), 200
        return jsonify({'error': 'Device not found'}), 404
    except Exception as e:
        logger.error(f"Device info failed for {ip}: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == '__main__':
    import sys
    
    print("=" * 60, file=sys.stderr)
    print("Shelly Device Scanner - Home Assistant Add-on", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Version: 0.5.9", file=sys.stderr)
    print(f"Host: 0.0.0.0", file=sys.stderr)
    print(f"Port: {INGRESS_PORT}", file=sys.stderr)
    print(f"Admin Password: {'Configured' if ADMIN_PASSWORD else 'Not set'}", file=sys.stderr)
    print(f"Ingress Support: Enabled (X-Ingress-Path header support)", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("Access via Ingress: Home Assistant Sidebar → Shelly Scanner", file=sys.stderr)
    print("Access via Direct: http://[your-host]:{}/".format(INGRESS_PORT), file=sys.stderr)
    print("Debug Endpoint: http://[your-host]:{}/debug".format(INGRESS_PORT), file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    sys.stderr.flush()
    
    # Run Flask development server
    # For production, use WSGI server like gunicorn
    app.run(
        host='0.0.0.0',
        port=INGRESS_PORT,
        debug=False,
        threaded=True,
        use_reloader=False  # Important for add-on environment
    )
