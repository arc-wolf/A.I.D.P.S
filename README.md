# A.I.D.P.S. — Automated Infrastructure Discovery & Provisioning System

A lab infrastructure management application for discovering devices on an authorized network, identifying remote-management services, maintaining an inventory, and preparing provisioning workflows.

## Features

- Subnet discovery using ARP scanning (Scapy)
- Service detection for SSH and WinRM
- Device inventory in SQLite
- Software inventory in MongoDB
- Remote-management provisioning helpers for Linux and Windows
- Ansible inventory generation
- Scheduled audits
- Flask dashboard and Excel export

## Architecture

```
aidps/
├── backend/         # Flask-integrated discovery, detection, inventory, provisioning
├── core/            # Configuration
├── frontend/        # HTML templates and static assets
├── scheduler/       # Scheduled audits
├── tests/           # Automated tests
├── requirements.txt
├── main.py
└── .env.example
```

## Setup

1. Use this project only on networks and devices you own or are explicitly authorized to administer.
2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Configure environment variables:

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Put the generated value in `SECRET_KEY`. Set a unique dashboard username and a strong password (at least 12 characters) using `AIDPS_ADMIN_USERNAME` and `AIDPS_ADMIN_PASSWORD`. Do not commit your real `.env` file.

4. Configure the target subnet and database connection details in `.env`. Start MongoDB if your software-inventory configuration requires it.
5. Start the application:

```bash
python main.py
```

The dashboard listens on port 5000. There is **no built-in admin/admin account**; startup fails if the secret key or dashboard credentials are missing or too short.

## Security and operational notes

- Keep `.env` out of version control and restrict its filesystem permissions.
- Use HTTPS when accessing the dashboard across a network. Set `SESSION_COOKIE_SECURE=true` when served over HTTPS.
- Run behind a production WSGI server and a properly configured reverse proxy; do not use Flask's development server for production.
- Use dedicated, least-privilege remote accounts. Avoid reusing personal or domain administrator credentials.
- Restrict network scanning and provisioning to explicitly authorized subnets and devices.
- Review the provisioning modules before running them: remote changes can alter SSH/WinRM settings on target machines.
- The application should receive a security review before deployment outside a trusted lab.

## Testing

Install development dependencies if the repository provides them, then run its test suite:

```bash
pytest
```

