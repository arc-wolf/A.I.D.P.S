import pandas as pd
from typing import Dict, Any
from backend.database.device_inventory import DeviceInventory
from datetime import datetime

class ExcelExporter:
    def __init__(self):
        self.inventory = DeviceInventory()
    
    def export_devices(self, filename: str = None) -> str:
        """Export device inventory to Excel"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'lab_inventory_{timestamp}.xlsx'
        
        # Get all devices
        devices = self.inventory.get_all_devices()
        
        if not devices:
            return f"No devices found. Empty export: {filename}"
        
        # Convert to DataFrame
        df = pd.DataFrame(devices)
        
        # Reorder columns for better presentation
        column_order = ['ip', 'mac', 'hostname', 'os_type', 'ssh_enabled', 
                       'winrm_enabled', 'status', 'last_seen']
        df = df[column_order]
        
        # Format booleans and dates
        df['ssh_enabled'] = df['ssh_enabled'].map({True: '✅', False: '❌'})
        df['winrm_enabled'] = df['winrm_enabled'].map({True: '✅', False: '❌'})
        df['last_seen'] = pd.to_datetime(df['last_seen']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Write to Excel with formatting
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Devices', index=False)
            
            # Get stats worksheet
            workbook = writer.book
            stats_sheet = workbook.create_sheet('Stats')
            
            stats = self.inventory.get_stats()
            stats_data = [
                ['Total Devices', stats['total']],
                ['Active (24h)', stats['active']],
                ['Linux', stats['os_distribution'].get('linux', 0)],
                ['Windows', stats['os_distribution'].get('windows', 0)],
                ['Unknown OS', stats['os_distribution'].get('unknown', 0)]
            ]
            for row_idx, row in enumerate(stats_data, 1):
                for col_idx, value in enumerate(row, 1):
                    stats_sheet.cell(row=row_idx, column=col_idx, value=value)
        
        return f"✅ Exported {len(devices)} devices to {filename}"
    
    def export_software_summary(self, filename: str) -> str:
        """Export software summary"""
        pass  # Future enhancement

