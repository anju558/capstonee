const API_BASE = "http://127.0.0.1:8000/api";

let userChart = null;
let adminChart = null;

/* ================================
   TOKEN HELPERS
================================ */

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

/* ================================
   SCORE → LEVEL
================================ */

function convertToLevel(score) {
  score = Number(score) || 0;
  if (score >= 75) return "High";
  if (score >= 40) return "Medium";
  return "Low";
}

/* ================================
   AUTO LOAD DASHBOARD
================================ */

if (window.location.pathname === "/dashboard") {
  loadDashboard();
}

async function loadDashboard() {

  const token = getToken();
  if (!token) {
    window.location.href = "/login";
    return;
  }

  const payload = JSON.parse(atob(token.split(".")[1]));

  // Show user in navbar
  const userDisplay = payload.email || payload.sub || "";
  document.getElementById("navUser").innerText = ` | ${userDisplay}`;

  if (payload.role === "admin") {
    loadAdminDashboard(token);
  } else {
    loadUserDashboard(token);
  }
}

/* ================================
   USER DASHBOARD
================================ */

async function loadUserDashboard(token) {

  document.getElementById("userSection").style.display = "block";

  const res = await fetch(`${API_BASE}/analytics/skills`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const data = await res.json();
  const skills = data.skills || [];

  const tableBody = document.getElementById("userSkillsTable");
  tableBody.innerHTML = "";

  skills.forEach(skill => {
    const row = document.createElement("tr");

    const tech = document.createElement("td");
    tech.textContent = skill.skill || "-";

    const level = document.createElement("td");
    level.textContent = convertToLevel(skill.confidence_score);

    row.appendChild(tech);
    row.appendChild(level);
    tableBody.appendChild(row);
  });

  loadUserHistoryGraph(token);
}

async function loadUserHistoryGraph(token) {

  const res = await fetch(`${API_BASE}/analytics/skills/history`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const history = await res.json();
  if (!Array.isArray(history) || history.length === 0) return;

  // Sort by date
  history.sort((a, b) =>
    new Date(a.created_at) - new Date(b.created_at)
  );

  // Show only last 10 records
  const recent = history.slice(-10);

  const labels = recent.map(h =>
    new Date(h.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  );

  const scores = recent.map(h =>
    Number(h.confidence_score) || 0
  );

  if (userChart) userChart.destroy();

  userChart = new Chart(document.getElementById("skillChart"), {
    type: "line",
    data: {
      labels,
      datasets: [{
        data: scores,
        borderColor: "#2563eb",
        backgroundColor: "rgba(37,99,235,0.1)",
        tension: 0.4,
        pointRadius: 4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 6
          }
        },
        y: {
          min: 0,
          max: 100,
          ticks: { stepSize: 20 },
          grid: { color: "rgba(0,0,0,0.05)" }
        }
      }
    }
  });
}
/* ================================
   ADMIN DASHBOARD
================================ */

async function loadAdminDashboard(token) {

  document.getElementById("adminSection").style.display = "block";

  const res = await fetch(`${API_BASE}/auth/admin/users`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const users = await res.json();
  const tableBody = document.getElementById("adminUsersTableBody");
  tableBody.innerHTML = "";

  users.forEach(u => {
    tableBody.innerHTML += `
      <tr onclick="loadUserDetails('${u.id}', '${u.username}')">
        <td>${u.username}</td>
        <td>${u.email}</td>
        <td>${u.role}</td>
        <td>${new Date(u.created_at).toLocaleDateString()}</td>
      </tr>
    `;
  });
}

async function loadUserDetails(userId, username) {

  const token = getToken();
  document.getElementById("adminUserDetails").style.display = "block";
  document.getElementById("selectedUserTitle").innerText =
    `Skill Profile: ${username}`;

  const res = await fetch(`${API_BASE}/analytics/admin/${userId}`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const data = await res.json();
  const skills = data.skills || [];

  const tableBody = document.getElementById("adminSkillsTable");
  tableBody.innerHTML = "";

  skills.forEach(skill => {
    tableBody.innerHTML += `
      <tr>
        <td>${skill.skill}</td>
        <td>${convertToLevel(skill.confidence_score)}</td>
      </tr>
    `;
  });
}