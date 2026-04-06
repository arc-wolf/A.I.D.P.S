# A.I.D.P.S Documentation

## Automated Infrastructure Discovery & Provisioning System

**Production-ready Flask app for lab network management.**

### Quick Start Tutorial

1. **Clone & Setup**
```bash
git clone <repo>
cd A.I.D.P.S
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

2. **Services**
```bash
docker-compose up -d  # MongoDB
```

3. **Run**
```bash
python main.py
```
**Access**: http://localhost:5000 (admin/admin)

### UI Tutorial - New Connectors!

**Dashboard Workflow Wizard:**
1. Click **Full Workflow** → Follow stepper:
   - Scan subnet → Prompt subnet
   - Detect services → Enter IPs
   - Provision → Auto OS-based
   - Export + Ansible generated

**Devices Bulk Actions:**
1. Checkboxes + **Actions** dropdown
2. Provision/Detect/Export selected devices

**Global Features:**
- Navbar search
- Live progress bars
- Responsive mobile

### Features
| Module | Description |
|--------|-------------|
| Network Scan | Scapy ARP subnet discovery |
| Service Detect | TCP SYN port scanning |
| Provisioning | SSH/WinRM auto-setup |
| Inventory | SQLite devices + Mongo software |
| Export | Excel reports |
| Automation | Daily audits + Ansible integration |

**Full docs in sidebar.**
