# Wordle Game - Deployment Guide

## Prerequisites (Ubuntu Server 22.04+)
- Python 3.11+
- Node.js 20+
- PostgreSQL 16
- Nginx
- Certbot (Let's Encrypt)

## Quick Deploy
```bash
# 1. Clone
git clone https://github.com/caiyilian/wordle_game.git /opt/wordle
cd /opt/wordle

# 2. Backend setup
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env  # edit DATABASE_URL, JWT_SECRET

# 3. Database
sudo -u postgres createdb wordle
alembic upgrade head

# 4. Frontend build
cd frontend && npm install && npm run build

# 5. Setup systemd service
sudo cp deploy/wordle.service /etc/systemd/system/
sudo systemctl enable --now wordle

# 6. Setup Nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/wordle
sudo ln -s /etc/nginx/sites-available/wordle /etc/nginx/sites-enabled/
sudo certbot --nginx -d your-domain.com
sudo nginx -s reload
```

## Files
- `deploy/nginx.conf` - Nginx reverse proxy config
- `deploy/wordle.service` - systemd service unit
- `deploy/.env.example` - Environment variables template
