"""
Home Assistant WebSocket API client
Used to fetch device registry and config entries
"""
import json
import logging
import os
import websocket

logger = logging.getLogger(__name__)


class HAWebSocketClient:
    """Client to interact with Home Assistant via WebSocket"""
    
    def __init__(self):
        self.supervisor_token = os.environ.get('SUPERVISOR_TOKEN', '')
        self.ws_url = 'ws://supervisor/core/websocket'
        self.message_id = 0
        
    def _get_next_id(self):
        """Get next message ID"""
        self.message_id += 1
        return self.message_id
    
    def _send_message(self, ws, message):
        """Send a message and return the response"""
        msg_json = json.dumps(message)
        logger.debug(f"Sending: {msg_json}")
        ws.send(msg_json)
        
        # Receive response
        result = ws.recv()
        logger.debug(f"Received: {result[:200]}...")
        return json.loads(result)
    
    def get_device_registry(self):
        """Get device registry from Home Assistant via WebSocket"""
        logger.info("Connecting to HA WebSocket API for device registry...")
        
        try:
            # Connect to WebSocket
            ws = websocket.create_connection(self.ws_url, timeout=10)
            
            # Step 1: Receive auth_required
            auth_required = json.loads(ws.recv())
            if auth_required.get('type') != 'auth_required':
                logger.error(f"Unexpected message: {auth_required}")
                ws.close()
                return []
            
            logger.debug("✓ Auth required received")
            
            # Step 2: Send authentication
            auth_msg = {
                'type': 'auth',
                'access_token': self.supervisor_token
            }
            ws.send(json.dumps(auth_msg))
            
            # Step 3: Receive auth result
            auth_result = json.loads(ws.recv())
            if auth_result.get('type') != 'auth_ok':
                logger.error(f"Authentication failed: {auth_result}")
                ws.close()
                return []
            
            logger.info("✓ WebSocket authenticated")
            
            # Step 4: Request device registry
            device_request = {
                'id': self._get_next_id(),
                'type': 'config/device_registry/list'
            }
            response = self._send_message(ws, device_request)
            
            # Step 5: Parse response
            if response.get('success'):
                devices = response.get('result', [])
                logger.info(f"✓ Got {len(devices)} devices from WebSocket")
                ws.close()
                return devices
            else:
                logger.error(f"Failed to get device registry: {response}")
                ws.close()
                return []
            
        except Exception as e:
            logger.error(f"WebSocket error getting device registry: {e}", exc_info=True)
            return []
    
    def get_config_entries(self):
        """Get config entries from Home Assistant via WebSocket"""
        logger.info("Connecting to HA WebSocket API for config entries...")
        
        try:
            # Connect to WebSocket
            ws = websocket.create_connection(self.ws_url, timeout=10)
            
            # Step 1: Receive auth_required
            auth_required = json.loads(ws.recv())
            if auth_required.get('type') != 'auth_required':
                logger.error(f"Unexpected message: {auth_required}")
                ws.close()
                return []
            
            # Step 2: Send authentication
            auth_msg = {
                'type': 'auth',
                'access_token': self.supervisor_token
            }
            ws.send(json.dumps(auth_msg))
            
            # Step 3: Receive auth result
            auth_result = json.loads(ws.recv())
            if auth_result.get('type') != 'auth_ok':
                logger.error(f"Authentication failed: {auth_result}")
                ws.close()
                return []
            
            logger.info("✓ WebSocket authenticated")
            
            # Step 4: Request config entries
            entries_request = {
                'id': self._get_next_id(),
                'type': 'config_entries/list'
            }
            response = self._send_message(ws, entries_request)
            
            # Step 5: Parse response
            if response.get('success'):
                entries = response.get('result', [])
                logger.info(f"✓ Got {len(entries)} config entries from WebSocket")
                ws.close()
                return entries
            else:
                logger.error(f"Failed to get config entries: {response}")
                ws.close()
                return []
            
        except Exception as e:
            logger.error(f"WebSocket error getting config entries: {e}", exc_info=True)
            return []
