import { loadCSS } from "../../utils/loadCSS.js";

export function renderEmployee(app) {
    loadCSS("employee-css", "./modules/employee/index.css");


    const user = localStorage.getItem("user") || "Admin";

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

            <div class="employee-wrapper">
            <div class="employee-card">

                <h2>Employee Management 👨‍💼</h2>
                <p><b>Logged in as:</b> ${user}</p>

                <hr/>

                <!-- ADD EMPLOYEE -->
                <div class="form">
                <input id="name" placeholder="Name"/>
                <input id="emp_id" placeholder="Employee ID"/>
                <button onclick="addEmployee()">Add Employee</button>
                </div>

                <br><br>

                <!-- TABLE -->
                <div class="table-container">
                <table class="employee-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Employee ID</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="employeeTable"></tbody>
                </table>
            </div>
            </div>
        </div>
        </div>
        </div>
    </div>
    `;

    loadEmployees();
}


window.loadEmployees = async function () {
    try {
        const res = await fetch("http://127.0.0.1:5000/get_employees");
        const data = await res.json();

        const table = document.getElementById("employeeTable");
        table.innerHTML = "";

        data.forEach(emp => {
            table.innerHTML += `
                <tr>
                    <td>${emp.name}</td>
                    <td>${emp.emp_id}</td>
                    <td>
                        <button class="capture-btn" onclick="captureFace('${emp.emp_id}')">Capture</button>
                        <button class="delete" onclick="deleteEmployee('${emp.emp_id}')">Delete</button>
                    </td>
                </tr>
            `;
        });

    } catch (err) {
        console.error("Load error:", err);
    }
};


window.addEmployee = async function () {
    const name = document.getElementById("name").value;
    const emp_id = document.getElementById("emp_id").value;

    if (!name || !emp_id) {
        alert("Enter all fields");
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:5000/add_employee", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ name, emp_id })
        });

        const data = await res.json();

        alert("Employee added ✅");
        loadEmployees();

    } catch (err) {
        console.error(err);
        alert("Error adding employee");
    }
};

window.deleteEmployee = async function (emp_id) {

    if (!confirm("Are you sure to delete?")) return;

    try {
        const res = await fetch(`http://127.0.0.1:5000/delete_employee/${emp_id}`, {
            method: "DELETE"
        });

        const data = await res.json();

        if (res.ok) {
            alert("Deleted successfully ✅");

            loadEmployees();
        } else {
            alert("Delete failed ");
        }

    } catch (err) {
        console.error(err);
        alert("Server error");
    }
};

window.captureFace = async function(emp_id) {

    alert("Opening camera... Press SPACE to capture, ESC to exit");

    try {
        await fetch(`http://127.0.0.1:5000/capture_face/${emp_id}`);
    } catch (err) {
        console.error(err);
        alert("Camera error");
    }
};