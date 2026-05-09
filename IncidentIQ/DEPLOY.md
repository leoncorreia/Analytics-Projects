# Deploy IncidentIQ

## 1. GitHub

From the **portfolio** repo root (parent of `IncidentIQ/`):

```bash
git add IncidentIQ
git commit -m "Add IncidentIQ: backend, frontend, HydraDB integration"
git push origin main
```

- `backend/.env` and `frontend/.env.local` are ignored — do not commit secrets.
- `FailureForge/` stays untracked unless you choose to add it in a separate commit.

## 2. Render — API (FastAPI)

1. [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint** (or **Web Service**).
2. Connect your **GitHub** repo and select the branch (e.g. `main`).
3. **Blueprint path:** `IncidentIQ/backend/render.yaml`  
   - If you use **Web Service** instead: set **Root Directory** to `IncidentIQ/backend`, **Build** `pip install -r requirements.txt`, **Start** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
4. After the first deploy, open the service → **Environment** and set:
   - **ALLOWED_ORIGINS** — your real frontend origin(s), comma-separated, e.g. `https://your-app.vercel.app,https://your-app.pages.dev` (include `https://`; no trailing slashes).
   - **PIPESHIFT_API_KEY**, **PIPESHIFT_API_URL**, **PIPESHIFT_MODEL** (optional; analysis falls back without key).
   - **HYDRADB_API_KEY**, **HYDRADB_TENANT_ID** (optional; **HYDRADB_BASE_URL** defaults to `https://api.hydradb.com` in `render.yaml`).
5. Note the service URL, e.g. `https://incidentiq-backend.onrender.com`.

**Health check:** `GET /health`

Free web services **sleep** when idle; the first request after sleep can take ~30–60s.

## 3. Frontend (Vite)

Host the app on **Vercel**, **Cloudflare Pages**, **Netlify**, or another static/SSR host for `IncidentIQ/frontend`.

**Build (typical):**

- Install: `npm ci`
- Build: `npm run build`
- Output: follow your host’s docs for Vite / TanStack Start (often `dist/client` or the path your `vite.config` emits).

**Environment variable at build time:**

- `VITE_API_URL` = `https://<your-render-service>.onrender.com` (no trailing slash)

Then redeploy the frontend so API calls hit Render.

## 4. Smoke test

- Open the deployed frontend → console route.
- Confirm browser network calls go to your Render URL (not `localhost:10000`).
- `GET https://<render-host>/health` should return JSON `{"status":"ok",...}`.
