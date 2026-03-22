# yaisj

A simple, lightweight personal expense tracking web application.

Track your daily spending, categorize expenses, add descriptions, and see totals — all in a clean, modern interface.

## Features

- Add new expenses with amount, category and optional description
- View list of all recorded expenses
- Automatic calculation of total spending
- Real-time server resource overview (CPU, memory, disk, network usage)
- Responsive design that works well on desktop and mobile
- Dark/light mode support (via system preference)
- Data stored locally in SQLite database

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML + Tailwind CSS + vanilla JavaScript
- **Database**: SQLite
- **Dependencies**: minimal — psutil, SQLAlchemy, Uvicorn

## Quick Start (Local Development)

1. Clone the repository

```bash
git clone https://github.com/yhdessa/yaisj.git
cd yaisj
```

2. Create and activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate    # on Windows: .venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Run the application

```bash
uvicorn app.main:app --reload --port 8000
```

5. Open in browser

- Application: http://127.0.0.1:8000/static/index.html
- API documentation: http://127.0.0.1:8000/docs

## Project Structure

```
yaisj/
├── app/
│   └── main.py             # FastAPI application + all endpoints
├── static/
│   └── index.html          # Single-page frontend
├── expenses.db             # SQLite database (gitignored)
├── requirements.txt
├── .gitignore
└── README.md
```

## API Endpoints (main ones)

| Method | Endpoint          | Description                          |
|--------|-------------------|--------------------------------------|
| POST   | `/expenses/`      | Create new expense                   |
| GET    | `/expenses/`      | List all expenses                    |
| GET    | `/system/`        | Current server resource statistics   |
| GET    | `/health`         | Simple health check                  |

Full interactive documentation available at `/docs` when server is running.

## License

MIT License

Feel free to use, modify and distribute.
