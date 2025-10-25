from flask import Flask, render_template, jsonify
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
    """Check if IP is a Shelly device and get info"""
    try:
        # Try to connect to Shelly API
        url = f"http://{ip}/shelly"
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found Shelly device at {ip}: {data.get('type')}")
            device_info = {
                'ip': ip,
                'type': data.get('type', 'Unknown'),
                'mac': data.get('mac', 'Unknown'),
                'auth': data.get('auth', False),
                'fw': data.get('fw', 'Unknown')
            }
            
            # Try to get settings if password is provided
            settings_url = f"http://{ip}/settings"
            try:
                if ADMIN_PASSWORD:
                    settings_response = requests.get(
                        settings_url,
                        auth=('admin', ADMIN_PASSWORD),
                        timeout=2
                    )
                else:
                    # Try without authentication first
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8099, debug=False)
