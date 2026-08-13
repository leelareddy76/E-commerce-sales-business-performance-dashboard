## E‑commerce Sales & Business Performance Analytics

This repository contains a small analytics scaffold for exploring e‑commerce sales and business performance metrics with a Streamlit frontend and FastAPI backend.

Core files

- `src/analytics.py` — load data and compute KPIs
- `app/backend.py` — FastAPI backend serving precomputed JSON caches
- `app/streamlit_app.py` — Streamlit frontend UI (can call backend)
- `scripts/precompute.py` — generate `cache/` JSON and `data_parquet/` for fast responses
- `scripts/run_local.ps1` — helper to precompute and launch backend + Streamlit on Windows
- `scripts/integration_smoke.py` — simple integration smoke test for endpoints + UI
- `tests/test_analytics.py` — unit tests for analytics functions
- `Dockerfile`, `docker-compose.yml` — containerization
- `.github/workflows/python-tests.yml` — unit-test CI workflow
- `.github/workflows/integration-smoke-test.yml` — integration smoke-test CI workflow

Quick start (Windows PowerShell)

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2. Precompute caches (writes `cache/` and `data_parquet/`):

```powershell
& '.\.venv\Scripts\python.exe' scripts\precompute.py
```

3. Run locally (open two terminals):

Backend (terminal A):
```powershell
& '.\.venv\Scripts\python.exe' -m uvicorn app.backend:app --reload --reload-dir app --reload-dir scripts
```

Streamlit UI (terminal B):
```powershell
& '.\.venv\Scripts\python.exe' -m streamlit run app/streamlit_app.py --server.port 8501 --server.address 127.0.0.1
```

4. Run tests:

```powershell
& '.\.venv\Scripts\python.exe' -m pytest -q
```

5. Run the integration smoke test (after starting services or using the helper):

```powershell
& '.\.venv\Scripts\python.exe' scripts\integration_smoke.py
```

Helper

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\run_local.ps1
```

Docker (optional)

```powershell
docker build -t ecommerce-backend .
docker-compose up --build
```

CI

- Unit tests: `.github/workflows/python-tests.yml` (runs `pytest`).
- Integration smoke test: `.github/workflows/integration-smoke-test.yml` (runs precompute, starts backend + Streamlit, runs `scripts/integration_smoke.py`).

Notes

- If using OneDrive, consider moving the virtual environment out of the workspace to avoid file-watch noise on Windows.
- If `docker compose` isn't available, install Docker Desktop or use the appropriate Docker Compose command for your environment.

If you want me to push these changes to GitHub (requires remote & credentials) or add CI caching/matrix, tell me which next step to take.

Production deployment
---------------------

This project can be deployed on a single Linux VM using Docker Compose and Nginx as a reverse proxy. The repository includes a production compose file `docker-compose.prod.yml`, an example Nginx config at `docker/nginx/default.conf`, and a `deploy/` folder with `systemd` unit and timer examples.

Important environment files

- Use `.env.example` as a starting point and create a real `.env` on the VM (or use Docker secrets/vault).

Basic bring-up (on the VM)

1. Copy code to the VM and create a `.env` file (edit paths as needed):

```bash
scp -r . user@vm:/srv/ecommerce
ssh user@vm
cd /srv/ecommerce
cp .env.example .env
# edit .env to set DATA_DIR and CACHE_DIR to persistent locations
```

2. Build and start the production stack:

```bash
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

3. Verify services:

```bash
docker compose -f docker-compose.prod.yml ps
curl -sS http://localhost/api/kpis
curl -sS http://localhost/  # Streamlit proxied at root
```

Nginx & TLS (Let's Encrypt)

The provided `docker/nginx/default.conf` proxies `/api/` to the backend and `/` to Streamlit. For TLS in production, use `certbot` on the host or run the `certbot` container and mount certificates into the Nginx container. A quick example using Certbot (on the VM):

```bash
sudo apt update && sudo apt install -y certbot
sudo certbot certonly --nginx -d your.domain.example
# configure nginx to point to /etc/letsencrypt/live/your.domain.example/fullchain.pem and privkey.pem
sudo systemctl reload nginx
```

Alternatively, use the `certbot/certbot` Docker image and bind-mount `/etc/letsencrypt` into the nginx service.

systemd unit examples

Two examples are included in `deploy/`:

- `deploy/ecommerce.service` — simple one-shot to bring up the Docker Compose stack on boot (edit `WorkingDirectory` and `docker-compose` paths).
- `deploy/precompute.service` + `deploy/precompute.timer` — run the `scripts/precompute.py` inside the `backend` container on a schedule (timer uses `OnCalendar=daily`).

Prometheus scraping

The FastAPI backend exposes metrics via `prometheus-fastapi-instrumentator` at `/metrics` (instrumentation is enabled if package is installed). When Nginx proxies `/api/` to the backend, metrics are available at `http(s)://<host>/api/metrics`.

Example `prometheus.yml` scrape config snippet:

```yaml
scrape_configs:
	- job_name: 'ecommerce-backend'
		static_configs:
			- targets: ['your.vm.host:80']
		metrics_path: /api/metrics
```

Secrets and `.env` guidance

- Keep secrets out of the repository. Use `/etc/environment`, Docker secrets, or a secret manager.
- Example env variables are in `.env.example`.
- For docker-compose secrets, see Docker docs; for Vault integration, inject secrets at container startup.

Scheduled precompute

Two options are provided:
- `deploy/precompute.timer` + `deploy/precompute.service` — runs the precompute inside a container on the VM.
- GitHub Actions scheduled job — `.github/workflows/scheduled-precompute.yml` will run `scripts/precompute.py` daily and upload the `cache/` as an artifact (good for CI-based pipelines).

Healthchecks & verification

- Backend KPIs: `curl http://localhost/api/kpis`
- Metrics: `curl http://localhost/api/metrics` (Prometheus format)
- Streamlit UI: visit `http://<host>/` proxied by Nginx

Rollback and updates

- To update the stack, pull the new code on the VM, rebuild, and restart:

```bash
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build
```

Questions or next steps

If you want, I can:

- Add a small Nginx configuration that performs HTTP -> HTTPS redirect and includes recommended security headers.
- Add Docker Compose labels for healthchecks and a tiny `watchdog` container to restart failing services.
- Create a `Makefile` with common deploy commands.

Tell me which of the above you'd like me to implement next.
