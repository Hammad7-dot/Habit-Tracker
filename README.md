# Habit Tracker: 
A production-ready full-stack habit tracker.
- **Alembic** (`backend/alembic/`): a real migration history instead of
  `Base.metadata.create_all()`. `0001_initial` mirrors the four existing
  models exactly (`User`, `Habit`, `HabitLog`, `UserAchievement`). Table
  auto-creation in `app/factory.py` now only runs when `ENV != production`
  — in production, schema is owned entirely by migrations, so a failed
  migration can't be silently masked by auto-create.
- **`backend/config.py`**: normalizes Render's legacy `postgres://` URL
  scheme to `postgresql://` (required by SQLAlchemy 2.x) automatically, and
  refuses to start with `ENV=production` if `SECRET_KEY` is still the
  placeholder default.
- **`render.yaml`**: a Render Blueprint that provisions the backend web
  service and a managed Postgres database together, wires `DATABASE_URL`
  and a generated `SECRET_KEY` automatically, and runs
  `alembic upgrade head` as a pre-deploy step on every deploy.
- **`backend/Dockerfile`**: now binds to Render's injected `$PORT` (falls
  back to `8000` for local `docker-compose`).
- **`frontend/js/config.js`**: the one file you edit per environment — sets
  the production API URL. `app.js` reads it instead of hardcoding a
  placeholder, so the shared app code never needs touching for a deploy.
- **`frontend/vercel.json`**: static-hosting config (security headers,
  long-cache immutable headers for `css/`/`js/`).
- **`.gitignore`**: excludes `.env`, the local SQLite file, and `__pycache__`.


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


Open http://localhost:5500. The frontend auto-detects `localhost`/`127.0.0.1`
and points at `http://localhost:8000` — `frontend/js/config.js` is ignored
locally, so there's nothing to edit for local dev.

## Running with Docker

```bash
docker-compose up --build
```

## Database migrations (Alembic)

The schema lives in `backend/alembic/versions/`, not in code that runs on
every startup. Common commands (run from `backend/`):

```bash
# Apply all pending migrations (also runs automatically on Render deploys)
alembic upgrade head

# After changing a model, generate a new migration
alembic revision --autogenerate -m "describe the change"

# Roll back the last migration
alembic downgrade -1
```

`alembic/env.py` reads `DATABASE_URL` from the same `Settings` the app
uses, so it works against SQLite locally and Postgres in production with
no extra config — just make sure your `.env` (or shell environment) is set
before running these commands.


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


## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | /auth/register | Create account, returns JWT |
| POST | /auth/login | Login, returns JWT |
| GET | /auth/me | Current user |
| GET | /habits/options | Valid categories/icons/colors for the picker UI |
| GET | /habits | List habits |
| POST | /habits | Create habit |
| PUT | /habits/{id} | Update habit |
| DELETE | /habits/{id} | Delete habit |
| POST | /complete/{habit_id} | Toggle completion for today (or `?log_date=YYYY-MM-DD`) |
| GET | /dashboard | Today's habits + streaks + completion % |
| GET | /analytics | Daily/category/per-habit stats (`?days=N`) |
| GET | /analytics/heatmap | Calendar heatmap data for a given year (`?year=YYYY`) |
| GET | /profile | Profile |
| PUT | /profile | Update profile |
| POST | /profile/change-password | Change password |
| GET | /profile/stats | Total habits/completions |
| GET | /achievements | Full catalog + this user's progress/unlock status |
<<<<<<< HEAD
=======
=======

>>>>>>> cc30b236afbf34ce26a54add4ee6a06deec9f873
>>>>>>> 67dc7449e9306e1041dd90249aae478f9d1548fc
| POST | /achievements/evaluate | Re-check and unlock any newly-earned achievements |

## Possible next steps

- CI (GitHub Actions) running `alembic upgrade head --sql` as a dry-run check and the test suite on PRs
- Custom domain + HTTPS on both Render and Vercel
- Rate limiting on `/auth/login` and `/auth/register`
