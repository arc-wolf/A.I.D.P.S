import paramiko
import subprocess
import json
from typing import Dict, List, Optional
from backend.database.device_inventory import DeviceInventory
from backend.database.software_inventory import SoftwareInventory
from core.config import config

class WindowsWinRMProvisioner:
    def __init__(self):
        self.inventory = DeviceInventory()
        self.swinv = SoftwareInventory()
    
    def enable_winrm(self, ip: str, username: str = None, password: str = None) -> Dict:
        """Enable WinRM on Windows target"""
        username = username or config.DEFAULT_WINRM_USER
        password = password or config.DEFAULT_WINRM_PASSWORD
        
        if not all([username, password]):
            return {'success': False, 'error': 'Missing Windows credentials'}
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # Try WinRM port first, fallback to SSH if available
            if self._test_winrm(ip):
                # WinRM already enabled
                apps = self._collect_windows_software(ip, username, password)
                self.swinv.upsert_software(ip, 'windows', apps)
                return {'success': True, 'ip': ip, 'status': 'winrm_already_enabled'}
            
            # Fallback: Try SSH provisioning first
            ssh_result = self._provision_via_ssh(ip, username, password)
            if ssh_result['success']:
                apps = self._collect_windows_software(ip, username, password)
                self.swinv.upsert_software(ip, 'windows', apps)
                self.inventory.upsert_device({
                    'ip': ip,
                    'winrm_enabled': True,
                    'status': 'winrm_provisioned'
                })
                return {'success': True, 'method': 'ssh_fallback', 'ip': ip}
            
            # Last resort: WMI/CIM fallback (requires impacket or pywinrm)
            wmi_result = self._provision_via_wmi(ip, username, password)
            if wmi_result['success']:
                return wmi_result
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': 'All provisioning methods failed'}
    
    def _test_winrm(self, ip: str) -> bool:
        """Test WinRM connectivity"""
        from impacket.winrm import WinRM
        
        try:
            winrm = WinRM(ip, username=config.DEFAULT_WINRM_USER, 
                         password=config.DEFAULT_WINRM_PASSWORD)
            winrm.connect()
            return True
        except:
            return False
    
    def _provision_via_ssh(self, ip: str, username: str, password: str) -> Dict:
        """Provision WinRM via SSH (if SSH available on Windows)"""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            client.connect(ip, port=22, username=username, password=password, timeout=10)
            
            # Enable WinRM via PowerShell
            ps_script = '''
            Enable-PSRemoting -Force;
            Set-Item WSMan:\\localhost\\Client\\TrustedHosts -Value "*" -Force;
            Restart-Service WinRM;
            Set-NetFirewallRule -DisplayGroup "Windows Remote Management" -Enabled True;
            '''
            
            stdin, stdout, stderr = client.exec_command(f'powershell -Command "{ps_script}"')
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            client.close()
            return {'success': 'WinRM' not in error, 'output': output}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _provision_via_wmi(self, ip: str, username: str, password: str) -> Dict:
        """WMI/CIM provisioning fallback"""
        try:
            cmd = [
                'wmic', '/node:' + ip, '/user:' + username, 
                '/password:' + password, '/connect:RPC', 
                'process', 'call', 'create', 
                'powershell -Command "Enable-PSRemoting -Force; Set-WSManQuickConfig -Force"'
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return {'success': result.returncode == 0}
        except:
            return {'success': False}
    
    def _collect_windows_software(self, ip: str, username: str, password: str) -> List[Dict]:
        """Collect installed software via PowerShell"""
        apps = []
        
        try:
            ps_script = '''
            Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, 
                           HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* |
            Where-Object { $_.DisplayName } |
            Select-Object DisplayName, DisplayVersion, Publisher |
            ConvertTo-Json -Compress
            '''
            
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, port=22, username=username, password=password)
            
            stdin, stdout, stderr = client.exec_command(f'powershell -Command "{ps_script}"')
            json_data = stdout.read().decode().strip()
            
            if json_data:
                parsed = json.loads(json_data)
                if isinstance(parsed, list):
                    for app in parsed[:50]:  # Limit
                        apps.append({
                            'name': app.get('DisplayName', 'Unknown'),
                            'version': app.get('DisplayVersion', 'Unknown'),
                            'publisher': app.get('Publisher', 'Unknown')
                        })
            
            client.close()
        except:
            pass
        
        return apps

