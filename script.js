const API_URL = "https://rustic-garden-api.azurewebsites.net";

async function getTime() {
    const res = await fetch(`${API_URL}/time`);
    const data = await res.json();
    document.getElementById("output").innerText = data.time;
}
