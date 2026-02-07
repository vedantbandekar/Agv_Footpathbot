import { fetchLatestRoverData } from "./api.js";

/* ================== CONSTANTS ================== */
const API_ENDPOINT = "http://127.0.0.1:5000/api/telemetry";
const UPDATE_INTERVAL = 2000;

/* ================== DOM REFERENCES ================== */
const els = {
    roverId: document.getElementById("roverId"),
    lat: document.getElementById("lat"),
    lng: document.getElementById("lng"),
    gps: document.getElementById("gps"),
    ultrasonic: document.getElementById("distance"),
    battery: document.getElementById("battery"),
    batteryBar: document.getElementById("batteryBar"),
    history: document.getElementById("history"),
    statusDot: document.getElementById("statusDot"),
    statusText: document.getElementById("statusText"),
    botImg: document.getElementById("botImage"),
    imgTime: document.getElementById("imgTime"),
    manualBtn: document.getElementById("sendManual")
};

/* ================== MAP ================== */
let map;
let roverMarker;

function initMap() {
    const mapEl = document.getElementById("map");
    if (!mapEl) return;

    map = L.map(mapEl, { zoomControl: false, attributionControl: false })
        .setView([0, 0], 15);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")
        .addTo(map);

    const roverIcon = L.divIcon({
        className: "custom-div-icon",
        html: `<div style="
            background:#007AFF;
            width:14px;height:14px;
            border-radius:50%;
            border:2px solid white;
            box-shadow:0 0 15px rgba(0,122,255,.6)">
        </div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7]
    });

    roverMarker = L.marker([0, 0], { icon: roverIcon }).addTo(map);
}

/* ================== DASHBOARD UPDATE ================== */
async function updateDashboard() {
    const data = await fetchLatestRoverData();
    if (!data) return setOfflineStatus();

    setOnlineStatus();
    els.roverId.textContent = data.rover_id || "BOT-042";

    updateLocation(data.gps);
    updateSensors(data);
    updateImage(data.image_url);
    updateHistory(data);
}

/* ================== UPDATE HELPERS ================== */
function updateLocation(gps) {
    if (!gps?.lat || !gps?.lng || !roverMarker) return;

    const { lat, lng } = gps;
    const pos = [lat, lng];

    roverMarker.setLatLng(pos);
    map.panTo(pos);

    els.lat.textContent = lat.toFixed(4);
    els.lng.textContent = lng.toFixed(4);
    els.gps && (els.gps.textContent = `${lat.toFixed(2)}° N, ${lng.toFixed(2)}° E`);
}

function updateSensors(data) {
    els.ultrasonic.textContent = data.ultrasonic?.distance ?? "--";
    els.battery.textContent = `${data.battery ?? "--"}%`;

    if (els.batteryBar) {
        els.batteryBar.style.width = `${data.battery || 0}%`;
    }
}

function updateImage(url) {
    if (!url || !els.botImg || els.botImg.src === url) return;

    els.botImg.src = url;
    els.imgTime.textContent = new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}

function updateHistory(data) {
    if (!els.history) return;

    const li = document.createElement("li");
    const time = new Date().toLocaleTimeString([], {
        hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit"
    });

    li.className =
        "flex justify-between border-b border-white/5 pb-1 hover:text-blue-400 transition-colors";

    li.innerHTML = `
        <span class="text-slate-600 mr-2">[${time}]</span>
        <span class="flex-1">POS: ${data.gps?.lat?.toFixed(2) ?? "--"}, ${data.gps?.lng?.toFixed(2) ?? "--"}</span>
        <span class="text-blue-500 font-bold">${data.ultrasonic?.distance ?? "--"}cm</span>
    `;

    els.history.prepend(li);
    if (els.history.children.length > 8) {
        els.history.lastChild.remove();
    }
}

/* ================== STATUS ================== */
function setOnlineStatus() {
    els.statusDot.className = "w-3 h-3 rounded-full bg-green-500 animate-pulse";
    els.statusText.textContent = "SYSTEM ONLINE";
}

function setOfflineStatus() {
    els.statusDot.className = "w-3 h-3 rounded-full bg-red-600";
    els.statusText.textContent = "CONNECTION LOST";
}

/* ================== MANUAL OVERRIDE ================== */
els.manualBtn?.addEventListener("click", async () => {
    const lat = parseFloat(document.getElementById("mLat").value);
    const lng = parseFloat(document.getElementById("mLng").value);
    const dist = parseFloat(document.getElementById("mDist").value);
    const imageInput = document.getElementById("mImage");

    if (isNaN(lat) || isNaN(lng) || isNaN(dist)) {
        alert("Invalid telemetry values");
        return;
    }

    const payload = {
        rover_id: "MANUAL-CTRL",
        source: "MANUAL",
        gps: { lat, lng },
        ultrasonic: { distance: dist },
        battery: 100
    };

    const formData = new FormData();
    formData.append("data", JSON.stringify(payload));

    if (imageInput?.files?.[0]) {
        formData.append("image", imageInput.files[0]);
    }

    try {
        await fetch("http://127.0.0.1:5000/api/telemetry", {
            method: "POST",
            body: formData
        });

        imageInput.value = "";
        updateDashboard();
    } catch (err) {
        console.error("Manual override failed", err);
    }
});

/* ================== START ================== */
initMap();
updateDashboard();
setInterval(updateDashboard, UPDATE_INTERVAL);
