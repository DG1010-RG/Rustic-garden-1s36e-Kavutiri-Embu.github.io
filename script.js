const API_URL = "rustic-garden-api-bzhbh0gxf2ayh6ev.ukwest-01.azurewebsites.net";

async function getTime() {
    const res = await fetch(`${API_URL}/time`);
    const data = await res.json();
    document.getElementById("output").innerText = data.time;
}
