from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, session
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from core.config import config
from backend.discovery.network_scan import NetworkScanner
from backend.detection.service_detect import ServiceDetector
from backend.database.device_inventory import DeviceInventory
from backend.database.software_inventory import SoftwareInventory
from backend.export.excel_export import ExcelExporter
from backend.provisioning.linux_ssh import LinuxSSHProvisioner
from backend.provisioning.windows_winrm import WindowsWinRMProvisioner
from scheduler.daily_audit import DailyAuditor
from ansible_inventory_generator import generate_ansible_inventory
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            template_folder='frontend/templates',
            static_folder='frontend/static')
app.config.from_object(config)
app.secret_key = config.SECRET_KEY

# Basic auth (username: admin, password: admin - CHANGE IN PRODUCTION)
USERS = {'admin': generate_password_hash('admin')}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and check_password_hash(USERS[username], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    inventory = DeviceInventory()
    swinv = SoftwareInventory()
    
    stats = inventory.get_stats()
    recent_software = swinv.get_recent_inventories(days=7)
    
    return render_template('dashboard.html', stats=stats, recent_sw=recent_software)

@app.route('/devices')
@login_required
def devices():
    inventory = DeviceInventory()
    devices = inventory.get_all_devices()
    return render_template('devices.html', devices=devices)

@app.route('/device/<ip>')
@login_required
def device_detail(ip):
    inventory = DeviceInventory()
    swinv = SoftwareInventory()
    
    device = inventory.get_device_by_ip(ip)
    software = swinv.get_software_by_ip(ip)
    
    return render_template('device_detail.html', device=device, software=software)

@app.route('/scan', methods=['POST'])
@login_required
def scan_network():
    subnet = request.json.get('subnet', config.SCAN_SUBNET)
    scanner = NetworkScanner()
    devices = scanner.scan_subnet(subnet)
    return jsonify({'success': True, 'count': len(devices), 'devices': devices})

@app.route('/detect', methods=['POST'])
@login_required
def detect_services():
    ips = request.json.get('ips', [])
    detector = ServiceDetector()
    results = detector.scan_services_parallel([{'ip': ip} for ip in ips])
    return jsonify({'success': True, 'results': results})

@app.route('/provision/<ip>')
@login_required
def provision_device(ip):
    inventory = DeviceInventory()
    device = inventory.get_device_by_ip(ip)
    os_type = device['os_type'] if device else 'unknown'
    
    if os_type == 'linux':
        result = LinuxSSHProvisioner().enable_ssh_access(ip)
    elif os_type == 'windows':
        result = WindowsWinRMProvisioner().enable_winrm(ip)
    else:
        result = {'success': False, 'error': 'Unknown OS type or device not found'}
    
    return jsonify(result)

@app.route('/export')
@login_required
def export_excel():
    exporter = ExcelExporter()
    filename = 'lab_inventory.xlsx'
    result = exporter.export_devices(filename)
    return send_file(filename, as_attachment=True)

@app.route('/ansible/inventory')
@login_required
def generate_inventory():
    generate_ansible_inventory()
    return jsonify({'success': True, 'message': f'Ansible inventory generated: {config.ANSIBLE_INVENTORY}'})

@app.route('/api/stats')
@login_required
def api_stats():
    inventory = DeviceInventory()
    return jsonify(inventory.get_stats())

@app.route('/api/devices')
@login_required
def api_devices():
    inventory = DeviceInventory()
    return jsonify(inventory.get_all_devices())

if __name__ == '__main__':
    # Start scheduler
    auditor = DailyAuditor()
    scheduler = auditor.start_scheduler()
    
    # Run Flask
    app.run(host='0.0.0.0', port=5000, debug=config.FLASK_ENV == 'development')

