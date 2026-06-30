import { loadCSS } from "../../utils/loadCSS.js";

export async function renderReports(app) {
    loadCSS("reports-css", "./modules/reports/index.css");

    app.innerHTML = `
    <div class="layout">

        <!-- SIDEBAR -->
        <div class="sidebar">
            <h2>DVR System</h2>
            <hr/>

            <p onclick="navigate('dashboard')">Dashboard</p>
            <p onclick="navigate('employee')">Employee</p>
            <p onclick="navigate('camera')">Camera</p>
            <p onclick="navigate('attendance')">Attendance</p>
            <p onclick="navigate('reports')">Reports</p>

            <p onclick="logout()" class="logout">Logout</p>
        </div>

        <!-- MAIN -->
        <div class="main">
            <div class="reports-wrapper">
                <div class="reports-card">
                    <h2>📊 Reports</h2>

                    <p id="total"></p>

                    <div class="table-container">
                        <table class="reports-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Date & Time</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody id="report-body">
                                <tr><td colspan="3">Loading...</td></tr>
                            </tbody>
                        </table>
                    </div>

                </div>
            </div>
        </div>
    </div>
    `;

    const tbody = document.getElementById("report-body");
    const totalText = document.getElementById("total");

  
    async function loadReports() {
        try {
            const res = await fetch("http://127.0.0.1:5000/report_details");
            let data = await res.json();

            tbody.innerHTML = "";

            if (!data || data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="3">No records found</td></tr>`;
                totalText.innerText = "Total Records: 0";
                return;
            }

            totalText.innerText = `Total Records: ${data.length}`;

            data.forEach(item => {
                const row = document.createElement("tr");

                row.innerHTML = `
                <td>${item.name || "-"}</td>
                <td> 
                    <div>Day: ${item.day || "-"}</div>
                    <div>Date: ${item.date || "-"}</div>
                    <div>Login: ${item.login || "-"}</div>
                    <div>Logout: ${item.logout || "-"}</div>
                    <div>Hours: ${item.hours || "0.00"} hrs</div>
                </td>
                <td>
                    <button class="delete" onclick="deleteReport(${item.id})">
                        Delete
                    </button>
                </td>
                `;

                tbody.appendChild(row);
            });

        } catch (err) {
            console.error("Error loading reports:", err);
            tbody.innerHTML = `<tr><td colspan="3">Error loading data</td></tr>`;
        }
    }


    window.deleteReport = async function(id) {
        if (!id) {
            alert("Invalid ID");
            return;
        }

        const confirmDelete = confirm("⚠️ Delete this record?");
        if (!confirmDelete) return;

        try {
            const res = await fetch(`http://127.0.0.1:5000/delete_report/${id}`, {
                method: "DELETE"
            });

            const result = await res.json();

            if (result.status === "success") {
                alert("✅ Deleted successfully");
                loadReports();
            } else {
                alert("Failed to delete");
            }

        } catch (err) {
            console.error("Delete error:", err);
            alert(" Server error");
        }
    };
    loadReports();
}