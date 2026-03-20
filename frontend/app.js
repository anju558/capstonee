const API_BASE = "http://127.0.0.1:8000/api";
let userChart = null;

/* ================= TOKEN ================= */

function saveToken(token) {
  localStorage.setItem("token", token);
}

function getToken() {
  return localStorage.getItem("token");
}

function logout() {
  localStorage.removeItem("token");
  window.location.href = "/";
}

/* ================= LOGIN ================= */

if (window.location.pathname.includes("login")) {

  const loginForm = document.getElementById("loginForm");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const email = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value;

      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);
      formData.append("grant_type", "password");

      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString()
      });

      const data = await res.json();

      if (res.ok) {
        saveToken(data.access_token);
        window.location.href = "/dashboard";
      } else {
        document.getElementById("message").innerText =
          data.detail || "Login failed";
      }
    });
  }
}

/* ================= DASHBOARD ================= */

if (window.location.pathname.includes("dashboard")) {
  loadDashboard();
}

async function loadDashboard() {

  const token = getToken();
  if (!token) {
    window.location.href = "/login";
    return;
  }

  document.getElementById("userSection").style.display = "block";

  const payload = JSON.parse(atob(token.split(".")[1]));
  document.getElementById("navUser").innerText = ` | ${payload.sub}`;

  try {

    /* ================= TABLE DATA ================= */

    const skillRes = await fetch(`${API_BASE}/analytics/skills`, {
      headers: { Authorization: `Bearer ${token}` }
    });

    const skillData = await skillRes.json();
    const skills = skillData.skills || skillData || [];

    const tableBody = document.getElementById("userSkillsTable");
    tableBody.innerHTML = "";

    skills.forEach(skill => {
      tableBody.innerHTML += `
        <tr>
          <td>${skill.skill}</td>
          <td>${convertToLevel(skill.confidence_score)}</td>
        </tr>
      `;
    });

    /* ================= HISTORY DATA (CLEAN TREND) ================= */

    const historyRes = await fetch(`${API_BASE}/analytics/skills/history`, {
      headers: { Authorization: `Bearer ${token}` }
    });

    const history = await historyRes.json();

    if (!history || history.length === 0) return;

    // Sort by date (just to be safe)
    history.sort((a, b) =>
      new Date(a.created_at) - new Date(b.created_at)
    );

    const labels = history.map(h => {
      const d = new Date(h.created_at);
      return d.toLocaleDateString();
    });

    const values = history.map(h =>
      Number(h.confidence_score)
    );

    const ctx = document.getElementById("skillChart");

    if (userChart) userChart.destroy();

    userChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [{
          label: "Overall Skill Growth",
          data: values,
          borderWidth: 3,
          tension: 0.4,
          pointRadius: 6,
          pointHoverRadius: 8,
          fill: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: function(context) {
                return "Score: " + context.raw;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            ticks: {
              stepSize: 10
            }
          }
        }
      }
    });

  } catch (err) {
    console.error(err);
    logout();
  }
}

/* ================= LEVEL CONVERTER ================= */

function convertToLevel(score) {
  score = Number(score) || 0;
  if (score >= 75) return "High";
  if (score >= 40) return "Medium";
  return "Low";
}