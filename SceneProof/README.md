# SceneProof

SceneProof turns policy documents and SOPs into structured training videos: extraction, scene planning, storyboards, narration, optional presenter avatars, validation against source text, and an assembly-ready media manifest.

Built for the **Beta University Seed Agents Challenge**. Media and reasoning are wired through **Seed 2.0**, **Seedream 5.0**, **Seedance 2.0**, **Seed Speech**, and **OmniHuman** with **mock-safe providers** so the product runs end-to-end locally without API keys.

## Architecture

- `frontend/` — React + Vite + TypeScript SPA (upload, review, output dashboards).
- `backend/` — FastAPI + Pydantic + async job orchestration + local JSON/file storage under `DATA_DIR`.
- Providers under `backend/app/providers/` encapsulate each vendor; missing credentials automatically fall back to deterministic demo payloads (no crashes).

## Quick start

### Prerequisites

- Python 3.11+
- Node.js 20+

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example .env   # optional: fill keys later; also works if .env lives at repo root
python -m uvicorn app.main:app --reload --port 8000
```

Settings load **both** `SceneProof/.env` and `backend/.env` (backend wins on duplicate keys), so you can keep secrets at repo root or next to the API.

If `uvicorn` is not found, always use `python -m uvicorn` as shown above.

Health check: `http://127.0.0.1:8000/api/health`

### One-shot dev (Windows)

From the repo root:

```powershell
.\scripts\dev.ps1
```

This opens a second terminal for the API and runs the Vite dev server in the current window.

Uploaded assets and job JSON are written to `backend/data/` (override with `DATA_DIR`).

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies `/api` and `/media` to the backend.

### Hackathon deploy (what judges open)

Use **one public URL** for the app (the frontend). The UI talks to the API using `VITE_API_BASE_URL` (see `frontend/src/lib/apiBase.ts`). **Vercel + Render** is the simplest split:

| Piece | Platform | Why |
| --- | --- | --- |
| **Frontend** | [Vercel](https://vercel.com) | Native Vite/React hosting, free tier, fast CDN. |
| **Backend** | [Render](https://render.com) | Long-lived Python process, file uploads, background jobs (free tier sleeps after ~15 min — first request can take ~30s). |

**1. Push the repo to GitHub** (judges and deploy hooks need a remote).

**2. Deploy the API on Render**

- **New → Web Service**, connect the repo.
- **Root directory:** `backend`
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health check path:** `/api/health`
- **Environment → Environment variables:**
  - `CORS_ORIGINS` = your Vercel URL once you have it (e.g. `https://sceneproof.vercel.app`). You can add `http://localhost:5173` too, comma-separated.
  - Optional: copy keys from `.env.example` for live providers.

Copy the service URL (e.g. `https://sceneproof-api.onrender.com`).

**Optional:** **New → Blueprint** and point Render at this repo’s `render.yaml` (defines the same API service; you still set `CORS_ORIGINS` in the dashboard).

**3. Deploy the frontend on Vercel**

- **Add New → Project**, import the same repo.
- **Root Directory:** `frontend`
- **Framework preset:** Vite (auto).
- **Environment variables → Production:**
  - `VITE_API_BASE_URL` = your Render API URL **with no trailing slash** (e.g. `https://sceneproof-api.onrender.com`).

Redeploy the frontend after changing env vars (Vite bakes `VITE_*` at build time).

**4. Finish CORS**

If the UI loads but API calls fail with CORS errors, update Render’s `CORS_ORIGINS` to exactly your Vercel origin (scheme + host, no path), save, and let Render redeploy.

**What you submit:** the **Vercel production URL** (and optionally the Render API URL + GitHub repo in the form).

**All on Render instead:** you can add a second Render **Static Site** pointed at `frontend` with build `npm install && npm run build` and publish directory `dist`, setting `VITE_API_BASE_URL` in that service’s environment before build — same idea as Vercel.

### Production-ish frontend build

```powershell
cd frontend
npm run build
npm run preview
```

## API

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/health` | Liveness + provider configuration flags |
| `POST` | `/api/jobs` | Multipart job creation (`raw_text`, optional `document`, optional `presenter_image`, `audience`, `language`, `style_preset`) |
| `GET` | `/api/jobs/{job_id}` | Job status, progress, partial outputs |
| `POST` | `/api/jobs/{job_id}/review` | Runs ingestion → Seed 2.0 extraction → Seed 2.0 planning |
| `POST` | `/api/jobs/{job_id}/generate` | Runs Seedream, Seed Speech, Seedance, optional OmniHuman, validation, assembly |
| `GET` | `/api/jobs/{job_id}/result` | Final `GenerationResult` (409 until `completed`) |
| `POST` | `/api/jobs/{job_id}/regenerate-scene/{scene_id}` | Placeholder hook for per-scene refresh |

## GitHub repository

Initialize and publish (requires [GitHub CLI](https://cli.github.com/)):

```powershell
cd SceneProof
git init
git add .
git commit -m "Initial SceneProof full-stack implementation"
gh repo create SceneProof --private --source . --remote origin --push
```

Without `gh`, create an empty repository in the GitHub UI, then:

```powershell
git remote add origin https://github.com/<you>/SceneProof.git
git push -u origin main
```

## Notes for judges / investors

- **Demo mode** is the default whenever keys and base URLs are absent; providers still return normalized structures your UI can render.
- **Assembly** currently emits a JSON program manifest plus typed `MediaAsset` metadata; binary muxing can plug into the same `AssemblyService` interface without changing API contracts.
- **Security**: never commit `.env`; use `.env.example` as the single source of variable names.

## License

Hackathon / demonstration use unless otherwise specified.
