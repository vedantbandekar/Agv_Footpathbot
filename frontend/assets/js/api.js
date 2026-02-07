const API_BASE = "http://127.0.0.1:5000/api";

export async function fetchLatestRoverData() {
  try {
    const res = await fetch(`${API_BASE}/rover/latest`);
    if (!res.ok) throw new Error("No data");
    return await res.json();
  } catch (err) {
    console.error("API error:", err);
    return null;
  }
}
