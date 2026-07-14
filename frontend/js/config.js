// ============================================================================
// Deployment config — the only file you need to edit per-environment.
//
// Local dev: leave PROD_API_BASE_URL as-is; app.js auto-detects localhost
// and ignores this value.
// Production (Vercel): set PROD_API_BASE_URL to your deployed Render
// backend URL, e.g. "https://habit-tracker-backend.onrender.com".
// ============================================================================

window.HABIT_TRACKER_CONFIG = {
  PROD_API_BASE_URL: "habit-tracker-backend-production-9432.up.railway.app",
};
