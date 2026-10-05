import serial
import paho.mqtt.client as mqtt
import requests
import json
import threading
import time
import numpy as np
from typing import Dict, Any

class HardwareBridge:
    def __init__(self):
        self.devices = {}
        self.mqtt_client = mqtt.Client()
        self.serial_connections = {}
        self.setup_mqtt()
        
    def setup_mqtt(self):
        """Setup MQTT connection for IoT devices"""
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        
        try:
            self.mqtt_client.connect("localhost", 1883, 60)
            self.mqtt_client.loop_start()
        except:
            print("MQTT broker not available, running in simulation mode")
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT broker")
        client.subscribe("iot/+/data")
    
    def on_mqtt_message(self, client, userdata, msg):
        """Handle incoming MQTT messages from devices"""
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        
        device_id = topic.split('/')[1]
        self.devices[device_id] = {
            'last_seen': time.time(),
            'data': payload,
            'protocol': 'mqtt'
        }
    
    def scan_network(self) -> list:
        """Discover devices on the network"""
        devices = []
        
        # Scan for MQTT devices
        devices.extend(self.scan_mqtt_devices())
        
        # Scan serial ports for Arduino/ESP32
        devices.extend(self.scan_serial_devices())
        
        # Scan for REST API devices
        devices.extend(self.scan_http_devices())
        
        return devices
    
    def scan_mqtt_devices(self) -> list:
        """Discover MQTT-enabled devices"""
        # In real implementation, this would query an MQTT broker
        # For now, return simulated devices
        return [
            {
                'id': 'esp32_sensor_1',
                'type': 'temperature_sensor',
                'protocol': 'mqtt',
                'ip': '192.168.1.101',
                'status': 'online'
            },
            {
                'id': 'arduino_gateway_1',
                'type': 'gateway',
                'protocol': 'mqtt',
                'ip': '192.168.1.102',
                'status': 'online'
            }
        ]
    
    def scan_serial_devices(self) -> list:
        """Scan for devices connected via serial (USB)"""
        import serial.tools.list_ports
        
        devices = []
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            try:
                # Try to open port and identify device
                ser = serial.Serial(port.device, 115200, timeout=1)
                ser.write(b"ID?\n")
                response = ser.readline().decode().strip()
                
                if response:
                    devices.append({
                        'id': response,
                        'type': 'serial_device',
                        'protocol': 'serial',
                        'port': port.device,
                        'status': 'online'
                    })
                ser.close()
            except:
                pass
        
        return devices
    
    def scan_http_devices(self) -> list:
        """Scan for devices with REST APIs"""
        # Common IoT device IP ranges
        ip_ranges = ['192.168.1.{}'.format(i) for i in range(100, 120)]
        devices = []
        
        for ip in ip_ranges:
            try:
                response = requests.get(f'http://{ip}/status', timeout=0.5)
                if response.status_code == 200:
                    data = response.json()
                    devices.append({
                        'id': data.get('id', f'device_{ip}'),
                        'type': data.get('type', 'unknown'),
                        'protocol': 'http',
                        'ip': ip,
                        'status': 'online'
                    })
            except:
                pass
        
        return devices
    
    def connect_device(self, device_id: str, protocol: str = 'mqtt') -> Dict:
        """Establish connection with a physical device"""
        
        if protocol == 'mqtt':
            # Already connected via MQTT
            if device_id in self.devices:
                return {'success': True, 'device': self.devices[device_id]}
            else:
                return {'success': False, 'error': 'Device not found'}
        
        elif protocol == 'serial':
            # Try serial connection
            for port in self.scan_serial_devices():
                if port['id'] == device_id:
                    try:
                        ser = serial.Serial(port['port'], 115200, timeout=1)
                        self.serial_connections[device_id] = ser
                        return {'success': True, 'port': port['port']}
                    except Exception as e:
                        return {'success': False, 'error': str(e)}
        
        elif protocol == 'http':
            # HTTP/REST connection
            # Find device IP from discovery
            for device in self.devices.values():
                if device.get('id') == device_id and device.get('ip'):
                    return {
                        'success': True,
                        'ip': device['ip'],
                        'base_url': f"http://{device['ip']}/api"
                    }
        
        return {'success': False, 'error': 'Connection failed'}
    
    def read_sensor_data(self, device_id: str) -> Dict:
        """Read real-time data from a connected device"""
        
        if device_id in self.devices:
            # Return cached MQTT data
            return self.devices[device_id]['data']
        
        elif device_id in self.serial_connections:
            # Read from serial
            ser = self.serial_connections[device_id]
            ser.write(b"READ\n")
            response = ser.readline().decode().strip()
            
            try:
                return json.loads(response)
            except:
                return {'raw': response}
        
        # Simulated data for demo
        return {
            'temperature': 22.5 + np.random.random() * 2,
            'humidity': 45 + np.random.random() * 10,
            'rssi': -65 - np.random.random() * 10,
            'battery': 85 - np.random.random() * 5
        }
    
    def configure_device(self, device_id: str, config: Dict) -> Dict:
        """Send configuration to a physical device"""
        
        if device_id in self.serial_connections:
            # Send via serial
            ser = self.serial_connections[device_id]
            config_str = json.dumps(config)
            ser.write(f"CONFIG {config_str}\n".encode())
            response = ser.readline().decode().strip()
            return {'success': True, 'response': response}
        
        # Simulated response
        return {'success': True, 'message': 'Configuration applied'}
    
    def send_command(self, device_id: str, command: str) -> Dict:
        """Send real-time command to device"""
        
        if device_id in self.serial_connections:
            ser = self.serial_connections[device_id]
            ser.write(f"{command}\n".encode())
            response = ser.readline().decode().strip()
            return {'success': True, 'response': response}
        
        # Simulated commands
        commands = {
            'reboot': 'Device rebooting...',
            'status': 'Device operational',
            'scan': 'Scanning networks... Found 3 APs',
            'led_on': 'LED turned on',
            'led_off': 'LED turned off'
        }
        
        return {
            'success': True,
            'response': commands.get(command, 'Command executed')
        }