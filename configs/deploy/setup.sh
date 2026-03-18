#!/bin/bash
set -e

echo "=== DMCargo Production Setup ==="

APP_DIR=$(pwd)
APP_USER="dmcargo"
VENV="$APP_DIR/.venv"
PYTHON="$VENV/bin/python"
PIP="$VENV/bin/pip"
GUNICORN="$VENV/bin/gunicorn"

mkdir -p $APP_DIR/run
mkdir -p $APP_DIR/logs
chown -R $APP_USER:$APP_USER $APP_DIR/run
chown -R $APP_USER:$APP_USER $APP_DIR/logs

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
ALTER DATABASE $DB_NAME OWNER TO $DB_USER;
EOF

# append db vars to .env
cat >> .env <<EOF
DB_ENGINE=django.db.backends.postgresql
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASS
DB_HOST=localhost
DB_PORT=5432
EOF

echo "✅ PostgreSQL configured. DB: $DB_NAME, User: $DB_USER"

# ── Python virtualenv ─────────────────────────────────────────────────────────
echo "=== Setting up Python virtualenv ==="
python3.12 -m venv $VENV
$PIP install --upgrade pip
$PIP install -r requirements.txt
echo "✅ Dependencies installed"

# ── Django setup ──────────────────────────────────────────────────────────────
echo "=== Running Django setup ==="
$PYTHON src/manage.py migrate
$PYTHON src/manage.py collectstatic --noinput
cd src && ../  $VENV/bin/django-admin compilemessages && cd ..
echo "✅ Django setup complete"

# ── Fix ownership ─────────────────────────────────────────────────────────────
echo "=== Setting file ownership ==="
chown -R $APP_USER:$APP_USER $APP_DIR
echo "✅ Ownership set to $APP_USER"

# ── Gunicorn systemd service ──────────────────────────────────────────────────
echo "=== Configuring Gunicorn ==="

cp $APP_DIR/configs/deploy/dmcargo.service /etc/systemd/system/dmcargo.service
systemctl daemon-reload
systemctl enable dmcargo
systemctl start dmcargo

echo "✅ Gunicorn service started"

# ── Configure Nginx ───────────────────────────────────────────────────────────
echo "=== Configuring Nginx ==="
ln -sf $APP_DIR/configs/nginx/delivery_tracking.conf /etc/nginx/sites-enabled/dmcargo.conf
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl enable nginx
systemctl restart nginx
echo "✅ Nginx configured"

echo ""
echo "=== ✅ Setup complete ==="
echo "DB credentials have been written to .env"
echo "Make sure to fill in remaining .env variables:"
echo "  SECRET_KEY, TELEGRAM_BOT_TOKEN, ALLOWED_HOSTS, DEBUG=False"