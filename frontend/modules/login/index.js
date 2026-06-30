export function renderLogin(app) {
  app.innerHTML = `
    <div class="login-container">
      <div class="login-card">
        <h2>DVR System Login</h2>
        <p class="subtitle">Face Recognition Attendance</p>

        <input id="username" placeholder="Username" />
        <input id="password" type="password" placeholder="Password" />

        <button onclick="login()">Login</button>

        <p id="error-msg"></p>
      </div>
    </div>
  `;

  window.login = function () {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const error = document.getElementById("error-msg");

    if (username === "admin" && password === "admin") {
      localStorage.setItem("isLoggedIn", "true");
      localStorage.setItem("user", username);

      navigate("dashboard");
    } else {
      error.innerText = "Invalid credentials";
    }
  };

  document.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      login();
    }
  });
}