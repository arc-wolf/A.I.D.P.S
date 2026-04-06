# Architecture Overview

## Component Diagram
```
Browser → Flask (main.py)
  ↓
[Frontend: Bootstrap + JS Workflow]
  ↓ AJAX
Backend Routes:
├── Scan (/scan) → Scapy NetworkScanner
├── Detect (/detect) → ServiceDetector  
├── Provision (/bulk_provision) → Paramiko Provisioners
├── Inventory → SQLite + MongoDB
└── Export → Pandas Excel

Automation → APScheduler DailyAuditor
Ansible → inventory_generator.py
```

## Data Flow
1. **Discovery**: ARP scan → SQLite devices
2. **Detection**: Port scan → Update services
3. **Inventory**: SSH/WinRM inventory → Mongo software
4. **Export**: Query DB → XLSX
5. **Ansible**: DB dump → inventory.ini

## UI Connectors Flow
```
Global Nav → Workflow Wizard (Stepper)
  1. Scan Modal
  2. Detect Prompt
  3. Bulk Provision
  4. Auto Export + Ansible
```

**Scalable, modular MVC architecture.**
