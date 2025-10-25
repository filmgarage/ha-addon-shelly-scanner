from flask import Flask, render_template, jsonify, request
import socket
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress

app = Flask(__name__, static_folder='static', static_url_path='/static')

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')

def get_local_ip():
    """Get local IP address to determine network range"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
        print(f"Local IP detected: {ip}")
    except Exception as e:
        print(f"Error getting local IP: {e}")
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def get_network_range():
    """Get network range based on local IP"""
    local_ip = get_local_ip()
    # Assume /24 network
    network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
    print(f"Scanning network range: {network}")
    return network

def check_shelly_device(ip):
    """Check if IP is a Shelly device and get info. Supports both Gen1 and Gen2+ devices."""
    try:
        # First try Gen2+ API (RPC-based)
        gen2_url = f"http://{ip}/rpc/Shelly.GetDeviceInfo"
        try:
            response = requests.get(gen2_url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"Found Gen2 Shelly device at {ip}: {data.get('model', 'Unknown')}")
                
                device_info = {
                    'ip': ip,
                    'type': data.get('model', 'Unknown'),
                    'mac': data.get('mac', 'Unknown'),
                    'auth': data.get('auth_en', False),
                    'fw': data.get('fw_id', data.get('ver', 'Unknown')),
                    'name': data.get('name', f"Shelly {data.get('model', 'Device')}"),
                    'generation': 2
                }
                
                # Try to get additional config if available (Gen2+ only uses password, no username)
                if ADMIN_PASSWORD and device_info['auth']:
                    config_url = f"http://{ip}/rpc/Shelly.GetConfig"
                    try:
                        # Gen2+ uses only password in query string, no username needed
                        config_response = requests.get(
                            f"{config_url}?password={ADMIN_PASSWORD}",
                            timeout=2
                        )
                        if config_response.status_code == 200:
                            config = config_response.json()
                            if 'sys' in config and 'device' in config['sys']:
                                device_info['name'] = config['sys']['device'].get('name', device_info['name'])
                    except:
                        pass
                
                return device_info
        except:
            pass
        
        # Try Gen1 API (HTTP-based)
        gen1_url = f"http://{ip}/shelly"
        response = requests.get(gen1_url, timeout=2)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found Gen1 Shelly device at {ip}: {data.get('type')}")
            device_info = {
                'ip': ip,
                'type': data.get('type', 'Unknown'),
                'mac': data.get('mac', 'Unknown'),
                'auth': data.get('auth', False),
                'fw': data.get('fw', 'Unknown'),
                'generation': 1
            }
            
            # Try to get settings (Gen1 uses 'admin' username)
            settings_url = f"http://{ip}/settings"
            try:
                if ADMIN_PASSWORD:
                    # Gen1 requires username 'admin' and password
                    settings_response = requests.get(
                        settings_url,
                        auth=('admin', ADMIN_PASSWORD),
                        timeout=2
                    )
                else:
                    # Try without authentication
                    settings_response = requests.get(settings_url, timeout=2)
                
                if settings_response.status_code == 200:
                    settings = settings_response.json()
                    device_info['name'] = settings.get('name', settings.get('device', {}).get('hostname', f"Shelly-{data.get('mac', 'Unknown')[-6:]}"))
                    device_info['device'] = settings.get('device', {})
                elif settings_response.status_code == 401:
                    device_info['name'] = '🔒 Password Required'
                else:
                    device_info['name'] = f"Shelly {data.get('type', 'Device')}"
            except requests.exceptions.Timeout:
                device_info['name'] = f"Shelly {data.get('type', 'Device')}"
            except Exception as e:
                device_info['name'] = f"Shelly {data.get('type', 'Device')}"
                
            return device_info
    except Exception as e:
        pass
    return None

def scan_network():
    """Scan network for Shelly devices"""
    devices = []
    network = get_network_range()
    
    print(f"Starting scan of {network.num_addresses} IP addresses...")
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(check_shelly_device, str(ip)): ip 
                   for ip in network.hosts()}
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                devices.append(result)
    
    print(f"Scan complete. Found {len(devices)} Shelly device(s)")
    return sorted(devices, key=lambda x: x['ip'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scan')
def scan():
    devices = scan_network()
    return jsonify(devices)

@app.route('/api/device/<ip>')
def device_info(ip):
    """Get detailed info for specific device"""
    device = check_shelly_device(ip)
    if device:
        return jsonify(device)
    return jsonify({'error': 'Device not found'}), 404

@app.route('/api/update/<ip>', methods=['POST'])
def update_device(ip):
    """Trigger firmware update on device"""
    try:
        # First detect which generation
        device = check_shelly_device(ip)
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        if device['generation'] == 2:
            # Gen2+ update via RPC
            update_url = f"http://{ip}/rpc/Shelly.Update"
            params = {'stage': 'stable'}
            if ADMIN_PASSWORD:
                params['password'] = ADMIN_PASSWORD
            
            response = requests.post(update_url, json=params, timeout=5)
            if response.status_code == 200:
                return jsonify({'success': True, 'message': 'Update started'})
        else:
            # Gen1 update
            update_url = f"http://{ip}/ota?update=true"
            if ADMIN_PASSWORD:
                response = requests.get(update_url, auth=('admin', ADMIN_PASSWORD), timeout=5)
            else:
                response = requests.get(update_url, timeout=5)
            
            if response.status_code == 200:
                return jsonify({'success': True, 'message': 'Update started'})
        
        return jsonify({'error': 'Update failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/<ip>', methods=['POST'])
def toggle_auth(ip):
    """Toggle authentication on device"""
    try:
        if not ADMIN_PASSWORD:
            return jsonify({'error': 'Password not configured in app settings'}), 400
        
        data = request.get_json()
        enable = data.get('enable', False)
        
        # First detect which generation
        device = check_shelly_device(ip)
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        if device['generation'] == 2:
            # Gen2+ auth toggle via RPC
            config_url = f"http://{ip}/rpc/Sys.SetConfig"
            params = {
                'config': {
                    'auth': {
                        'enable': enable,
                        'user': 'admin',
                        'pass': ADMIN_PASSWORD if enable else ''
                    }
                }
            }
            
            # Current password needed if auth is currently enabled
            if device['auth']:
                params['password'] = ADMIN_PASSWORD
            
            response = requests.post(config_url, json=params, timeout=5)
            if response.status_code == 200:
                return jsonify({'success': True, 'auth_enabled': enable})
        else:
            # Gen1 auth toggle
            settings_url = f"http://{ip}/settings"
            params = {
                'login': {
                    'enabled': enable,
                    'username': 'admin',
                    'password': ADMIN_PASSWORD if enable else ''
                }
            }
            
            # Use current auth if enabled
            if device['auth']:
                response = requests.post(settings_url, json=params, auth=('admin', ADMIN_PASSWORD), timeout=5)
            else:
                response = requests.post(settings_url, json=params, timeout=5)
            
            if response.status_code == 200:
                return jsonify({'success': True, 'auth_enabled': enable})
        
        return jsonify({'error': 'Failed to change authentication'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8099, debug=False)
