import { loadCSS } from "../../utils/loadCSS.js";

export async function renderAttendance(app) {
    loadCSS("attendance-css", "./modules/attendance/index.css");


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
        <div class="attendance-wrapper">
        <div class="attendance-card">
            <h2>📊 Attendance Records</h2>
            <div class="table-container">
            <table class="attendance-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Date & Time</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody id="attendance-body">
                    <tr><td colspan="3">Loading...</td></tr>
                </tbody>
            </table>
            </div>
        </div>
    </div>
    </div>
    </div>
    `;

    const tbody = document.getElementById("attendance-body");


    async function loadAttendance() {
        try {

            const res = await fetch("http://127.0.0.1:5000/attendance_full");
            let data = await res.json();

            tbody.innerHTML = "";

            if (!data || data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="3">No attendance records</td></tr>`;
                return;
            }

            data.forEach(item => {
                const row = document.createElement("tr");

                // ✅ FIXED FIELD MAPPING
                const date = item.time ? item.time.split(" ")[0] : "-";
                const login = item.time ? item.time.split(" ")[1] : "-";
                const logout = item.logout_time ? item.logout_time: "-";
                const hours = (item.total_hours !== null && item.total_hours !==undefined)? Number(item.total_hours).toFixed(2):"In Progress";

                row.innerHTML = `
                    <td>${item.name}</td>
                    <td>
                        ${date}<br>
                        Login: ${login}<br>
                        Logout: ${logout}<br>
                        Hours: ${hours}
                    </td>
                    <td>
                        ${!item.logout_time || item.logout_time==="" ? `
                        <button class="logout-btn"
                            style="background:green; color:white; border:none; padding:5px 10px; cursor:pointer;"
                            onclick="logoutUser('${item.name}')"
                        >
                            Logout
                        </button>
                        ` : ""}

                        <button class="delete"
                            style="background:red; color:white; border:none; padding:5px 10px; cursor:pointer;"
                            onclick="deleteAttendance(${item.id})"
                        >
                            Delete
                        </button>
                    </td>
                `;

                tbody.appendChild(row);
            });

        } catch (err) {
            console.error("Error loading attendance:", err);
            tbody.innerHTML = `<tr><td colspan="3">Error loading data</td></tr>`;
        }
    }

    window.logoutUser = async function(name) {
        try {
            const res = await fetch("http://127.0.0.1:5000/logout", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name })
            });

            const result = await res.json();

            if (result.status === "success") {
                alert("✅ Logout marked");
                await loadAttendance();
            } else if (result.status === "no_active_login") {
                alert("⚠️ Already logged out");
            } else {
                alert("⚠️ Logout failed");
            }

        } catch (err) {
            console.error("Logout error:", err);
            alert("❌ Server error");
        }
    };


    window.deleteAttendance = async function(id) {

        const confirmDelete = confirm("⚠️ Are you sure you want to delete this record?");
        if (!confirmDelete) return;

        try {
            const res = await fetch(`http://127.0.0.1:5000/delete_attendance/${id}`, {
                method: "DELETE"
            });

            const result = await res.json();

            if (result.status === "success") {
                alert("✅ Deleted successfully");
                loadAttendance();
            } else {
                alert("❌ Failed to delete");
            }

        } catch (err) {
            console.error("Delete error:", err);
            alert("Server error");
        }
    };

    loadAttendance();
}. 