from scapy.all import IP, TCP, sr1
import socket
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional, Tuple
from core.config import config
from backend.database.device_inventory import DeviceInventory

class ServiceDetector:
    def __init__(self):
        self.inventory = DeviceInventory()
        SSH_PORT = 22
        WINRM_HTTP_PORT = 5985
        WINRM_HTTPS_PORT = 5986
    
    def check_port_open(self, ip: str, port: int, timeout: float = 1.0) -> bool:
        """Check if port is open using TCP SYN scan"""
        try:
            # SYN scan with scapy
            resp = sr1(
                IP(dst=ip)/TCP(dport=port, flags='S'),
                timeout=timeout,
                verbose=0
            )
            return resp and resp.haslayer(TCP) and resp[TCP].flags == 0x12  # SYN-ACK
        except:
            return False
    
    def detect_ssh(self, ip: str, timeout: float = 2.0) -> bool:
        """Detect SSH service (port 22)"""
        return self.check_port_open(ip, 22, timeout)
    
    def detect_winrm(self, ip: str, timeout: float = 2.0) -> bool:
        """Detect WinRM (ports 5985/5986)"""
        return (self.check_port_open(ip, 5985, timeout) or 
                self.check_port_open(ip, 5986, timeout))
    
    def detect_os_type(self, ip: str) -> str:
        """Basic OS detection based on open services"""
        if self.detect_ssh(ip):
            return 'linux'
        elif self.detect_winrm(ip):
            return 'windows'
        else:
            return 'unknown'
    
    def scan_services_parallel(self, devices: list, max_workers: int = 20) -> list:
        """
        Scan services for multiple devices in parallel
        Returns updated device records
        """
        def scan_device(ip: str):
            ssh = self.detect_ssh(ip)
            winrm = self.detect_winrm(ip)
            os_type = self.detect_os_type(ip)
            
            # Update inventory
            device_data = {
                'ip': ip,
                'os_type': os_type,
                'ssh_enabled': ssh,
                'winrm_enabled': winrm,
                'status': 'services_detected'
            }
            self.inventory.upsert_device(device_data)
            
            return device_data
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(scan_device, [d['ip'] for d in devices]))
        
        return results

