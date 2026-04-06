# Build A.I.D.P.S From Scratch - Complete Prompt

**Detailed recreation prompt for AI/coder to build exact project.**

## Tech Stack
- Backend: Flask, Scapy, Paramiko, Pandas, PyMongo
- Frontend: Bootstrap 5, Jinja2, vanilla JS
- DB: SQLite + MongoDB
- Tools: APScheduler, Docker

## File Structure (Create Exactly)
```
A.I.D.P.S/
├── main.py (Flask app)
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── README.md
├── core/config.py
├── backend/database/device_inventory.py
├── backend/database/software_inventory.py
├── backend/discovery/network_scan.py
├── backend/detection/service_detect.py
├── backend/provisioning/linux_ssh.py
├── backend/provisioning/windows_winrm.py
├── backend/export/excel_export.py
├── scheduler/daily_audit.py
├── ansible_inventory_generator.py
├── frontend/templates/*.html
├── frontend/static/css/style.css
├── frontend/static/js/app.js
├── tests/*
```

## Step-by-Step Build

### 1. Core Flask App (`main.py`)
```python
from flask import Flask...
# Copy exact from project (imports, routes: login, dashboard, devices...)
# Include new: @app.route('/bulk_provision', methods=['POST'])
```

### 2. Config (`core/config.py`)
Class with env vars: SCAN_SUBNET, MONGODB_URI, SECRET_KEY...

### 3. Backend Modules (Create each)
**network_scan.py**: Scapy ARP scanner class with ThreadPoolExecutor.

**service_detect.py**: Parallel TCP SYN scanner.

**device_inventory.py**: SQLite CRUD (ip, mac, os_type, ssh_enabled...).

**software_inventory.py**: PyMongo software list.

**provisioning/**: Paramiko SSH/WinRM enablement.

### 4. Frontend
**base.html**: Navbar with workflow button, global search.

**dashboard.html**: Stats cards + **workflow stepper** (4 steps).

**devices.html**: Table with checkboxes + bulk dropdown.

**app.js**: ajaxRequest, workflowWizard, bulkProvision, stepper logic.

### 5. Features to Implement Exactly
- Basic auth (admin/admin hashed)
- AJAX scan/provision/bulk
- Progress bars/toasts
- Responsive stepper UI
- Ansible inventory generator from DB

### 6. Dependencies (`requirements.txt`)
```
flask==2.3.3
scapy==2.5.0
paramiko==3.4.0
pandas==2.1.3
pymongo==4.6.0
apscheduler==3.10.4
python-dotenv==1.0.0
werkzeug==2.3.7
openpyxl==3.1.2
```

### 7. Docker (`docker-compose.yml`)
MongoDB service.

**Validation:** Run `pytest`, scan network, test workflow end-to-end.

**This prompt recreates 100% identical project.**
