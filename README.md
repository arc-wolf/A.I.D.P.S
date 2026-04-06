# A.I.D.P.S - Automated Infrastructure Discovery & Provisioning System

## Overview

Enterprise-style lab infrastructure management platform for:

* Network discovery (ARP scanning)
* Service detection (SSH/WinRM)
* Remote management enablement
* SQL inventory (SQLite)
* Software tracking (MongoDB)
* Automated provisioning (Ansible)
* Web dashboard (Flask + Bootstrap)
* Excel reports
* Daily audits

## Architecture

```
aidps/
├── backend/         # Flask API + core logic
├── core/            # Shared utilities
├── frontend/        # HTML templates + static assets
├── scheduler/       # Daily cron jobs
├── requirements.txt
├── main.py
└── .env.example
```

## Features

- 🔍 Subnet scanning (scapy ARP)
- 🧠 OS detection (port scanning)
- 🔐 SSH/WinRM provisioning (paramiko)
- 🗄️ SQL inventory (SQLite)
- 📦 Software inventory (MongoDB)
- ⏰ Scheduled scans
- 📊 Bootstrap dashboard
- 📥 Excel export
- 🎛️ Ansible integration

## 🚀 Quick Start

```bash
cd A.I.D.P.S

# 1. Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\\Scripts\\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment
cp .env.example .env
# Edit .env with SCAN_SUBNET and credentials

# 4. Start MongoDB
docker-compose up -d mongodb

# 5. Run application
python main.py
```

**Access**: http://localhost:5000 (admin/admin)

## 📱 Usage Guide

1. **Login** → Dashboard
2. **Scan Network** → Discover devices
3. **View Devices** → Check services/status
4. **Provision** → Enable SSH/WinRM
5. **Export Excel** → Download reports
6. **Ansible**: `/ansible/inventory` → Generate inventory.ini

## 🧪 Testing

```bash
pip install -r requirements-dev.txt
python -m pytest tests/
```


## Usage

1. **Scan Network**: `/scan?subnet=192.168.1.0/24`
2. **Dashboard**: `http://localhost:5000`
3. **Export**: `/export/excel`

## Development

```bash
# Install deps
pip install -r requirements-dev.txt

# Run tests
pytest

# Lint
flake8 .
```

## Requirements

- Python 3.10+
- Docker (MongoDB)
- Local lab network access
- Root/admin for scapy

## Security

```
.env stores credentials securely
Basic auth on UI
No hardcoded passwords
Timeout handling
```

---

**Production-ready infrastructure management for lab environments**

