.PHONY: help install migrate collectstatic lint format test run \
        nginx-link nginx-reload nginx-test gunicorn deploy

# ── Variables ────────────────────────────────────────────────────────────────
PROJECT_NAME   = delivery_tracking
SRC_DIR        = src
MANAGE         = poetry run python $(SRC_DIR)/manage.py
NGINX_CONF     = $(PWD)/configs/nginx/$(PROJECT_NAME).conf
NGINX_ENABLED  = /etc/nginx/sites-enabled/$(PROJECT_NAME).conf

# ── Help ─────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "  Dev"
	@echo "    install        Install dependencies via poetry"
	@echo "    run            Start Django development server"
	@echo "    migrate        Run database migrations"
	@echo "    migrations     Create new migrations"
	@echo "    collectstatic  Collect static files"
	@echo "    messages       Extract translatable strings into .po files"
	@echo "    compilemessages  Compile .po files into .mo files"
	@echo ""
	@echo "  Code Quality"
	@echo "    lint           Check code with black and isort (no changes)"
	@echo "    format         Auto-format code with black and isort"
	@echo ""
	@echo "  Testing"
	@echo "    test           Run all tests"
	@echo "    test-app       Run tests for a specific app  (make test-app APP=orders)"
	@echo "    test-cov       Run tests with coverage report"
	@echo ""
	@echo "  Nginx"
	@echo "    nginx-link     Symlink nginx config to sites-enabled"
	@echo "    nginx-unlink   Remove nginx symlink from sites-enabled"
	@echo "    nginx-test     Test nginx configuration"
	@echo "    nginx-reload   Reload nginx"
	@echo ""
	@echo "  Production"
	@echo "    setup          Provision a fresh server (postgres, nginx, gunicorn, deps)"
	@echo "    deploy         Release update (migrate, collectstatic, compilemessages, nginx-reload)"
	@echo "    gunicorn       Start gunicorn server manually"
	@echo "    restart        Restart gunicorn service and reload nginx"
	@echo ""

# ── Dev ───────────────────────────────────────────────────────────────────────
install:
	poetry install

run:
	$(MANAGE) runserver

migrate:
	$(MANAGE) migrate

migrations:
	$(MANAGE) makemigrations

messages:
	cd $(SRC_DIR) && poetry run django-admin makemessages -a

compilemessages:
	cd $(SRC_DIR) && poetry run django-admin compilemessages

collectstatic:
	$(MANAGE) collectstatic --noinput

# ── Code Quality ─────────────────────────────────────────────────────────────
lint:
	poetry run black --check $(SRC_DIR)
	poetry run isort --check-only $(SRC_DIR)

format:
	poetry run black $(SRC_DIR)
	poetry run isort $(SRC_DIR)

# ── Testing ───────────────────────────────────────────────────────────────────
test:
	poetry run pytest

test-app:
	poetry run pytest $(SRC_DIR)/apps/$(APP)/tests.py -v

test-cov:
	poetry run pytest --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html

# ── Nginx ─────────────────────────────────────────────────────────────────────
nginx-link:
	@echo "Linking nginx config..."
	sudo ln -sf $(NGINX_CONF) $(NGINX_ENABLED)
	@echo "Linked $(NGINX_CONF) → $(NGINX_ENABLED)"

nginx-unlink:
	@echo "Removing nginx symlink..."
	sudo rm -f $(NGINX_ENABLED)
	@echo "Removed $(NGINX_ENABLED)"

nginx-test:
	sudo nginx -t

nginx-reload:
	sudo nginx -s reload

# ── Gunicorn ──────────────────────────────────────────────────────────────────
gunicorn:
	poetry run gunicorn \
		--config configs/gunicorn/gunicorn.conf.py \
		--chdir $(SRC_DIR) \
		core.wsgi:application

# ── Deploy ────────────────────────────────────────────────────────────────────
deploy: migrate collectstatic nginx-test nginx-reload
	@echo "Deploy complete."

setup:
	chmod +x configs/deploy/setup.sh
	sudo configs/deploy/setup.sh

restart:
	sudo systemctl restart dmcargo
	sudo nginx -s reload
