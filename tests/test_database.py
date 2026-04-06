"""Test SQLite and MongoDB operations"""
import unittest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.device_inventory import DeviceInventory
from backend.database.software_inventory import SoftwareInventory
from unittest.mock import patch, MagicMock

class TestDatabase(unittest.TestCase):
    
    def setUp(self):
        self.db_path = 'test_inventory.db'
        os.remove(self.db_path) if os.path.exists(self.db_path) else None
        self.device_inv = DeviceInventory(self.db_path)
    
    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_device_upsert(self):
        device = {
            'ip': '192.168.1.10',
            'mac': 'aa:bb:cc:dd:ee:ff',
            'os_type': 'linux'
        }
        result = self.device_inv.upsert_device(device)
        self.assertTrue(result)
        
        saved = self.device_inv.get_device_by_ip('192.168.1.10')
        self.assertEqual(saved['ip'], '192.168.1.10')
        self.assertEqual(saved['os_type'], 'linux')
    
    def test_stats(self):
        # Add test devices
        test_devices = [
            {'ip': '192.168.1.1', 'os_type': 'linux'},
            {'ip': '192.168.1.2', 'os_type': 'windows'}
        ]
        for d in test_devices:
            self.device_inv.upsert_device(d)
        
        stats = self.device_inv.get_stats()
        self.assertEqual(stats['total'], 2)
        self.assertIn('linux', stats['os_distribution'])
    
    @patch('pymongo.MongoClient')
    def test_mongo_connection(self, mock_client):
        mock_db = MagicMock()
        mock_client.return_value.__getitem__.return_value = mock_db
        sw_inv = SoftwareInventory()
        self.assertIsNotNone(sw_inv.collection)

if __name__ == '__main__':
    unittest.main()

