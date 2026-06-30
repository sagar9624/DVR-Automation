import { loadCSS } from "../../utils/loadCSS.js";

export function renderDashboard(app) {
  loadCSS("dashboard-css", "./modules/dashboard/index.css");

  const user = localStorage.getItem("user") || "Admin";

  app.innerHTML = `
    <div class="layout">

      <!-- Sidebar -->
      <div class="sidebar">
        <h2>DVR System</h2>
        <hr/>

        <p style="cursor:pointer;" onclick="navigate('dashboard')">Dashboard</p>
        <p style="cursor:pointer;" onclick="navigate('employee')">Employee</p>
        <p style="cursor:pointer;" onclick="navigate('camera')">Camera</p>
        <p style="cursor:pointer;" onclick="navigate('attendance')">Attendance</p>
        <p style="cursor:pointer;" onclick="navigate('reports')">Reports</p>

        <p onclick="logout()" class="logout">Logout</p>
      </div>

      <!-- Main Content -->
      <div class="main">
        <div class="dashboard-card">

          <h1>Welcome to Dashboard</h1>
          <p>DVR Face Recognition System is running.</p>

          <hr/>

          <h3>User Info</h3>
          <p><b>Logged in as:</b> ${user}</p>

          <hr/>

          <h3>Quick Overview</h3>
          <ul id="dashboard-data">
            <li>Loading data...</li>
          </ul>

          <hr/>

          <h3>Analytics 📊</h3>
          <div class="chart-container">
          <canvas id="dashboardChart" height="100"></canvas>
          <div>

        </div>
      </div>

    </div>
  `;


  loadDashboardData();
}


async function loadDashboardData() {
  try {
    const res = await fetch("http://127.0.0.1:5000/dashboard");
    const data = await res.json();

    const list = document.getElementById("dashboard-data");

    list.innerHTML = `
      <li>👨‍💼 Employees: <b>${data.employees}</b></li>
      <li>📷 Camera: <b>${data.camera}</b></li>
      <li>🕒 Attendance Records: <b>${data.attendance}</b></li>
      <li>📊 Reports: <b>${data.reports}</b></li>
    `;


    renderChart(data);

  } catch (error) {
    console.error("Dashboard Error:", error);

    document.getElementById("dashboard-data").innerHTML =
      `<li style="color:red;">❌ Error loading dashboard data</li>`;
  }
}

function renderChart(data) {
  const ctx = document.getElementById("dashboardChart");

  if (!ctx) {
    console.error("Canvas not found ❌");
    return;
  }

  if (window.dashboardChartInstance) {
    window.dashboardChartInstance.destroy();
  }

  window.dashboardChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Employees", "Attendance", "Reports"],
      datasets: [{
        label: "System Data",
        data: [
          data.employees,
          data.attendance,
          data.reports
        ],
        backgroundColor: [
          "#3498db",
          "#2ecc71",
          "#e67e22"
        ]
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: false
        }
      }
    }
  });
}