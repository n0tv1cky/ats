# Backend API

FastAPI backend for the ATS system.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp ../env_files/.env.dev .env
# Edit .env with your configuration
```

3. Run migrations:
```bash
alembic upgrade head
```

4. Seed initial data:
```bash
python ../scripts/seed_data.py
```

5. Run the server:
```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── src/
│   └── v1/
│       ├── api/            # API endpoints
│       ├── core/           # Business logic
│       ├── models/         # SQLAlchemy models
│       ├── schemas/        # Pydantic schemas
│       ├── db/             # Database configuration
│       ├── config.py       # Settings
│       └── dependencies.py # Dependency injection
├── requirements.txt
└── alembic.ini
```

