import paho.mqtt.client as mqtt
import json
import threading
import time
from datetime import datetime
import logging
from queue import Queue
import ssl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MQTTHandler:
    def __init__(self, broker_host="localhost", broker_port=1883, username=None, password=None):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        
        # MQTT Client setup
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe
        
        # Security (if using TLS)
        # self.client.tls_set(ca_certs="ca.crt", 
        #                    certfile="client.crt", 
        #                    keyfile="client.key")
        
        if username and password:
            self.client.username_pw_set(username, password)
        
        # Message queue for processing
        self.message_queue = Queue()
        
        # Connected devices tracking
        self.connected_devices = {}
        self.device_status = {}
        self.command_callbacks = {}
        
        # Start message processor thread
        self.processor_thread = threading.Thread(target=self.process_messages, daemon=True)
        self.processor_thread.start()
        
        # Topics structure
        self.topics = {
            'device_data': 'iot/+/data',
            'device_status': 'iot/+/status',
            'device_events': 'iot/+/events',
            'command_response': 'iot/+/response',
            'network_scan': 'iot/scan/result',
            'gateway_announce': 'iot/gateway/announce'
        }
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback when MQTT client connects"""
        if rc == 0:
            logger.info("Connected to MQTT Broker")
            # Subscribe to all device topics
            for name, topic in self.topics.items():
                self.client.subscribe(topic)
                logger.info(f"Subscribed to {name}: {topic}")
            
            # Announce analyzer is online
            self.client.publish("iot/analyzer/status", 
                              json.dumps({"status": "online", "timestamp": time.time()}))
        else:
            logger.error(f"Failed to connect, return code {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """Handle disconnection"""
        logger.warning("Disconnected from MQTT Broker")
        if rc != 0:
            logger.info("Attempting to reconnect...")
            self.reconnect()
    
    def on_message(self, client, userdata, msg):
        """Process incoming MQTT messages"""
        try:
            # Parse topic
            topic_parts = msg.topic.split('/')
            
            if len(topic_parts) >= 3:
                device_id = topic_parts[1]
                message_type = topic_parts[2]
                
                # Parse payload
                try:
                    payload = json.loads(msg.payload.decode())
                except:
                    payload = {"raw": msg.payload.decode()}
                
                # Add metadata
                payload['timestamp'] = time.time()
                payload['topic'] = msg.topic
                
                # Queue message for processing
                self.message_queue.put({
                    'device_id': device_id,
                    'type': message_type,
                    'payload': payload,
                    'timestamp': datetime.now()
                })
                
                # Update device status
                self.update_device_status(device_id, message_type, payload)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def on_subscribe(self, client, userdata, mid, granted_qos):
        """Confirm subscription"""
        logger.info(f"Subscribed to topic with QoS: {granted_qos}")
    
    def process_messages(self):
        """Background thread to process queued messages"""
        while True:
            try:
                message = self.message_queue.get(timeout=1)
                
                # Process based on message type
                if message['type'] == 'data':
                    self.process_sensor_data(message)
                elif message['type'] == 'status':
                    self.process_status_update(message)
                elif message['type'] == 'events':
                    self.process_event(message)
                elif message['type'] == 'response':
                    self.process_command_response(message)
                
                self.message_queue.task_done()
            except:
                continue
    
    def process_sensor_data(self, message):
        """Process sensor data from devices"""
        device_id = message['device_id']
        data = message['payload']
        
        logger.debug(f"Data from {device_id}: {data}")
        
        # Store in database (would call database handler)
        # db.store_sensor_data(device_id, data)
        
        # Check for alerts
        self.check_alerts(device_id, data)
    
    def process_status_update(self, message):
        """Process device status updates"""
        device_id = message['device_id']
        status = message['payload']
        
        self.device_status[device_id] = {
            'status': status.get('status', 'unknown'),
            'rssi': status.get('rssi', -100),
            'ip': status.get('ip', ''),
            'last_seen': time.time(),
            'battery': status.get('battery', 100)
        }
        
        logger.info(f"Device {device_id} status: {status.get('status')}")
        
        # Trigger callbacks if any
        if device_id in self.command_callbacks:
            for callback in self.command_callbacks[device_id]:
                callback('status', status)
    
    def process_event(self, message):
        """Process device events"""
        device_id = message['device_id']
        event = message['payload']
        
        logger.info(f"Event from {device_id}: {event}")
        
        # Handle specific events
        event_type = event.get('event')
        if event_type == 'button_pressed':
            self.handle_button_press(device_id)
        elif event_type == 'motion_detected':
            self.handle_motion_detected(device_id, event)
        elif event_type == 'temperature_alert':
            self.handle_temperature_alert(device_id, event)
    
    def process_command_response(self, message):
        """Process responses to commands"""
        device_id = message['device_id']
        response = message['payload']
        
        logger.info(f"Command response from {device_id}: {response}")
        
        # Trigger command callbacks
        if device_id in self.command_callbacks:
            for callback in self.command_callbacks[device_id]:
                callback('response', response)
    
    def send_command(self, device_id, command, parameters=None, callback=None):
        """Send command to a specific device"""
        topic = f"iot/{device_id}/commands"
        
        command_msg = {
            'command': command,
            'timestamp': time.time(),
            'command_id': f"cmd_{int(time.time())}"
        }
        
        if parameters:
            command_msg['parameters'] = parameters
        
        # Register callback if provided
        if callback:
            if device_id not in self.command_callbacks:
                self.command_callbacks[device_id] = []
            self.command_callbacks[device_id].append(callback)
        
        # Publish command
        result = self.client.publish(topic, json.dumps(command_msg))
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"Command sent to {device_id}: {command}")
            return True
        else:
            logger.error(f"Failed to send command to {device_id}")
            return False
    
    def broadcast_command(self, command, parameters=None, device_type=None):
        """Broadcast command to all devices or specific type"""
        topic = "iot/broadcast/commands"
        
        command_msg = {
            'command': command,
            'timestamp': time.time(),
            'target_type': device_type
        }
        
        if parameters:
            command_msg['parameters'] = parameters
        
        self.client.publish(topic, json.dumps(command_msg))
        logger.info(f"Broadcast command: {command}")
    
    def request_network_scan(self, gateway_id=None):
        """Request network scan from gateway"""
        if gateway_id:
            self.send_command(gateway_id, 'scan_network')
        else:
            self.broadcast_command('scan_network', device_type='gateway')
    
    def get_device_list(self):
        """Get list of all connected devices"""
        devices = []
        for device_id, status in self.device_status.items():
            if time.time() - status['last_seen'] < 300:  # Consider offline after 5 minutes
                devices.append({
                    'id': device_id,
                    'status': status
                })
        return devices
    
    def update_device_status(self, device_id, message_type, payload):
        """Update internal device status tracking"""
        if device_id not in self.device_status:
            self.device_status[device_id] = {}
        
        self.device_status[device_id]['last_seen'] = time.time()
        self.device_status[device_id]['last_message_type'] = message_type
        
        if 'rssi' in payload:
            self.device_status[device_id]['rssi'] = payload['rssi']
        if 'battery' in payload:
            self.device_status[device_id]['battery'] = payload['battery']
    
    def check_alerts(self, device_id, data):
        """Check for alert conditions"""
        alerts = []
        
        # Check RSSI
        if 'rssi' in data and data['rssi'] < -80:
            alerts.append({
                'type': 'weak_signal',
                'device': device_id,
                'value': data['rssi'],
                'threshold': -80
            })
        
        # Check battery
        if 'battery' in data and data['battery'] < 20:
            alerts.append({
                'type': 'low_battery',
                'device': device_id,
                'value': data['battery'],
                'threshold': 20
            })
        
        # Publish alerts
        for alert in alerts:
            self.client.publish("iot/alerts", json.dumps(alert))
            logger.warning(f"Alert: {alert}")
    
    def reconnect(self):
        """Reconnect to MQTT broker"""
        try:
            self.client.reconnect()
        except Exception as e:
            logger.error(f"Reconnection failed: {e}")
            time.sleep(5)
            self.reconnect()
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.disconnect()
        logger.info("Disconnected from MQTT Broker")

# Example usage
if __name__ == "__main__":
    # Create MQTT handler
    mqtt = MQTTHandler(broker_host="localhost", broker_port=1883)
    
    # Connect to broker
    mqtt.client.connect(mqtt.broker_host, mqtt.broker_port, 60)
    mqtt.client.loop_start()
    
    try:
        while True:
            # Send command to device
            mqtt.send_command("ESP32_NODE_001", "get_status")
            
            # Get list of devices
            devices = mqtt.get_device_list()
            print(f"Connected devices: {devices}")
            
            time.sleep(10)
    except KeyboardInterrupt:
        mqtt.disconnect()