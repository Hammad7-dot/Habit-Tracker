// ============================================================================
// Profile page — /profile, /profile/stats, /profile/change-password
// ============================================================================

(async function () {
  const user = await initAppPage("profile");
  if (!user) return;

  document.getElementById("username").value = user.username;
  document.getElementById("email").value = user.email;
  document.getElementById("avatar_url").value = user.avatar_url || "";

  loadStats();

  async function loadStats() {
    let stats;
    try {
      stats = await api.get("/profile/stats");
    } catch (err) {
      toast(err.message || "Couldn't load stats.", "error");
      return;
    }
    document.getElementById("profile-stats").innerHTML = `
      <div class="stat-card">
        <i class="fa-solid fa-list-check stat-icon"></i>
        <div class="stat-label">Total habits</div>
        <div class="stat-value">${stats.total_habits}</div>
      </div>
      <div class="stat-card ember">
        <i class="fa-solid fa-fire stat-icon"></i>
        <div class="stat-label">Total completions</div>
        <div class="stat-value">${stats.total_completions}</div>
      </div>
    `;
  }

  // ---- Profile form ----
  const profileForm = document.getElementById("profile-form");
  const profileError = document.getElementById("profile-error");
  const profileBtn = document.getElementById("profile-submit-btn");
  const profileLabel = document.getElementById("profile-submit-label");

  profileForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    setFormError(profileError, "");

    const payload = {
      username: document.getElementById("username").value.trim(),
      avatar_url: document.getElementById("avatar_url").value.trim() || null,
    };

    profileBtn.disabled = true;
    profileLabel.textContent = "Saving…";
    try {
      const updated = await api.put("/profile", payload);
      setCachedUser(updated);
      toast("Profile updated.", "success");
      renderShell("profile", updated);
    } catch (err) {
      setFormError(profileError, err.message || "Couldn't update profile.");
    } finally {
      profileBtn.disabled = false;
      profileLabel.textContent = "Save changes";
    }
  });

  // ---- Password form ----
  const passwordForm = document.getElementById("password-form");
  const passwordError = document.getElementById("password-error");
  const passwordSuccess = document.getElementById("password-success");
  const passwordBtn = document.getElementById("password-submit-btn");
  const passwordLabel = document.getElementById("password-submit-label");

  passwordForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    setFormError(passwordError, "");
    passwordSuccess.style.display = "none";

    const current_password = document.getElementById("current_password").value;
    const new_password = document.getElementById("new_password").value;

    passwordBtn.disabled = true;
    passwordLabel.textContent = "Updating…";
    try {
      await api.post("/profile/change-password", { current_password, new_password });
      passwordSuccess.style.display = "inline-flex";
      passwordForm.reset();
    } catch (err) {
      setFormError(passwordError, err.message || "Couldn't update password.");
    } finally {
      passwordBtn.disabled = false;
      passwordLabel.textContent = "Update password";
    }
  });
})();
