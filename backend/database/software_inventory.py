from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import Dict, List, Optional, Any
from datetime import datetime
from core.config import config

class SoftwareInventory:
    def __init__(self):
        self.client = MongoClient(config.MONGO_URI)
        self.db = self.client[config.MONGO_DB]
        self.collection = self.db['software_inventory']
        
        # Create indexes
        self.collection.create_index('ip')
        self.collection.create_index('last_updated')
    
    def upsert_software(self, ip: str, os_type: str, applications: List[Dict]):
        """Upsert software inventory for device"""
        doc = {
            'ip': ip,
            'os_type': os_type,
            'applications': applications,
            'last_updated': datetime.now(),
            'application_count': len(applications)
        }
        
        result = self.collection.replace_one(
            {'ip': ip},
            doc,
            upsert=True
        )
        return result.acknowledged
    
    def get_software_by_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        """Get software for specific IP"""
        doc = self.collection.find_one({'ip': ip})
        return doc
    
    def get_all_inventory(self) -> List[Dict[str, Any]]:
        """Get all software inventories sorted by last_updated"""
        return list(self.collection.find().sort('last_updated', -1))
    
    def get_recent_inventories(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get inventories from last N days"""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        return list(self.collection.find({
            'last_updated': {'$gte': datetime.fromtimestamp(cutoff)}
        }).sort('last_updated', -1))
    
    def delete_old_inventories(self, days: int = 30):
        """Clean up old inventories"""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        result = self.collection.delete_many({
            'last_updated': {'$lt': datetime.fromtimestamp(cutoff)}
        })
        return result.deleted_count
    
    def test_connection(self) -> bool:
        """Test MongoDB connection"""
        try:
            self.client.admin.command('ping')
            return True
        except ConnectionFailure:
            return False

