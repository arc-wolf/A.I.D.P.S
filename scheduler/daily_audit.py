from apscheduler.schedulers.background import BackgroundScheduler
from backend.discovery.network_scan import NetworkScanner
from backend.detection.service_detect import ServiceDetector
from backend.database.software_inventory import SoftwareInventory
from backend.database.device_inventory import DeviceInventory
from backend.provisioning.linux_ssh import LinuxSSHProvisioner
from backend.provisioning.windows_winrm import WindowsWinRMProvisioner
import logging
from core.config import config
from datetime import datetime, time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DailyAuditor:
    def __init__(self):
        self.scanner = NetworkScanner()
        self.detector = ServiceDetector()
        self.swinv = SoftwareInventory()
        self.inventory = DeviceInventory()
        self.linux_provisioner = LinuxSSHProvisioner()
        self.windows_provisioner = WindowsWinRMProvisioner()
    
    def daily_full_audit(self):
        """Complete daily audit cycle"""
        try:
            logger.info("🕐 Starting daily audit...")
            
            # 1. Network discovery
            devices = self.scanner.scan_subnet()
            logger.info(f"📡 Discovered {len(devices)} devices")
            
            # 2. Service detection
            if devices:
                detected = self.detector.scan_services_parallel(devices)
                logger.info(f"🔍 Detected services on {len(detected)} devices")
            
            # 3. Software inventory collection (provisioned systems only)
            active_devices = self.inventory.get_all_devices()
            for device in active_devices:
                if device['ssh_enabled'] and device['os_type'] == 'linux':
                    self.linux_provisioner.enable_ssh_access(device['ip'])
                elif device['winrm_enabled'] and device['os_type'] == 'windows':
                    self.windows_provisioner.enable_winrm(device['ip'])
            
            # Cleanup
            self.inventory.delete_old_devices(days=30)
            self.swinv.delete_old_inventories(days=30)
            
            logger.info("✅ Daily audit completed")
            
        except Exception as e:
            logger.error(f"❌ Daily audit failed: {e}")
    
    def start_scheduler(self):
        """Start scheduler with daily task"""
        scheduler = BackgroundScheduler()
        
        # Daily at 18:00
        hour, minute = map(int, config.SCHEDULE_TIME.split(':'))
        scheduler.add_job(
            self.daily_full_audit,
            'cron',
            hour=hour,
            minute=minute,
            id='daily_audit',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info(f"⏰ Scheduler started - daily audit at {config.SCHEDULE_TIME}")
        return scheduler


if __name__ == "__main__":
    auditor = DailyAuditor()
    auditor.daily_full_audit()

