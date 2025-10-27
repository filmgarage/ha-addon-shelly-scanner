"""
Home Assistant API client to fetch Shelly devices
"""
import os
import requests
import logging
import re
from ha_websocket import HAWebSocketClient

logger = logging.getLogger(__name__)


class HomeAssistantClient:
    """Client to interact with Home Assistant Supervisor API"""
    
    def __init__(self):
        self.supervisor_token = os.environ.get('SUPERVISOR_TOKEN', '')
        self.ha_url = 'http://supervisor/core'
        self.headers = {
            'Authorization': f'Bearer {self.supervisor_token}',
            'Content-Type': 'application/json'
        }
        self.ws_client = HAWebSocketClient()
        
        logger.info(f"HA Client initialized. Token present: {bool(self.supervisor_token)}")
    
    def get_shelly_devices(self):
        """Get all Shelly devices from Home Assistant via WebSocket API"""
        logger.info("=" * 60)
        logger.info("FETCHING SHELLY DEVICES FROM HOME ASSISTANT")
        logger.info("=" * 60)
        
        try:
            # Get device registry via WebSocket
            logger.info("Getting device registry via WebSocket...")
            device_registry = self.ws_client.get_device_registry()
            logger.info(f"✓ Found {len(device_registry)} devices in registry")
            
            # Build device list from device registry
            shelly_devices = []
            
            for device in device_registry:
                # Check if this is a Shelly device
                identifiers = device.get('identifiers', [])
                
                # Check if it's a Shelly device by manufacturer or identifiers
                manufacturer = device.get('manufacturer', '').lower()
                is_shelly = 'shelly' in manufacturer
                
                # Also check identifiers
                if not is_shelly:
                    for identifier_pair in identifiers:
                        if isinstance(identifier_pair, list) and len(identifier_pair) >= 2:
                            if 'shelly' in str(identifier_pair[0]).lower():
                                is_shelly = True
                                break
                
                if is_shelly:
                    device_id = device.get('id')
                    name = device.get('name') or device.get('name_by_user', 'Unknown')
                    model = device.get('model', 'Unknown')
                    sw_version = device.get('sw_version', '')
                    
                    # Extract IP from configuration_url
                    ip_address = None
                    configuration_url = device.get('configuration_url', '')
                    
                    if configuration_url:
                        # Extract IP from URL like "http://192.168.1.100" or "http://192.168.1.100/"
                        # Use regex to find IP pattern
                        import re
                        ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', configuration_url)
                        if ip_match:
                            ip_address = ip_match.group(1)
                            logger.debug(f"Extracted IP {ip_address} from {configuration_url}")
                    
                    # Extract MAC address from identifiers
                    mac_address = 'Unknown'
                    for identifier_pair in identifiers:
                        if isinstance(identifier_pair, list) and len(identifier_pair) >= 2:
                            if identifier_pair[0] == 'shelly':
                                mac_address = identifier_pair[1].upper()
                                break
                    
                    device_info = {
                        'id': device_id,
                        'name': name,
                        'ip': ip_address,
                        'model': model,
                        'sw_version': sw_version,
                        'mac': mac_address,
                        'manufacturer': device.get('manufacturer', 'Shelly'),
                        'type': model,
                        'fw': sw_version,
                        'generation': None,  # Will be enriched later
                        'auth': False  # Will be enriched later
                    }
                    
                    if ip_address:
                        logger.info(f"✓ Found IP for {name}: {ip_address}")
                        shelly_devices.append(device_info)
                    else:
                        logger.warning(f"⚠ Device {name} has no configuration_url or IP")
                        logger.debug(f"  Device data: {device}")
                        # Still add it but mark as no IP
                        device_info['error'] = 'No IP address found'
                        shelly_devices.append(device_info)
            
            logger.info(f"✓ Found {len(shelly_devices)} Shelly devices")
            logger.info(f"  - With IP: {sum(1 for d in shelly_devices if d.get('ip'))}")
            logger.info(f"  - Without IP: {sum(1 for d in shelly_devices if not d.get('ip'))}")
            logger.info("=" * 60)
            
            return shelly_devices
            
        except Exception as e:
            logger.error(f"❌ Error getting Shelly devices: {e}", exc_info=True)
            logger.info("=" * 60)
            return []
    
    def test_connection(self):
        """Test if we can connect to HA API"""
        logger.info("Testing HA API connection...")
        
        try:
            response = requests.get(
                f'{self.ha_url}/api/',
                headers=self.headers,
                timeout=5
            )
            
            logger.info(f"API test response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✓ Connected to HA API")
                logger.info(f"  - Message: {data.get('message')}")
                return True
            else:
                logger.error(f"❌ API connection failed: {response.status_code}")
                return False
            
        except Exception as e:
            logger.error(f"❌ API connection error: {e}")
            return False
