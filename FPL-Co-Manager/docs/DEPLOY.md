# Production deploy — URL for judges

Judges only need **one public URL**: the **Vercel frontend** (e.g. `https://fpl-co-manager.vercel.app`).  
The **FastAPI** API runs separately (e.g. Render) because of long requests, SQLite, and secrets.

---

## A. Deploy the API (Render)

### Option 1 — Blueprint (fast)

1. Push this repository to GitHub.
2. [Render](https://render.com) → **New** → **Blueprint** → select the repo.
3. Render reads **`render.yaml`** at the **repository root** (`Analytics-Projects/render.yaml`) and creates the `fpl-comanager-api` web service with root directory `FPL-Co-Manager/backend`.
4. In the Render dashboard → **Environment** for that service, add **all** secrets (copy names from `backend/.env.example`, values from your local `backend/.env`):
   - Required for analyze: `GMI_API_KEY`, `GMI_BASE_URL`, `KIMI_MODEL`, `KIMI_VISION_MODEL`
   - Optional: `DIFY_*`, `HYDRADB_*`
5. Set **CORS** after you know your Vercel URL (step B), then **Manual Deploy** → **Clear build cache & deploy** if CORS was wrong.

### Option 2 — Manual Web Service

1. **New** → **Web Service** → connect repo.
2. **Root directory:** `FPL-Co-Manager/backend`
3. **Build:** `pip install -r requirements.txt`  
   **Start:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Health check path:** `/health`
5. Same environment variables as above.

### CORS (required for browser → API)

In Render **Environment**, set:

| Variable | Example |
|----------|---------|
| `CORS_ORIGINS` | `https://your-app.vercel.app` (your **production** Vercel URL, no path) |
| `CORS_ORIGIN_REGEX` | `https://.*\.vercel\.app` (optional; allows **preview** deployments `*.vercel.app` without listing each) |

Keep `http://localhost:5173` in `CORS_ORIGINS` only if you still test locally against production API.

Copy the API URL (e.g. `https://fpl-comanager-api.onrender.com`). Check: `GET /` and `GET /health` in a browser.

**Note:** Free Render **spins down** when idle; the first request after sleep can take **~30–60s**. For a live demo, hit `/health` once before presenting.

---

## B. Deploy the frontend (Vercel)

1. [Vercel](https://vercel.com) → **Add New** → **Project** → import the **same** GitHub repo.
2. **Root Directory:** `FPL-Co-Manager/frontend`
3. Framework: **Vite** (auto).
4. **Environment variables** → **Production**:
   - `VITE_API_URL` = your API origin **without** trailing slash, e.g. `https://fpl-comanager-api.onrender.com`
5. **Deploy**.

**Give judges the Vercel URL** (Production domain), e.g. `https://fpl-co-manager.vercel.app`.

After changing `VITE_API_URL`, trigger a **redeploy** so the build picks it up.

---

## C. Final checklist

| Check | How |
|-------|-----|
| API up | Browser: `https://<api>/health` → `{"status":"ok",...}` |
| CORS | Browser devtools: no CORS error when using Analyze from Vercel UI |
| Frontend → API | `VITE_API_URL` matches Render URL exactly (https, no `/` at end) |
| Secrets | Only in Render / Vercel dashboards — never committed |

---

## D. Docker (optional)

`backend/Dockerfile`: build context = `FPL-Co-Manager/backend`, pass the same env vars, bind `$PORT`.
