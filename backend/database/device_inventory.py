import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from core.config import config

class DeviceInventory:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.SQLITE_DB
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database with devices table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT UNIQUE NOT NULL,
                mac TEXT,
                hostname TEXT,
                os_type TEXT,
                ssh_enabled BOOLEAN DEFAULT FALSE,
                winrm_enabled BOOLEAN DEFAULT FALSE,
                status TEXT DEFAULT 'unknown',
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Index for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip ON devices(ip)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_seen ON devices(last_seen)')
        
        conn.commit()
        conn.close()
    
    def upsert_device(self, device_data: Dict) -> bool:
        """Upsert device information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO devices 
            (ip, mac, hostname, os_type, ssh_enabled, winrm_enabled, status, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            device_data.get('ip'),
            device_data.get('mac'),
            device_data.get('hostname'),
            device_data.get('os_type'),
            device_data.get('ssh_enabled', False),
            device_data.get('winrm_enabled', False),
            device_data.get('status', 'unknown'),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def get_all_devices(self) -> List[Dict]:
        """Get all devices"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM devices ORDER BY last_seen DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def get_device_by_ip(self, ip: str) -> Optional[Dict]:
        """Get single device by IP"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM devices WHERE ip = ?', (ip,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def get_stats(self) -> Dict:
        """Get dashboard statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total devices
        cursor.execute('SELECT COUNT(*) FROM devices')
        total = cursor.fetchone()[0]
        
        # Active (seen in last 24h)
        cursor.execute("""
            SELECT COUNT(*) FROM devices 
            WHERE last_seen > datetime('now', '-1 day')
        """)
        active = cursor.fetchone()[0]
        
        # By OS
        cursor.execute("SELECT os_type, COUNT(*) FROM devices GROUP BY os_type")
        os_dist = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total': total,
            'active': active,
            'os_distribution': os_dist
        }
    
    def delete_old_devices(self, days: int = 30):
        """Clean up old inactive devices"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM devices 
            WHERE last_seen < datetime('now', ?)
        """, (f'-{days} days',))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted

