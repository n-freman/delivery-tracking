#!/bin/bash
set -e

echo "=== DMCargo Production Setup ==="

# ── System update ─────────────────────────────────────────────────────────────
apt update && apt upgrade -y

# ── Install system packages ───────────────────────────────────────────────────
apt install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    python3-dev \
    postgresql \
    postgresql-contrib \
    nginx \
    curl \
    git \
    build-essential \
    libpq-dev \
    gettext

# ── Install Poetry ────────────────────────────────────────────────────────────
curl -sSL https://install.python-poetry.org | python3 -
export PATH="/root/.local/bin:$PATH"

# ── Configure PostgreSQL ──────────────────────────────────────────────────────
echo "=== Setting up PostgreSQL ==="
DB_NAME="dmcargo"
DB_USER="dmcargo"
DB_PASS=$(openssl rand -base64 16)

sudo -u postgres psql <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

echo "DATABASE_URL=postgres://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME" >> .env
echo "✅ PostgreSQL configured. DB: $DB_NAME, User: $DB_USER"

# ── Install Python dependencies ───────────────────────────────────────────────
echo "=== Installing Python dependencies ==="
poetry install --only main --no-root

# ── Django setup ──────────────────────────────────────────────────────────────
echo "=== Running Django setup ==="
poetry run python src/manage.py migrate
poetry run python src/manage.py collectstatic --noinput
cd src && poetry run django-admin compilemessages && cd ..

# ── Install Gunicorn config ───────────────────────────────────────────────────
echo "=== Configuring Gunicorn ==="
cp configs/gunicorn/gunicorn.conf.py /etc/gunicorn.conf.py

cat > /etc/systemd/system/dmcargo.service <<EOF
[Unit]
Description=DMCargo Gunicorn Daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$(pwd)
EnvironmentFile=$(pwd)/.env
ExecStart=$(which poetry) run gunicorn \
    --config /etc/gunicorn.conf.py \
    --chdir $(pwd)/src \
    core.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable dmcargo
systemctl start dmcargo
echo "✅ Gunicorn service started"

# ── Configure Nginx ───────────────────────────────────────────────────────────
echo "=== Configuring Nginx ==="
ln -sf $(pwd)/configs/nginx/delivery_tracking.conf /etc/nginx/sites-enabled/dmcargo.conf
nginx -t
systemctl enable nginx
systemctl restart nginx
echo "✅ Nginx configured"

echo ""
echo "=== ✅ Setup complete ==="
echo "Database password saved to .env"
echo "Make sure to fill in remaining .env variables (SECRET_KEY, TELEGRAM_BOT_TOKEN, etc.)"