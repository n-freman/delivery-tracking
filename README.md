# DMCargo — Delivery Tracking

A Django-based delivery tracking web application with a client-facing interface and admin panel. Supports order management, product tracking, multilingual UI (English, Russian, Turkmen), and Telegram notifications.

---

## Tech Stack

- **Python** 3.11
- **Django** 4.2+
- **PostgreSQL** (production) / SQLite (development)
- **Poetry** for dependency management
- **Gunicorn** + **Nginx** for production serving
- **Telegram Bot API** for admin notifications

---

## Project Structure

```
.
├── configs/
│   ├── nginx/
│   │   └── delivery_tracking.conf
│   └── gunicorn/
│       └── gunicorn.conf.py
├── src/
│   ├── apps/
│   │   ├── authentication/   # Custom user model, login/logout views
│   │   ├── general/          # Index page, notifications, telegram helper
│   │   ├── orders/           # Order model, views, forms, signals
│   │   └── products/         # Product model
│   ├── core/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── locale/
│   │   ├── en/
│   │   ├── ru/
│   │   └── tk/
│   ├── static/
│   │   └── css/
│   │       └── main.css
│   ├── templates/
│   │   ├── base.html
│   │   ├── admin/
│   │   │   └── base_site.html
│   │   ├── auth/
│   │   ├── general/
│   │   ├── orders/
│   │   └── partials/
│   └── manage.py
├── tests/
│   └── test_models.py
├── Makefile
├── pyproject.toml
└── poetry.lock
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourname/delivery-tracking.git
cd delivery-tracking
```

### 2. Install dependencies

```bash
make install
```

### 3. Set up environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_CHAT_ID=your-chat-id
```

### 4. Run migrations

```bash
make migrate
```

### 5. Create a superuser

```bash
poetry run python src/manage.py createsuperuser
```

### 6. Compile translations

```bash
make compilemessages
```

### 7. Start the development server

```bash
make run
```

Visit [http://localhost:8000](http://localhost:8000)
Admin panel: [http://localhost:8000/admin](http://localhost:8000/admin)

---

## Makefile Commands

| Command | Description |
|---|---|
| `make install` | Install dependencies via Poetry |
| `make run` | Start Django development server |
| `make migrate` | Apply database migrations |
| `make migrations` | Create new migrations |
| `make collectstatic` | Collect static files |
| `make messages` | Extract translatable strings |
| `make compilemessages` | Compile `.po` files into `.mo` |
| `make lint` | Check code with black and isort |
| `make format` | Auto-format code with black and isort |
| `make test` | Run all tests |
| `make test-app APP=orders` | Run tests for a specific app |
| `make test-cov` | Run tests with coverage report |
| `make nginx-link` | Symlink nginx config to sites-enabled |
| `make nginx-reload` | Reload nginx |
| `make deploy` | Full deploy (migrate, collectstatic, compilemessages, nginx-reload) |

---

## Features

### Client Side
- Login / logout
- View recent orders on the home page
- Full order management — create, view, edit, delete
- Inline product management within orders
- Website notifications when an order is marked as reviewed

### Admin Panel
- Custom branded Django admin (DMCargo theme)
- Order and product management with fieldsets
- Inline product editing within orders

### Internationalization
- Three languages: English, Russian, Turkmen
- Language switcher in the header (session-based, no URL prefixes)
- All models, views, and templates are fully translated

### Telegram Notifications
- Admin receives a Telegram message (in Russian) when a user creates a new order
- Message includes order ID, user, delivery type, payment type, and product count

---

## Translations

Translation source files are in `src/locale/`. Only `.po` files are committed — `.mo` files are compiled during deployment.

To add new translatable strings:

```bash
make messages       # extracts strings into .po files
# edit .po files manually
make compilemessages  # compiles .po into .mo
```

---

## Deployment

### 1. Set up nginx

```bash
make nginx-link
make nginx-test
make nginx-reload
```

### 2. Full deploy

```bash
make deploy
```

This runs migrations, collects static files, compiles translations, tests nginx config, and reloads nginx.

---

## Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Debug mode (`True` / `False`) |
| `DATABASE_URL` | Database connection string |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token for notifications |
| `TELEGRAM_ADMIN_CHAT_ID` | Telegram chat ID to receive admin notifications |

---

## Running Tests

```bash
make test                      # all tests
make test-app APP=orders       # orders app only
make test-app APP=products     # products app only
make test-cov                  # with coverage report
```