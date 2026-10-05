from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from mesh_analyzer import MeshNetworkAnalyzer
from hardware_bridge import HardwareBridge
from mqtt_handler import MQTTHandler
from database import Database
from ml_predictor import SignalPredictor
from router_monitor import RouterMonitor
from config import config  # This is correct
from datetime import datetime
import threading
import json
import os
import time

app = Flask(__name__, static_folder='../frontend')
app.config['SECRET_KEY'] = config.SECRET_KEY  # Use config
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components with config if needed
db = Database(config.SQLALCHEMY_DATABASE_URI)  # Pass DB URI
analyzer = MeshNetworkAnalyzer()
hw_bridge = HardwareBridge()
mqtt = MQTTHandler(
    broker_host=config.MQTT_BROKER,
    broker_port=config.MQTT_PORT
)
ml_predictor = SignalPredictor()

# ==================== ROUTER MONITORING ====================
# Initialize router monitor
router_monitor = RouterMonitor()
router_devices = []
last_router_scan = 0

def background_router_scan():
    """Background thread to scan router every 10 seconds"""
    global router_devices, last_router_scan
    while True:
        try:
            router_devices = router_monitor.scan_network()
            last_router_scan = time.time()
            
            # Emit to connected clients via WebSocket
            socketio.emit('router_devices', {'devices': router_devices})
            
            time.sleep(config.ROUTER_SCAN_INTERVAL)  # Use config value
        except Exception as e:
            print(f"Router scan error: {e}")
            time.sleep(config.ROUTER_SCAN_INTERVAL)

# Start background scanning
threading.Thread(target=background_router_scan, daemon=True).start()

# ==================== ROUTER API ENDPOINTS ====================

@app.route('/api/router/devices', methods=['GET'])
def get_router_devices():
    """Get devices connected to your WiFi router with signal strength"""
    return jsonify({
        'devices': router_devices,
        'count': len(router_devices),
        'last_scan': last_router_scan
    })

@app.route('/api/router/scan', methods=['POST'])
def scan_router_now():
    """Force an immediate scan"""
    global router_devices, last_router_scan
    router_devices = router_monitor.scan_network()
    last_router_scan = time.time()
    
    # Emit to all connected clients
    socketio.emit('router_devices', {'devices': router_devices})
    
    return jsonify({
        'devices': router_devices,
        'count': len(router_devices)
    })
@app.route('/api/router/device/<ip>', methods=['GET'])
def get_router_device(ip):
    """Get details for a specific device by IP - Pings directly"""
    import subprocess
    import platform
    import re
    
    system = platform.system()
    
    def ping_device(ip_addr):
        """Ping an IP and return result"""
        try:
            if system == "Windows":
                param = '-n 2'
                timeout = '-w 2000'
            else:
                param = '-c 2'
                timeout = '-W 2'
            
            result = subprocess.run(['ping', param, timeout, ip_addr], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=3)
            
            if result.returncode == 0:
                # Extract ping time
                time_match = re.search(r'time[=<](\d+\.?\d*)', result.stdout.lower())
                if time_match:
                    ping_time = float(time_match.group(1))
                    if ping_time < 5:
                        rssi = -45
                    elif ping_time < 10:
                        rssi = -55
                    elif ping_time < 20:
                        rssi = -65
                    else:
                        rssi = -75
                else:
                    rssi = -60
                    ping_time = None
                
                return {
                    'online': True,
                    'rssi': rssi,
                    'ping_ms': ping_time
                }
            else:
                return {'online': False, 'rssi': -100}
                
        except subprocess.TimeoutExpired:
            return {'online': False, 'rssi': -100}
        except Exception as e:
            print(f"Ping error: {e}")
            return {'online': False, 'rssi': -100}
    
    # Try to get hostname
    def get_hostname(ip_addr):
        try:
            if system == "Windows":
                result = subprocess.run(['nslookup', ip_addr], capture_output=True, text=True, timeout=2)
                match = re.search(r'Name:\s+(\S+)', result.stdout)
                if match:
                    return match.group(1).split('.')[0]
            else:
                import socket
                try:
                    return socket.gethostbyaddr(ip_addr)[0].split('.')[0]
                except:
                    pass
        except:
            pass
        return "unknown"
    
    # First check cache
    cached_device = next((d for d in router_devices if d['ip'] == ip), None)
    
    # Ping the IP
    print(f"🔍 Checking IP: {ip}")
    ping_result = ping_device(ip)
    
    if ping_result['online']:
        hostname = get_hostname(ip)
        
        return jsonify({
            'id': cached_device['id'] if cached_device else f"Device_{ip.replace('.', '_')}",
            'ip': ip,
            'mac': cached_device['mac'] if cached_device else 'N/A',
            'hostname': hostname,
            'rssi': ping_result['rssi'],
            'ping_ms': ping_result['ping_ms'],
            'status': 'online',
            'type': 'wifi_client',
            'is_router': ip.endswith('.1') or ip.endswith('.254'),
            'last_seen': datetime.now().isoformat()
        })
    else:
        return jsonify({'error': f'Device at {ip} is not responding'}), 404


