# Habit Tracker 
A production-ready full-stack habit tracker. **Phase 5** takes Phase 4's
finished app to production: Alembic migrations replace ad-hoc table
creation, the backend deploys to Render on managed PostgreSQL, and the
frontend deploys to Vercel as a static site.

## What's included overall

- FastAPI backend with clean architecture: `routers/`, `models/`, `schemas/`, `services/`, `database/`, `utils/`
- SQLAlchemy models: `User`, `Habit`, `HabitLog`, `UserAchievement`, versioned with Alembic migrations
- JWT auth: register, login, `/auth/me`
- Habit CRUD with a curated category/icon/color picker (`GET /habits/options`)
- Completion toggling with streak calculation
- Dashboard endpoint (today's habits, streaks, completion %)
- Analytics endpoints (daily completions, category breakdown, per-habit rates, calendar heatmap)
- Achievements engine (catalog, progress tracking, auto-unlock on completion)
- Profile endpoints (get/update, change password, stats)
- Dockerfile + docker-compose for local dev, `render.yaml` for production
- **Complete frontend**: landing page, auth, dashboard, habits, analytics, achievements, profile — all vanilla HTML/CSS/JS, no build step

## Running locally

```bash
cd backend
pip install -r requirements.txt
cp ../.env.example .env   # defaults (SQLite) work out of the box
uvicorn main:app --reload
```

API docs: http://localhost:8000/docs

Then serve the frontend (any static server works, e.g.):

```bash
cd frontend
python -m http.server 5500
```

## Deploying

**Order matters**: deploy the backend first so you have its URL, then the
frontend, then circle back to set the backend's `CORS_ORIGINS` to the
frontend's real domain.

### 1. Backend → Render

1. Push this repo to GitHub/GitLab.
2. In the Render dashboard: **New → Blueprint**, point it at the repo. Render
   reads `render.yaml` and provisions the web service + a managed Postgres
   database together, wiring `DATABASE_URL` and generating `SECRET_KEY`
   automatically.
3. First deploy runs `alembic upgrade head` as a pre-deploy step, then
   starts the API. Note the resulting URL, e.g.
   `https://habit-tracker-backend.onrender.com`.
4. Leave `CORS_ORIGINS` as-is for now — you'll update it in step 3.

If you'd rather not use the Blueprint, create the web service manually
(Docker runtime, root `backend/`) and a Postgres database, then set
`DATABASE_URL`, `SECRET_KEY`, `ENV=production`, and `CORS_ORIGINS` as
environment variables yourself.

### 2. Frontend → Vercel

1. Edit `frontend/js/config.js` — set `PROD_API_BASE_URL` to your Render
   backend URL from step 1.
2. In the Vercel dashboard: **New Project**, point it at the repo, set the
   **root directory** to `frontend`. No build command needed (static site).
3. Deploy. Note the resulting URL, e.g. `https://your-app.vercel.app`.

### 3. Connect them

Back in Render, update the backend's `CORS_ORIGINS` environment variable to
your Vercel domain from step 2 (comma-separated if you have multiple, e.g.
a preview and a production domain), then redeploy the backend so the CORS
change takes effect.


| POST | /achievements/evaluate | Re-check and unlock any newly-earned achievements |

## Possible next steps

- CI (GitHub Actions) running `alembic upgrade head --sql` as a dry-run check and the test suite on PRs
- Custom domain + HTTPS on both Render and Vercel
- Rate limiting on `/auth/login` and `/auth/register`
