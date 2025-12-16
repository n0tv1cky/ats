# ATS Setup Guide

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)
- PostgreSQL 15+ (if running database locally)

## Quick Start

### Using Docker (Recommended)

1. **Set up environment files:**

   ```bash
   # Copy example files and fill in your actual values
   cp env_files/.env.dev.example env_files/.env.dev
   cp env_files/.env.prod.example env_files/.env.prod
   # Edit .env.dev and .env.prod with your actual API keys and secrets
   # IMPORTANT: These files are gitignored and will NOT be committed
   ```

2. **Start development environment:**

   ```bash
   make dev
   ```

3. **Seed initial data:**

   ```bash
   make seed
   ```

4. **Access the application:**
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Frontend: http://localhost:3000

### Local Development

1. **Set up backend:**

   ```bash
   cd services/backend
   pip install -r requirements.txt
   ```

2. **Set up frontend:**

   ```bash
   cd services/frontend
   npm install
   ```

3. **Set up database:**

   - Start PostgreSQL locally or use Docker:
     ```bash
     docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=ats_password -e POSTGRES_DB=ats_db postgres:15
     ```

4. **Run migrations:**

   ```bash
   cd services/backend
   alembic upgrade head
   ```

5. **Seed data:**

   ```bash
   python scripts/seed_data.py
   ```

6. **Start backend:**

   ```bash
   cd services/backend
   python main.py
   ```

7. **Start frontend:**
   ```bash
   cd services/frontend
   npm run dev
   ```

## Default Credentials

- Email: `admin@ucube.ai`
- Password: `admin123` (development) / Check `.env.prod` for production

## API Endpoints

- Health: `GET /health`
- Ready: `GET /ready`
- API Docs: `GET /docs`
- API Root: `GET /api/v1/`

## Database Migrations

Create a new migration:

```bash
make migrate-create message="description of changes"
```

Apply migrations:

```bash
make migrate
```

## Project Structure

```
.
├── services/
│   ├── backend/          # FastAPI backend
│   └── frontend/         # Next.js frontend
├── docker-compose.dev.yaml
├── docker-compose.prod.yaml
├── env_files/            # Environment configurations
├── docs/                 # Documentation
├── tests/                # Integration tests
├── scripts/              # Utility scripts
└── Makefile              # Common commands
```

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running
- Check DATABASE_URL in environment files
- Verify database credentials

### Port Conflicts

- Change ports in docker-compose files if needed
- Backend default: 8000
- Frontend default: 3000
- Database default: 5432

### Migration Issues

- Ensure database is created
- Check alembic.ini configuration
- Verify model imports in migrations/env.py
