from scapy.all import ARP, Ether, srp
from concurrent.futures import ThreadPoolExecutor
import socket
import threading
from typing import List, Dict, Optional
from core.config import config
from backend.database.device_inventory import DeviceInventory

class NetworkScanner:
    def __init__(self):
        self.inventory = DeviceInventory()
        self.lock = threading.Lock()
    
    def arp_scan(self, subnet: str, timeout: int = None) -> List[Dict]:
        """
        Perform ARP scan on subnet using scapy
        Returns list of {'ip': str, 'mac': str}
        """
        timeout = timeout or config.SCAN_TIMEOUT
        
        # Create ARP request
        arp = ARP(pdst=subnet)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp
        
        # Send packet and receive response
        result = srp(packet, timeout=timeout, verbose=0)[0]
        
        devices = []
        for sent, received in result:
            devices.append({
                'ip': received.psrc,
                'mac': received.hwsrc
            })
        
        return devices
    
    def resolve_hostname(self, ip: str, timeout: int = 2) -> Optional[str]:
        """Resolve hostname with timeout"""
        try:
            result = socket.gethostbyaddr(ip)
            return result[0]
        except:
            return None
    
    def scan_subnet(self, subnet: str = None) -> List[Dict]:
        """
        Full network scan:
        1. ARP discovery
        2. Hostname resolution (parallel)
        3. Update inventory
        """
        subnet = subnet or config.SCAN_SUBNET
        
        print(f"🔍 Scanning {subnet}...")
        devices = self.arp_scan(subnet)
        print(f"📡 Found {len(devices)} live hosts")
        
        # Parallel hostname resolution
        with ThreadPoolExecutor(max_workers=20) as executor:
            hostnames = dict(zip(
                devices,
                executor.map(self.resolve_hostname, [d['ip'] for d in devices])
            ))
        
        # Enrich and save to inventory
        enriched_devices = []
        for device in devices:
            hostname = hostnames.get(device, {}).split('.')[0] if hostnames.get(device) else None
            
            enriched = {
                'ip': device['ip'],
                'mac': device['mac'],
                'hostname': hostname,
                'os_type': 'unknown',
                'ssh_enabled': False,
                'winrm_enabled': False,
                'status': 'discovered'
            }
            
            self.inventory.upsert_device(enriched)
            enriched_devices.append(enriched)
        
        return enriched_devices
    
    def ping_host(self, ip: str, timeout: int = 1) -> bool:
        """Ping test for host responsiveness"""
        from scapy.all import IP, ICMP, sr1
        try:
            resp = sr1(IP(dst=ip)/ICMP(), timeout=timeout, verbose=0)
            return resp is not None
        except:
            return False

