# Expense Tracker VPS

A simple, lightweight web application for tracking personal expenses with real-time server resource monitoring.

Record daily spending, categorize transactions, add notes, view totals, and keep an eye on your server's health — all in one modern interface.

## Features

- Add expenses with amount, category, and optional description
- View complete list of recorded expenses
- Automatic total spending calculation
- Real-time server stats (CPU, memory, disk usage, network I/O, top processes)
- Responsive design — works great on desktop and mobile
- Clean, modern UI with Tailwind CSS
- Data stored locally in SQLite

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML + Tailwind CSS + vanilla JavaScript
- **Database**: SQLite
- **Containerization**: Docker + docker-compose
- **Reverse proxy & auto-HTTPS**: Caddy
- **Monitoring**: psutil

## Quick Start

### Recommended: Run with Docker

```bash
# 1. Clone the repository
git clone https://github.com/yhdessa/yaisj.git
cd yaisj

# 2. Start the application (builds and runs in background)
docker compose up -d --build

# 3. Open in your browser
http://localhost/
```

- Main app: http://localhost/
- API documentation (Swagger): http://localhost/docs

### Alternative: Run locally without Docker

```bash
# 1. Clone the repo
git clone https://github.com/yhdessa/yaisj.git
cd yaisj

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the backend
uvicorn app.main:app --reload --port 8000

# 5. Open the frontend
http://127.0.0.1:8000/static/index.html

# API docs
http://127.0.0.1:8000/docs
```

## Project Structure

```
yaisj/
├── app/
│   └── main.py             # FastAPI app + endpoints + logic
├── static/
│   └── index.html          # Single-page frontend
├── expenses.db             # SQLite database (gitignored)
├── Dockerfile
├── docker-compose.yml
├── Caddyfile
├── requirements.txt
├── .gitignore
└── README.md
```

## Main API Endpoints

| Method | Endpoint       | Description                          |
|--------|----------------|--------------------------------------|
| POST   | `/expenses/`   | Create a new expense                 |
| GET    | `/expenses/`   | Get list of all expenses             |
| GET    | `/system/`     | Current server resource statistics   |
| GET    | `/health`      | Simple health check                  |

Full interactive API documentation is available at `/docs` when the server is running.