#  API ENDPOINTS ====

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/network/analyze', methods=['POST'])
def analyze_network():
    """Advanced network analysis with ML predictions"""
    data = request.json
    
    # Run comprehensive analysis
    analysis = {
        'topology': analyzer.analyze_topology(data['nodes'], data['links']),
        'coverage': analyzer.analyze_coverage(data['nodes']),
        'interference': analyzer.detect_interference(data['nodes']),
        'bottlenecks': analyzer.find_bottlenecks(data['nodes'], data['links']),
        'redundancy': analyzer.calculate_redundancy(data['nodes']),
        'ml_predictions': ml_predictor.predict_network_behavior(data['nodes']),
        'recommendations': analyzer.generate_optimization_plan(data['nodes'])
    }
    
    # Save to database
    db.save_analysis(analysis)
    
    return jsonify(analysis)

@app.route('/api/hardware/discover', methods=['GET'])
def discover_devices():
    """Discover real IoT devices on the network"""
    devices = hw_bridge.scan_network()
    return jsonify({'devices': devices})

@app.route('/api/hardware/connect', methods=['POST'])
def connect_device():
    """Connect to a physical IoT device"""
    data = request.json
    result = hw_bridge.connect_device(
        device_id=data['device_id'],
        protocol=data.get('protocol', 'mqtt')
    )
    return jsonify(result)

@app.route('/api/hardware/read/<device_id>', methods=['GET'])
def read_device(device_id):
    """Read real-time data from physical device"""
    data = hw_bridge.read_sensor_data(device_id)
    return jsonify(data)

@app.route('/api/hardware/configure', methods=['POST'])
def configure_device():
    """Configure physical device parameters"""
    data = request.json
    result = hw_bridge.configure_device(
        device_id=data['device_id'],
        config=data['configuration']
    )
    return jsonify(result)

@app.route('/api/simulation/run', methods=['POST'])
def run_simulation():
    """Run what-if scenarios"""
    data = request.json
    results = analyzer.simulate_scenario(
        nodes=data['nodes'],
        scenario=data['scenario_type'],
        parameters=data['parameters']
    )
    return jsonify(results)

@app.route('/api/export/report', methods=['POST'])
def export_report():
    """Generate PDF/CSV report"""
    data = request.json
    report = analyzer.generate_report(
        analysis_id=data['analysis_id'],
        format=data.get('format', 'pdf')
    )
    return jsonify({'report_url': report})

@app.route('/api/network/status', methods=['GET'])
def network_status():
    """Get current network status"""
    return jsonify({
        'status': 'online',
        'timestamp': time.time(),
        'router_devices': len(router_devices)
    })

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get all devices (simulated for now)"""
    return jsonify({'devices': []})

# SOCKET.IO EVENTS 

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Send initial router data on connect
    emit('router_devices', {'devices': router_devices})

@socketio.on('command_device')
def handle_device_command(data):
    """Send real-time commands to devices"""
    device_id = data['device_id']
    command = data['command']
    response = hw_bridge.send_command(device_id, command)
    emit('command_response', {'device_id': device_id, 'response': response})

@socketio.on('scan_network')
def handle_scan_network():
    """Handle manual scan request"""
    global router_devices, last_router_scan
    router_devices = router_monitor.scan_network()
    last_router_scan = time.time()
    emit('router_devices', {'devices': router_devices})

# MAIN APP

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)