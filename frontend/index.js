
import { renderLogin } from "./modules/login/index.js";
import { renderDashboard } from "./modules/dashboard/index.js";
import { renderEmployee } from "./modules/employee/index.js";
import { renderCamera } from "./modules/camera/index.js";
import { renderAttendance } from "./modules/attendance/index.js";
import { renderReports } from "./modules/reports/index.js";


const app = document.getElementById("app");


function loadPage(page) {
    console.log("Navigating to:", page);

    const isLoggedIn = localStorage.getItem("isLoggedIn");
    const sidebar = document.getElementById("sidebar");


    if (!isLoggedIn && page !== "login") {
        page = "login";
    }


    if (!isLoggedIn || page === "login") {
        if (sidebar) sidebar.style.display = "none";
    } else {
        if (sidebar) sidebar.style.display = "block";
    }


    switch (page) {
        case "login":
            renderLogin(app);
            break;

        case "dashboard":
            renderDashboard(app);
            break;

        case "employee":
            renderEmployee(app);
            break;

        case "camera":
            renderCamera(app);
            break;

        case "attendance":
            renderAttendance(app);
            break;

        case "reports":
            renderReports(app);
            break;

        default:
            renderLogin(app);
    }
}


window.navigate = function (page) {
    loadPage(page);
};


window.logout = function () {
    localStorage.removeItem("isLoggedIn");
    loadPage("login");
};


window.onload = function () {
    console.log("App started");

    const isLoggedIn = localStorage.getItem("isLoggedIn");

    if (isLoggedIn) {
        loadPage("dashboard");
    } else {
        loadPage("login");
    }
};