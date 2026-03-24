# Expense Tracker VPS

A clean and lightweight personal expense tracking web application with real-time server monitoring.

Track your daily spending, categorize expenses, view totals, and monitor your server's resources — all in one modern interface.

## Features

- Add new expenses with amount, category, and description
- View and manage all recorded expenses
- Automatic total spending calculation
- Real-time server monitoring (CPU, Memory, Disk, Network, Top processes)
- Auto-refreshing server stats every 5 seconds
- Responsive and clean UI built with Tailwind CSS
- Fully containerized with Docker and docker-compose

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML + Tailwind CSS + Vanilla JavaScript
- **Database**: SQLite
- **Containerization**: Docker + docker-compose
- **Reverse Proxy**: Caddy
- **Monitoring**: psutil

## Quick Start (Recommended)

### Using Docker (easiest way)

```bash
# 1. Clone the repository
git clone https://github.com/yhdessa/yaisj.git
cd yaisj

# 2. Start the application
docker compose up -d --build

# 3. Open in browser
http://localhost/
```

**Available URLs:**
- Main Application: http://localhost/
- API Documentation (Swagger): http://localhost/docs
- Health Check: http://localhost/health

### Running Locally without Docker

```bash
git clone https://github.com/yhdessa/yaisj.git
cd yaisj

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

Then open: http://127.0.0.1:8000/static/index.html

## Project Structure

```
yaisj/
├── app/
│   └── main.py                 # FastAPI backend + endpoints
├── static/
│   └── index.html              # Single-page frontend
├── .env                        # Environment variables
├── expenses.db                 # SQLite database (gitignored)
├── Dockerfile
├── docker-compose.yml
├── Caddyfile
├── requirements.txt
├── .gitignore
└── README.md
```

## Main API Endpoints

| Method | Endpoint       | Description                              |
|--------|----------------|------------------------------------------|
| POST   | `/expenses/`   | Create a new expense                     |
| GET    | `/expenses/`   | Get all expenses                         |
| GET    | `/system/`     | Real-time server resource statistics     |
| GET    | `/health`      | Health check endpoint                    |

Full interactive API documentation is available at `/docs`.

## Environment Variables

The project uses a `.env` file for configuration. You can customize:
- `APP_TITLE`
- `DEBUG`
- `DOMAIN`
- `EMAIL` (used for Let's Encrypt on production)
