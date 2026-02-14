# HRMS Lite

A lightweight **Human Resource Management System** with employee management and attendance tracking. Built with a FastAPI backend (Python), React + Vite frontend (TypeScript), and MongoDB for data storage.

---

## Features

- **Employee Management** – Create, list, filter, and soft-delete employees (by department, search).
- **Attendance** – Mark daily attendance (present, absent, half-day, leave) with date ranges and filters.
- **Employee Attendance Stats** – Per-employee stats (present/absent/half-day/leave counts and attendance rate) for a date range.
- **Dashboard** – Overview and navigation to employees and attendance.
- **REST API** – Documented with OpenAPI/Swagger at `/docs`.
- **Production-ready** – Docker Compose stack, health checks, CORS, security headers, optional MongoDB Atlas.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React + Vite)                  │
│  Dashboard | Employees | Attendance | React Query, Axios, Tailwind │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP /api/v1/*
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Nginx (in Docker) or dev proxy                 │
│  SPA routing, /api → backend, gzip, security headers             │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                            │
│  /api/v1/employees, /api/v1/attendance, /health, /docs           │
└───────────────────────────────┬─────────────────────────────────┘
                                │ Motor (async)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MongoDB (Atlas or self-hosted)              │
│  employees, attendance collections, indexes                     │
└─────────────────────────────────────────────────────────────────┘
```

- **Backend**: FastAPI, Pydantic, Motor (async MongoDB), Uvicorn.
- **Frontend**: React 19, Vite 6, React Router 7, TanStack Query, Axios, Tailwind CSS 4.
- **Deployment**: Docker Compose builds backend + frontend; frontend serves static assets and proxies `/api` to the backend. Database is external (e.g. MongoDB Atlas).

---

## Quick Start

1. **Clone and configure**
   ```bash
   git clone <repository-url>
   cd hrms-lite
   cp env.example .env
   # Edit .env: set MONGODB_URL, SECRET_KEY, ALLOWED_ORIGINS
   ```

2. **Run with Docker Compose**
   ```bash
   docker compose up -d
   ```
   Frontend: http://localhost:3002 (or `FRONTEND_PORT` from `.env`).  
   API: http://localhost:3002/api/v1 (proxied through frontend container).

3. **Optional: seed data**
   ```bash
   cd backend
   python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt pymongo
   python scripts/seed_employees.py
   python scripts/seed_dummy_attendance.py
   ```

For **local development** (no Docker), see [SETUP_GUIDE.md](docs/SETUP_GUIDE.md).  
For **self-deployment** (server, domain, MongoDB Atlas), see [DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## Repository Structure

```
hrms-lite/
├── backend/                 # FastAPI app
│   ├── app/
│   │   ├── main.py           # App entry, lifespan, /health
│   │   ├── config/           # settings, database, logging
│   │   ├── api/v1/           # router, endpoints (employees, attendance)
│   │   ├── models/           # Pydantic models (employee, attendance)
│   │   ├── schemas/          # API request/response schemas
│   │   ├── services/         # Repository / business logic
│   │   ├── middleware/       # CORS, errors, request ID/timing
│   │   └── core/             # Exceptions
│   ├── scripts/              # seed_employees, seed_dummy_attendance
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
├── frontend/                 # React + Vite SPA
│   ├── src/
│   │   ├── App.tsx           # Routes, layout, providers
│   │   ├── pages/            # Dashboard, Employees, Attendance, NotFound
│   │   ├── components/       # UI, table, modal, attendance, etc.
│   │   ├── services/         # axios client, API services
│   │   ├── hooks/            # React Query hooks
│   │   ├── types/            # TypeScript types
│   │   └── constants/
│   ├── package.json
│   ├── vite.config.ts
│   ├── nginx.conf            # Used in Docker
│   └── Dockerfile
├── docker-compose.yml        # backend + frontend services
├── env.example               # Template for .env
├── README.md                 # This file
└── docs/
    ├── SETUP_GUIDE.md        # Local and Docker setup
    └── DEPLOYMENT.md         # Self-deployment guide
```

---

## API Overview

| Area        | Method | Endpoint | Description |
|------------|--------|----------|-------------|
| Health     | GET    | `/health` | Service + DB health |
| Employees  | GET    | `/api/v1/employees` | List (paginated, filter by department/search) |
| Employees  | POST   | `/api/v1/employees` | Create employee |
| Employees  | GET    | `/api/v1/employees/{employee_id}` | Get by employee ID |
| Employees  | GET    | `/api/v1/employees/id/{id}` | Get by MongoDB ObjectId |
| Employees  | DELETE | `/api/v1/employees/{employee_id}` | Soft delete |
| Attendance | POST   | `/api/v1/attendance` | Mark attendance |
| Attendance | GET    | `/api/v1/attendance` | List (filters: employee_id, start_date, end_date, status) |
| Attendance | GET    | `/api/v1/attendance/employee/{id}/stats` | Employee stats in date range |

Interactive docs: **Swagger UI** at `/docs`, **ReDoc** at `/redoc` (when backend is reachable, e.g. backend URL or via proxy).

---

## Environment Summary

| Variable         | Description | Example |
|------------------|-------------|---------|
| `MONGODB_URL`    | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/...` |
| `MONGODB_DB_NAME`| Database name | `hrms_lite` |
| `SECRET_KEY`     | Backend secret (min 32 chars) | Required in production |
| `ALLOWED_ORIGINS`| CORS origins (comma-separated) | `https://your-domain.com` |
| `FRONTEND_PORT`  | Port for frontend container | `80` or `3002` |

See `env.example` and [DEPLOYMENT.md](docs/DEPLOYMENT.md) for full production settings.

---

## Documentation

- **[Setup Guide](docs/SETUP_GUIDE.md)** – Local development (backend + frontend + MongoDB) and Docker-based setup.
- **[Deployment Guide](docs/DEPLOYMENT.md)** – Self-deployment: server prep, Docker Compose, env, MongoDB Atlas, reverse proxy, SSL.

---

## License

MIT (or as specified in the repository).
