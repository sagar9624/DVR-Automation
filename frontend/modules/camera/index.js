import { loadCSS } from "../../utils/loadCSS.js";
export function renderCamera(app) {
    loadCSS("camera-css", "./modules/camera/index.css");

    const emp_id = localStorage.getItem("capture_emp");

    app.innerHTML = `
    <div class="camera-page">

        <!-- SIDEBAR -->
        <div class="sidebar">
            <h2>DVR System</h2>
            <hr/>

            <p onclick="navigate('dashboard')">Dashboard</p>
            <p onclick="navigate('employee')">Employee</p>
            <p onclick="navigate('camera')">Camera</p>
            <p onclick="navigate('attendance')">Attendance</p>
            <p onclick="navigate('reports')">Reports</p>

            <p class="logout" onclick="logout()">Logout</p>
        </div>

        <!-- MAIN -->
        <div class="main">
        <div class="camera-card">
            <h2>📷 DVR Live Camera</h2>

            <p id="status" class="status-off">Camera: OFF 🔴</p>

            <p id="result" class="result"></p>

            <!-- 🔥 NEW: RTSP + TOGGLE -->
            <div class="rtsp-controls">
                <input id="rtspInput" placeholder="Enter RTSP URL">
                <button id="connectBtn">Connect</button>
                <button id="toggleBtn">Switch Mode</button>
            </div>

            <!-- CAMERA CARD -->
            <div class="camera-box">

                <div id="placeholder" class="placeholder">
                    📷 Camera is OFF <br/>
                    Click Start to begin
                </div>

                <video id="video" width="640" height="480" autoplay class="video"></video>

                <canvas id="canvas" width="640" height="480" class="canvas"></canvas>
            </div>

            <br>

            <button id="start" class="start-btn">▶ Start</button>
            <button id="stop" class="stop-btn">⏹ Stop</button>
        </div>
    </div>
    </div>
    `;

    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");

    const statusText = document.getElementById("status");
    const resultText = document.getElementById("result");
    const placeholder = document.getElementById("placeholder");

    const startBtn = document.getElementById("start");
    const stopBtn = document.getElementById("stop");


    const rtspInput = document.getElementById("rtspInput");
    const connectBtn = document.getElementById("connectBtn");
    const toggleBtn = document.getElementById("toggleBtn");

    let stream = null;
    let running = false;
    let isRTSP = false; 

    let unknownAlertShown = false;

    function triggerUnknownAlert() {
        if (!unknownAlertShown) {
            alert("⚠️ Unknown Person Detected");
            unknownAlertShown = true;
        }
    }

   
    async function startCamera() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;

            running = true;
            unknownAlertShown = false;

            video.style.display = "block";
            placeholder.style.display = "none";

            statusText.innerText = "Camera: ON ✅";
            statusText.className = "status-on";

            detectLoop();

        } catch (err) {
            statusText.innerText = "Camera access denied";
            statusText.className = "status-off";
            console.error(err);
        }
    }

    function stopCamera() {
        running = false;

        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            video.srcObject = null;
            stream = null;
        }

    
        video.src = "";
        fetch("http://127.0.0.1:5000/stop_camera");

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        video.style.display = "none";
        placeholder.style.display = "block";

        statusText.innerText = "Camera: OFF 🔴";
        statusText.className = "status-off";

        resultText.innerText = "";
    }

    function startRTSPCamera() {
        video.srcObject = null;

        video.src = "http://127.0.0.1:5000/video_feed?time=" + new Date().getTime();

        running = true;
        unknownAlertShown = false;

        video.style.display = "block";
        placeholder.style.display = "none";

        statusText.innerText = "Camera: RTSP ON 🟢";
        statusText.className = "status-on";

        setTimeout(() => {
            detectLoop();
        }, 500);
    }

    startBtn.onclick = async () => {
        if (isRTSP) {
            await fetch("http://127.0.0.1:5000/start_camera");
            startRTSPCamera();
        } else {
            startCamera(); // 🔥 original unchanged
        }
    };

    stopBtn.onclick = stopCamera;

    connectBtn.onclick = async () => {
        const url = rtspInput.value.trim();

        if (!url) {
            alert("Enter RTSP URL");
            return;
        }

        await fetch("http://127.0.0.1:5000/set_rtsp", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ url })
        });

        alert("RTSP URL Saved ✅");
    };

    toggleBtn.onclick = async () => {
        const res = await fetch("http://127.0.0.1:5000/toggle_mode");
        const data = await res.json();

        isRTSP = data.mode === "RTSP";
        alert("Switched to: " + data.mode);
    };

    async function detectLoop() {
        if (!running) return;

        if (isRTSP) {
            if (!video || video.readyState < 2) {
                requestAnimationFrame(detectLoop);
                return;
            }
        } else {
            if (video.videoWidth === 0) {
                requestAnimationFrame(detectLoop);
                return;
            }
        }

        try {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        } catch {
            requestAnimationFrame(detectLoop);
            return;
        }

        const image = canvas.toDataURL("image/jpeg");

        try {
            const res = await fetch("http://127.0.0.1:5000/recognize", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ image })
            });

            const data = await res.json();

            let output = "";

            if (Array.isArray(data)) {
                data.forEach(face => {

                    const [top, right, bottom, left] = face.box;

                    const color = face.name === "Unknown" ? "red" : "lime";

                    ctx.strokeStyle = color;
                    ctx.lineWidth = 3;
                    ctx.strokeRect(left, top, right - left, bottom - top);

                    ctx.fillStyle = color;
                    ctx.fillRect(left, top - 20, 120, 20);

                    ctx.fillStyle = "black";
                    ctx.fillText(face.name, left + 5, top - 5);

                    if (face.name === "Unknown") {
                        triggerUnknownAlert();
                    }

                    output += `👤 ${face.name} | ${face.status}\n`;
                });
            } else {
                output = data.name || "No face";
            }

            resultText.innerText = output;

        } catch (err) {
            console.error(err);
            resultText.innerText = "❌ Backend error";
        }

        setTimeout(() => {
            requestAnimationFrame(detectLoop);
        }, 300);
    }

    window.addEventListener("beforeunload", stopCamera);
}

