import paramiko
import time
from typing import Dict, Optional
from backend.database.device_inventory import DeviceInventory
from core.config import config
from backend.database.software_inventory import SoftwareInventory

class LinuxSSHProvisioner:
    def __init__(self):
        self.inventory = DeviceInventory()
        self.swinv = SoftwareInventory()
    
    def enable_ssh_access(self, ip: str, username: str = None, password: str = None) -> Dict:
        """Enable SSH access on Linux target"""
        username = username or config.DEFAULT_SSH_USER
        password = password or config.DEFAULT_SSH_PASSWORD
        
        if not password:
            return {'success': False, 'error': 'No credentials provided'}
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # Connect (assumes SSH already running)
            client.connect(
                ip, port=22, username=username, 
                password=password, timeout=10
            )
            
            # Check if openssh-server is installed and running
            stdin, stdout, stderr = client.exec_command('systemctl is-active ssh')
            ssh_status = stdout.read().decode().strip()
            
            commands = []
            if 'active' not in ssh_status:
                # Install and enable SSH
                if 'ubuntu' in self._get_distro(client).lower() or 'debian' in self._get_distro(client).lower():
                    commands.extend([
                        'sudo apt update',
                        'sudo apt install -y openssh-server',
                        'sudo systemctl enable ssh',
                        'sudo systemctl start ssh'
                    ])
                else:
                    commands.extend([
                        'sudo yum install -y openssh-server',
                        'sudo systemctl enable sshd',
                        'sudo systemctl start sshd'
                    ])
                
                # Execute commands
                for cmd in commands:
                    stdin, stdout, stderr = client.exec_command(cmd)
                    time.sleep(2)
                    error = stderr.read().decode()
                    if error:
                        client.close()
                        return {'success': False, 'error': f'Command failed: {cmd}', 'output': error}
            
            # Update inventory
            self.inventory.upsert_device({
                'ip': ip,
                'ssh_enabled': True,
                'status': 'ssh_provisioned'
            })
            
            # Collect software inventory
            apps = self._collect_linux_software(client)
            self.swinv.upsert_software(ip, 'linux', apps)
            
            client.close()
            return {'success': True, 'ip': ip, 'status': 'provisioned'}
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'ip': ip}
    
    def _get_distro(self, client) -> str:
        """Get Linux distribution"""
        stdin, stdout, _ = client.exec_command('cat /etc/os-release')
        return stdout.read().decode()
    
    def _collect_linux_software(self, client) -> list:
        """Collect installed packages"""
        apps = []
        
        # Try dpkg first (Debian/Ubuntu)
        stdin, stdout, _ = client.exec_command("dpkg -l 2>/dev/null | awk '/^[a-z]/ {print $2\":\"$3}'")
        dpkg_apps = stdout.read().decode().strip().split('\\n')
        
        if dpkg_apps and dpkg_apps != ['']:
            for app in dpkg_apps:
                if ':' in app:
                    name, version = app.split(':', 1)
                    apps.append({'name': name.strip(), 'version': version.strip()})
        
        # Fallback to rpm
        else:
            stdin, stdout, _ = client.exec_command("rpm -qa --qf '%{NAME}:%{VERSION}' 2>/dev/null")
            rpm_apps = stdout.read().decode().strip().split('\\n')
            for app in rpm_apps:
                if ':' in app:
                    name, version = app.split(':', 1)
                    apps.append({'name': name.strip(), 'version': version.strip()})
        
        return apps[:50]  # Limit for performance

