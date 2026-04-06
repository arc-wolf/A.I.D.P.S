#!/usr/bin/env python3
from backend.database.device_inventory import DeviceInventory
from core.config import config
from pathlib import Path

def generate_ansible_inventory():
    """Generate dynamic Ansible inventory from database"""
    inventory = DeviceInventory()
    devices = inventory.get_all_devices()
    
    linux_hosts = []
    windows_hosts = []
    
    for device in devices:
        if device['ssh_enabled'] and device['os_type'] == 'linux':
            linux_hosts.append(device['ip'])
        elif device['winrm_enabled'] and device['os_type'] == 'windows':
            windows_hosts.append(device['ip'])
    
    inventory_content = f'''[linux]
{chr(10).join(linux_hosts)}

[windows]
{chr(10).join(windows_hosts)}

[all:vars]
ansible_connection=smart
ansible_python_interpreter=/usr/bin/python3
'''
    
    Path(config.ANSIBLE_INVENTORY).write_text(inventory_content)
    print(f"Generated {config.ANSIBLE_INVENTORY} with {len(linux_hosts)} Linux, {len(windows_hosts)} Windows hosts")

if __name__ == "__main__":
    generate_ansible_inventory()

