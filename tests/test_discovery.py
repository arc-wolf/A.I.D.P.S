"""A.I.D.P.S Test Suite - Discovery"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.discovery.network_scan import NetworkScanner
from backend.database.device_inventory import DeviceInventory

class TestDiscovery(unittest.TestCase):
    
    def setUp(self):
        self.scanner = NetworkScanner()
        self.inventory = DeviceInventory()
    
    def test_arp_scan_format(self):
        """Test ARP scan returns correct format"""
        # Test with small subnet (gateway only)
        devices = self.scanner.arp_scan('192.168.1.255/32')
        self.assertIsInstance(devices, list)
        if devices:
            self.assertIn('ip', devices[0])
            self.assertIn('mac', devices[0])
    
    def test_hostname_resolution(self):
        """Test hostname resolution"""
        import socket
        hostname = self.scanner.resolve_hostname('8.8.8.8')
        self.assertIsNone(hostname)  # Should timeout for external IP
    
    def test_database_upsert(self):
        """Test device upsert works"""
        test_device = {
            'ip': '192.168.1.100',
            'mac': 'aa:bb:cc:dd:ee:ff',
            'hostname': 'test-host',
            'os_type': 'linux'
        }
        result = self.inventory.upsert_device(test_device)
        self.assertTrue(result)
        
        # Verify it was saved
        saved = self.inventory.get_device_by_ip('192.168.1.100')
        self.assertEqual(saved['ip'], '192.168.1.100')

if __name__ == '__main__':
    unittest.main()

