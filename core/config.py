import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Network
    SCAN_SUBNET = os.getenv('SCAN_SUBNET', '192.168.1.0/24')
    SCAN_TIMEOUT = int(os.getenv('SCAN_TIMEOUT', '3'))
    
    # Database
    SQLITE_DB = os.getenv('SQLITE_DB', 'aidps_inventory.db')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB = os.getenv('MONGO_DB', 'aidps')
    
    # Web
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-prod')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Credentials
    DEFAULT_SSH_USER = os.getenv('DEFAULT_SSH_USER', 'admin')
    DEFAULT_SSH_PASSWORD = os.getenv('DEFAULT_SSH_PASSWORD', '')
    DEFAULT_WINRM_USER = os.getenv('DEFAULT_WINRM_USER', 'Administrator')
    DEFAULT_WINRM_PASSWORD = os.getenv('DEFAULT_WINRM_PASSWORD', '')
    
    # Scheduler
    SCHEDULE_TIME = os.getenv('SCHEDULE_TIME', '18:00')
    
    # Ansible
    ANSIBLE_INVENTORY = os.getenv('ANSIBLE_INVENTORY', './inventory.ini')

config = Config()

