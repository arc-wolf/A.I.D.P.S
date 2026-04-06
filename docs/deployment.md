# Deployment Guide

## Development
```bash
cd A.I.D.P.S
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
docker-compose up -d
python main.py
```

## Production
1. **Gunicorn + Nginx**
```
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

2. **Env Vars** (.env)
```
SCAN_SUBNET=192.168.1.0/24
SECRET_KEY=your-secret
MONGODB_URI=mongodb://localhost:27017/aidps
FLASK_ENV=production
```

3. **Docker Full Stack**
Add Flask Dockerfile, docker-compose.prod.yml.

## Testing
```bash
pytest tests/
flake8 .
```

**Ready for lab/prod deployment!**
