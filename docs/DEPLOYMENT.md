# HRMS Lite – Self-Deployment Guide

This guide describes how to **self-deploy** HRMS Lite on your own server using Docker Compose, MongoDB Atlas (or self-hosted MongoDB), and optional reverse proxy with SSL.

---

## Overview

- **Backend**: FastAPI in Docker, no direct port exposure to the internet (behind reverse proxy or frontend proxy).
- **Frontend**: Nginx in Docker serving the SPA and proxying `/api/` to the backend.
- **Database**: MongoDB Atlas (recommended) or a MongoDB instance you host.
- **Optional**: Reverse proxy (e.g. Nginx or Caddy) on the host for SSL and single entry point.

---

## Prerequisites

- A **VPS or VM** (e.g. Ubuntu 22.04 LTS) with Docker and Docker Compose.
- A **domain** (optional but recommended for HTTPS).
- **MongoDB Atlas** account (or a reachable MongoDB server).

---

## Step 1: Server preparation

### Install Docker and Docker Compose

On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
# Log out and back in (or newgrp docker)
```

Verify:

```bash
docker --version
docker compose version
```

### Clone the repository

```bash
cd /opt   # or your preferred path
sudo git clone <repository-url> hrms-lite
cd hrms-lite
sudo chown -R $USER:$USER .
```

---

## Step 2: MongoDB (Atlas recommended)

### MongoDB Atlas

1. Create a cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. **Database Access**: Create a user with read/write on the target database.
3. **Network Access**: Add your server’s IP (or `0.0.0.0/0` for testing only; restrict in production).
4. **Connect** → **Drivers** → copy the connection string, e.g.:
   ```text
   mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
   ```
5. Replace `<password>` with the actual password (special chars URL-encoded).

### Self-hosted MongoDB

If you run MongoDB on the same or another server:

- Use a URL like: `mongodb://user:pass@host:27017` or `mongodb+srv://...` for Atlas-style.
- Ensure the HRMS Lite server can reach MongoDB (firewall, security groups).

---

## Step 3: Configure environment

From the project root:

```bash
cp env.example .env
nano .env   # or vim / your editor
```

Set **production** values:

```env
# Required
MONGODB_URL=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=hrms_lite
SECRET_KEY=<at-least-32-character-random-secret-key>
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Optional
ENVIRONMENT=production
FRONTEND_PORT=80
```

- **SECRET_KEY**: Generate a long random string, e.g. `openssl rand -base64 32`.
- **ALLOWED_ORIGINS**: Exact origins that will load the frontend (no trailing slash). Add `http://<server-ip>` only if you need non-HTTPS access.

Do **not** commit `.env`; it should be in `.gitignore`.

---

## Step 4: Build and run with Docker Compose

```bash
cd /opt/hrms-lite
docker compose build --no-cache
docker compose up -d
```

Check:

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
```

- Backend: health at `http://<server-ip>:8000/health` only if you expose port 8000 (see below).
- Frontend: by default `FRONTEND_PORT` is 80; open `http://<server-ip>` (or the port you set).

### Exposing the backend port (optional)

To hit the API directly (e.g. for `/docs` or health checks), in `docker-compose.yml` under `backend` add:

```yaml
ports:
  - "8000:8000"
```

Then:

- API: `http://<server-ip>:8000`
- Docs: `http://<server-ip>:8000/docs`

Otherwise, the API is only reachable via the frontend’s nginx proxy at `http://<server-ip>/api/`.

---

## Step 5: Reverse proxy and SSL (recommended)

Run the app on a high port (e.g. 3002) and put a reverse proxy in front with SSL.

### 1. Use a high port for the app

In `.env`:

```env
FRONTEND_PORT=3002
```

Restart:

```bash
docker compose up -d
```

So the app is only on `http://localhost:3002` from the host.

### 2. Install Nginx (or Caddy) and get SSL

**Option A: Nginx + Certbot**

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

**Option B: Caddy (auto HTTPS)**

```bash
sudo apt install -y debian-keyring debian-archive-keyring curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
sudo systemctl enable --now caddy
```

### 3. Nginx proxy config

Create a server block, e.g. `/etc/nginx/sites-available/hrms-lite`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate     /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:3002;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and reload:

```bash
sudo ln -s /etc/nginx/sites-available/hrms-lite /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Caddy proxy config

Create `/etc/caddy/Caddyfile` (or add a block):

```text
your-domain.com {
    reverse_proxy 127.0.0.1:3002
}
```

Reload Caddy:

```bash
sudo systemctl reload caddy
```

Now open `https://your-domain.com`. The SPA and `/api/` are served through the proxy.

---

## Step 6: Post-deploy checks

1. **Frontend**: Open `https://your-domain.com` (or `http://<server>:FRONTEND_PORT`). Dashboard should load.
2. **API via proxy**: Open `https://your-domain.com/api/v1/employees` (or use Swagger if you exposed backend and use the same base URL).
3. **Health**: If backend is exposed, `http://<server>:8000/health` should return `"status": "healthy"` and DB info.

---

## Step 7: Seed data (optional)

From the server, with backend env available:

```bash
cd /opt/hrms-lite/backend
# Use the same .env as compose (copy from project root or export vars)
export $(grep -v '^#' ../.env | xargs)
pip install -r requirements.txt pymongo
python scripts/seed_employees.py
python scripts/seed_dummy_attendance.py
```

Or run inside the backend container:

```bash
docker compose exec backend sh
pip install pymongo
python scripts/seed_employees.py
python scripts/seed_dummy_attendance.py
exit
```

---

## Security checklist

- Use a **strong SECRET_KEY** (≥32 chars, random).
- Set **ALLOWED_ORIGINS** to the exact frontend origin(s) (HTTPS in production).
- Prefer **MongoDB Atlas** with IP allowlist and strong DB user password.
- Do **not** expose backend port 8000 to the internet unless needed; keep it behind proxy or internal.
- Use **HTTPS** (Certbot/Caddy) for the public domain.
- Keep OS and Docker updated: `sudo apt update && sudo apt upgrade -y`.

---

## Updating the application

```bash
cd /opt/hrms-lite
git pull
docker compose build --no-cache
docker compose up -d
```

---

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| 502 Bad Gateway | Backend healthy? `docker compose logs backend`. Proxy points to correct port (e.g. 3002). |
| CORS errors | `ALLOWED_ORIGINS` includes the exact origin (scheme + host + port). |
| MongoDB connection failed | Atlas IP allowlist, correct `MONGODB_URL`, URL-encoded password. |
| Frontend blank / wrong API | With proxy, frontend should use relative `/api` (no `VITE_API_BASE_URL` in production build). Rebuild frontend if you changed env. |

---

## Summary

1. Prepare server: Docker + Docker Compose.
2. MongoDB: Atlas (or self-hosted); get connection string.
3. Copy `env.example` to `.env`, set `MONGODB_URL`, `SECRET_KEY`, `ALLOWED_ORIGINS`, and optionally `FRONTEND_PORT`.
4. Run `docker compose up -d`.
5. Put Nginx/Caddy in front with SSL and proxy to `FRONTEND_PORT`.
6. Optionally seed data and verify health and API.

For local and Docker-only setup, see [SETUP_GUIDE.md](SETUP_GUIDE.md).
