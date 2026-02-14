# HRMS Lite – Setup Guide

This guide covers setting up HRMS Lite for **local development** and **Docker-based** runs.

---

## Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.11+ (for backend)
- **MongoDB** 5.0+ (local or MongoDB Atlas)
- **Git**
- **Docker & Docker Compose** (optional, for containerized setup)

---

## Option A: Local Development (no Docker)

### 1. Clone and enter project

```bash
git clone <repository-url>
cd hrms-lite
```

### 2. MongoDB

**Option A1: Local MongoDB**

- Install MongoDB for your OS: [MongoDB Community](https://www.mongodb.com/docs/manual/installation/).
- Start MongoDB (e.g. `mongod` or via systemd).
- Default URL: `mongodb://localhost:27017`.

**Option A2: MongoDB Atlas**

- Create a cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
- Get the connection string (e.g. `mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority`).
- Use this as `MONGODB_URL` in backend `.env`.

### 3. Backend setup

```bash
cd backend
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

pip install -r requirements.txt
```

Create backend `.env`:

```bash
cp .env.example .env
# Or create .env manually
```

Minimum for local dev:

```env
MONGODB_URL=mongodb://localhost:27017
# Or: MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=hrms_lite
SECRET_KEY=dev-secret-key-change-in-production-32-chars-min
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

Run the API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- Swagger: http://localhost:8000/docs  
- Health: http://localhost:8000/health  

### 4. Frontend setup

In a **new terminal**, from project root:

```bash
cd frontend
npm install
```

Create frontend `.env` (optional for local):

```env
VITE_API_BASE_URL=http://localhost:8000
```

Run the dev server:

```bash
npm run dev
```

- App: http://localhost:5173 (Vite default).  
- Frontend will call the backend at `VITE_API_BASE_URL` (or fallback `http://localhost:8000`).

### 5. Optional: seed data

From `backend/` with venv active:

```bash
pip install pymongo   # if not already installed (motor brings pymongo; seed scripts use sync MongoClient)
python scripts/seed_employees.py
python scripts/seed_dummy_attendance.py
```

Ensure `MONGODB_URL` and `MONGODB_DB_NAME` in backend `.env` match your MongoDB.

---

## Option B: Docker Compose (backend + frontend)

Uses the root `docker-compose.yml`. **MongoDB is not included**; use Atlas or a separate MongoDB.

### 1. Clone and configure env

```bash
git clone <repository-url>
cd hrms-lite
cp env.example .env
```

Edit `.env`:

```env
MONGODB_URL=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=hrms_lite
SECRET_KEY=your-production-secret-key-at-least-32-characters-long
ALLOWED_ORIGINS=https://your-domain.com
# Optional:
FRONTEND_PORT=3002
```

For **local Docker** only (no domain yet), you can use:

```env
ALLOWED_ORIGINS=http://localhost:3002,http://127.0.0.1:3002
```

### 2. Build and run

```bash
docker compose up -d
```

- Frontend: http://localhost:3002 (or value of `FRONTEND_PORT`).  
- API is **proxied** at http://localhost:3002/api/ (nginx in frontend container proxies to backend).

### 3. Health checks

- Frontend: http://localhost:3002/  
- Backend health (via proxy): http://localhost:3002/api/v1/… or add a route that hits backend `/health`; or temporarily expose backend port for debugging.

To expose backend port 8000 for debugging:

```yaml
# In docker-compose.yml, under backend service, add:
ports:
  - "8000:8000"
```

Then http://localhost:8000/health and http://localhost:8000/docs.

### 4. Seed data with Docker

Using backend container:

```bash
docker compose exec backend sh
# Inside container (no venv needed):
pip install pymongo
python scripts/seed_employees.py
python scripts/seed_dummy_attendance.py
exit
```

Or run scripts on host with same env: from `backend/`, set `MONGODB_URL`/`MONGODB_DB_NAME` to your Atlas (or host-accessible MongoDB) and run the same Python commands.

---

## Environment variables reference

### Root `.env` (used by Docker Compose)

| Variable          | Description                    | Example |
|-------------------|--------------------------------|---------|
| `MONGODB_URL`     | MongoDB connection string      | `mongodb+srv://...` or `mongodb://localhost:27017` |
| `MONGODB_DB_NAME` | Database name                  | `hrms_lite` |
| `SECRET_KEY`      | Backend secret (≥32 chars)      | Required in production |
| `ALLOWED_ORIGINS` | CORS origins (comma-separated) | `http://localhost:5173` or `https://your-domain.com` |
| `FRONTEND_PORT`   | Port for frontend container    | `80` or `3002` |

### Backend (local dev: `backend/.env`)

Same as above; can add:

- `ENVIRONMENT=development`
- `DEBUG=true`
- `HOST=0.0.0.0`
- `PORT=8000`

### Frontend (local dev: `frontend/.env`)

| Variable             | Description              | Example |
|----------------------|--------------------------|---------|
| `VITE_API_BASE_URL`  | Backend API base URL     | `http://localhost:8000` |
| `VITE_API_TIMEOUT`   | Request timeout (ms)     | `30000` |

Leave `VITE_API_BASE_URL` empty when using Docker and nginx proxy (frontend uses relative `/api`).

---

## Troubleshooting

### Backend won’t start: MongoDB connection failed

- Check `MONGODB_URL` (no typos, correct user/password, IP allowlist on Atlas).
- For local MongoDB: ensure `mongod` is running and reachable at the URL.

### Frontend: “Network Error” or CORS

- **Local dev**: Set `VITE_API_BASE_URL=http://localhost:8000` and ensure backend is running. Add `http://localhost:5173` to backend `ALLOWED_ORIGINS`.
- **Docker**: Frontend should call `/api` (same origin); ensure nginx proxies `/api/` to backend. Add your browser origin to `ALLOWED_ORIGINS` if you use a different port/domain.

### Docker: frontend container exits or 502

- Backend must be healthy first (`depends_on: backend, condition: service_healthy`). Check backend logs: `docker compose logs backend`.
- Ensure `FRONTEND_PORT` is not already in use.

### Seed scripts fail

- Use same `MONGODB_URL` and `MONGODB_DB_NAME` as the running app.
- Run `seed_employees.py` before `seed_dummy_attendance.py` (attendance references employees).

---

## Next steps

- **Deploy to a server**: see [DEPLOYMENT.md](DEPLOYMENT.md).
- **API details**: run backend and open http://localhost:8000/docs (or proxied `/api` docs if configured).
