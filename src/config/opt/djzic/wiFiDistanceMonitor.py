from libDistance import known_devices
import subprocess
import re
import json
import time
from typing import Dict, Optional
import math
import socket

class WiFiDistanceMonitor:
    def __init__(self, known_devices: Dict[str, Dict[str, str]], interface: str = "wlan0"):
        self.known_devices = known_devices
        self.interface = interface
        self.hostname = socket.gethostname()

    def get_mac_from_arp(self, ip: str) -> Optional[str]:
        """Get MAC address from ARP table for given IP"""
        try:
            result = subprocess.run(['arp', '-n', ip], 
                                  capture_output=True, text=True, check=True)
            mac_match = re.search(r'([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})', result.stdout)
            if mac_match:
                return mac_match.group(0).lower()

        except subprocess.CalledProcessError:
            try:
                subprocess.run(['ping', '-c', '1', '-W', '1', ip], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                result = subprocess.run(['arp', '-n', ip], 
                                      capture_output=True, text=True, check=True)
                mac_match = re.search(r'([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})', result.stdout)
                if mac_match:
                    return mac_match.group(0).lower()
            except subprocess.CalledProcessError:
                pass
        return None
    
    def get_wifi_signal_info(self, mac: str) -> Optional[int]:
        """Get WiFi signal strength (RSSI) in dBm"""
        try:
            result = subprocess.run(['sudo', 'iw', 'dev', self.interface, 'station', 'get', mac],
                                  capture_output=True, text=True, check=True)
            
            for line in result.stdout.split('\n'):
                if 'signal:' in line:
                    signal_match = re.search(r'signal:\s*(-?\d+)', line)
                    if signal_match:
                        return int(signal_match.group(1))
        except subprocess.CalledProcessError:
            return None
        return None
    
    def estimate_distance(self, rssi: int, tx_power: int = -40, env_factor: float = 2.5) -> float:
        """
        Estimate distance using log-distance path loss model
        distance = 10^((tx_power - rssi) / (10 * env_factor))
        """
        if rssi >= 0:
            return 0.0
        distance = 10 ** ((tx_power - rssi) / (10 * env_factor))
        return round(distance, 2)
    
    def scan_devices(self) -> Dict:
        """Scan all known devices and return formatted data"""
        current_time = time.time()
        result = {
            "timestamp": current_time,
            "hostname": self.hostname,
            "devices": {}
        }
        
        for ip, device_info in self.known_devices.items():
            # Skip self
            if ip == socket.gethostbyname(self.hostname):
                continue
                
            mac = self.get_mac_from_arp(ip)
            if not mac:
                continue
                
            rssi = self.get_wifi_signal_info(mac)
            if rssi is None:
                continue
                
            distance = self.estimate_distance(rssi)
            
            result["devices"][device_info["hostname"]] = {
                "type": device_info.get("type", device_info.get("model", "Unknown")),
                "location": device_info.get("location", "Unknown"),
                "distance": distance,
                "ip": ip,
                "mac": mac,
                "last_seen": current_time,
                "rssi": rssi
            }
        
        return result

def main():
    
    # Create monitor instance
    monitor = WiFiDistanceMonitor(known_devices)
    
    # Scan devices and get results
    results = monitor.scan_devices()
    
    # Print results in pretty JSON format
    print(json.dumps(results, indent=2))
    
    # Save results to file
    with open('/var/www/html/data/distance_data.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to /var/www/html/data/distance_data.json")

if __name__ == "__main__":
    main()