# FastAPI Launchpad

A command-line tool to quickly scaffold FastAPI projects with best practices and common patterns.

## Features

- Quick project scaffolding with best practices
- Health check endpoint included by default
- Modern project structure following FastAPI recommendations
- Optional database setup: Postgres, MySQL, MongoDB
- Clear `.env` and `.env.example`

## Installation

```bash
pip install fastapi-launchpad
```

## Usage

- Create a new FastAPI project in a directory named `my_project`:

```bash
fastapi-launch project my-project
```

- Create with a specific database:

```bash
fastapi-launch project my-project --database postgres
# or --database mysql
# or --database mongodb
```

- Scaffold into the current directory:

```bash
mkdir my-project && cd my-project
fastapi-launch project .
```

- Show version:

```bash
fastapi-launch version
```

## Generated Project Structure

```
my_project/
├── src/
│   ├── dependencies/
│   ├── models/
│   ├── routers/
│   │   └── health.py
│   ├── schemas/
│   └── main.py
├── tests/
├── .env
├── .env.example
└── requirements.txt
```

## Running the generated app

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Unix/Mac
source venv/bin/activate

pip install -r requirements.txt
uvicorn src.main:app --reload
```

Then visit `http://127.0.0.1:8000/docs`.

## Development

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows
# or
source .venv/bin/activate # Unix/Mac

pip install -e .[dev]
pytest -q
```

## License

MIT License