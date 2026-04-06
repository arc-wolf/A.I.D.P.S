# A.I.D.P.S Setup Steps Tracking

## Completed:
- [x] venv exists and activated
- [x] pip upgraded to 26.0.1

## Pending:
- [ ] Edit requirements.txt to remove 'sqlite3' line
- [ ] pip install -r requirements.txt
- [ ] docker compose up -d mongodb (fix daemon if needed)
- [ ] cp .env.example .env (if .env missing or incomplete)
- [ ] python main.py
- [ ] Access http://localhost:5000 (admin/admin)

**Notes:** 
- Docker daemon error: ensure Docker service running (`sudo systemctl start docker`).
- Use `docker compose` (no hyphen) for modern Docker.
- Update checkboxes after each step.

