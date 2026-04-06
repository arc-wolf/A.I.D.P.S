# API & UI Reference

## Endpoints
| Route | Method | Description |
|-------|--------|-------------|
| `/scan` | POST `{subnet}` | Network discovery |
| `/detect` | POST `{ips[]}` | Service detection |
| `/bulk_provision` | POST `{ips[]}` | Bulk remote access |
| `/ansible/inventory` | GET | Generate Ansible file |
| `/api/stats` | GET | Dashboard metrics |
| `/api/devices` | GET | Device list JSON |

## UI Tutorial
**Workflow Wizard:**
- Dashboard → Full Workflow button
- Step 1: Enter subnet
- Step 2: Comma-separated IPs
- Step 3: Auto-provision
- Step 4: Download Excel + Ansible

**Bulk:**
- Devices → Checkboxes
- Actions dropdown → Execute

**Pro Tips:**
- Global search filters tables
- Progress bars for long ops
- Toasts for feedback

**Complete interactive system!**
