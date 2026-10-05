'''connect Router and monitor signal strength'''
import subprocess
import re
import time
import json
import platform
from datetime import datetime

class RouterMonitor:
    def __init__(self):
        self.devices = {}
        self.system = platform.system()
        
    def get_connected_devices(self):
        """Get all devices connected to your WiFi network"""
        
        if self.system == "Windows":
            return self._get_windows_devices()
        elif self.system == "Darwin":  # macOS
            return self._get_mac_devices()
        else:  # Linux
            return self._get_linux_devices()
    
    def _get_windows_devices(self):
        """Get devices on Windows using arp -a"""
        devices = []
        
        try:
            # Run command to get network devices
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            
            # Parse output
            lines = result.stdout.split('\n')
            for line in lines:
                # Look for  IP and MAC addresses
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([a-f0-9-]{17})', line.lower())
                if match:
                    ip = match.group(1)
                    mac = match.group(2).upper()
                    
                    # Skip broadcast and multicast addresses
                    if ip.endswith('.255') or mac.startswith('FF'):
                        continue
                    
                    devices.append({
                        'ip': ip,
                        'mac': mac,
                        'type': 'unknown'
                    })
            
        except Exception as e:
            print(f"Error getting Windows devices: {e}")
        
        return devices
    
    def _get_mac_devices(self):
        """Get devices on macOS using arp -a"""
        devices = []
        
        try:
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            
            lines = result.stdout.split('\n')
            for line in lines:
                
                match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([a-f0-9:]{17})', line.lower())
                if match:
                    ip = match.group(1)
                    mac = match.group(2).upper().replace(':', '-')
                    
                    if not ip.endswith('.255'):
                        devices.append({
                            'ip': ip,
                            'mac': mac,
                            'type': 'unknown'
                        })
                        
        except Exception as e:
            print(f"Error getting macOS devices: {e}")
        
        return devices
    
    def _get_linux_devices(self):
        """Get devices on Linux using arp -a or ip neigh"""
        devices = []
        
        try:
            # Try ip neigh command 
            result = subprocess.run(['ip', 'neigh'], capture_output=True, text=True)
            
            lines = result.stdout.split('\n')
            for line in lines:
                
                match = re.search(r'(\d+\.\d+\.\d+\.\d+).*lladdr\s+([a-f0-9:]{17})', line.lower())
                if match:
                    ip = match.group(1)
                    mac = match.group(2).upper().replace(':', '-')
                    
                    if not ip.endswith('.255'):
                        devices.append({
                            'ip': ip,
                            'mac': mac,
                            'type': 'unknown'
                        })
                        
        except Exception as e:
            print(f"Error getting Linux devices: {e}")
            
        
            try:
                result = subprocess.run(['arp', '-n'], capture_output=True, text=True)
                lines = result.stdout.split('\n')
                for line in lines:
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+).*([a-f0-9:]{17})', line.lower())
                    if match:
                        ip = match.group(1)
                        mac = match.group(2).upper().replace(':', '-')
                        
                        if not ip.endswith('.255'):
                            devices.append({
                                'ip': ip,
                                'mac': mac,
                                'type': 'unknown'
                            })
            except:
                pass
        
        return devices
    
    def ping_device(self, ip):
        """Ping a device to check if it's online and get approximate signal"""
        try:
            if self.system == "Windows":
                param = '-n 1'
            else:
                param = '-c 1'
            
            result = subprocess.run(['ping', param, ip], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=2)
            
            # Ping successful
            if result.returncode == 0:
            
                
                time_match = re.search(r'time[=<](\d+\.?\d*)', result.stdout.lower())
                if time_match:
                    ping_time = float(time_match.group(1))
                    
                    # Higher ping time = weak signal
                    if ping_time < 5:
                        return {'online': True, 'rssi': -45}  # Excellent
                    elif ping_time < 10:
                        return {'online': True, 'rssi': -55}  # Good
                    elif ping_time < 20:
                        return {'online': True, 'rssi': -65}  # Fair
                    else:
                        return {'online': True, 'rssi': -75}  # Weak
                else:
                    return {'online': True, 'rssi': -60}  
            else:
                return {'online': False, 'rssi': -100}
                
        except:
            return {'online': False, 'rssi': -100}
    
    def scan_network(self):
        """Scan network and return devices with signal strength"""
        print("🔍 Scanning network for devices...")
        
        # Get all devices on network
        devices = self.get_connected_devices()
        
        results = []
        for device in devices[:10]:  #only first ten devices
            if device['ip'].endswith('.1') or device['ip'].endswith('.254'):
                continue
                
            print(f"   Checking {device['ip']}...")
            
            # Ping device to check if online and signal
            status = self.ping_device(device['ip'])
            
            if status['online']:
                # hostname
                hostname = self.get_hostname(device['ip'])
                
                results.append({
                    'id': f"Device_{len(results)+1}",
                    'ip': device['ip'],
                    'mac': device['mac'],
                    'hostname': hostname,
                    'rssi': status['rssi'],
                    'status': 'online',
                    'type': 'wifi_client',
                    'last_seen': datetime.now().isoformat()
                })
        
        print(f" Found {len(results)} active devices")
        return results
    
    def get_hostname(self, ip):
        """Try to get hostname for an IP address"""
        try:
            if self.system == "Windows":
                result = subprocess.run(['nslookup', ip], capture_output=True, text=True)
                match = re.search(r'Name:\s+(\S+)', result.stdout)
                if match:
                    return match.group(1)
            else:
                import socket
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                    return hostname
                except:
                    pass
        except:
            pass
        return "unknown"

# test
if __name__ == "__main__":
    monitor = RouterMonitor()
    devices = monitor.scan_network()
    
    print("\n Connected Devices:")
    for d in devices:
        signal = d['rssi']
        if signal > -50:
            quality = "🟢 Excellent"
        elif signal > -65:
            quality = "🟡 Good"
        elif signal > -75:
            quality = "🟠 Fair"
        else:
            quality = "🔴 Weak"
            
        print(f"  {d['id']}: {d['ip']} - {quality} ({signal} dBm)")