const BASE = "http://127.0.0.1:5000";

function getUser(){
    return localStorage.getItem("user_id");
}

async function getStatus(){
    const res = await fetch(BASE + "/parking-status");
    const data = await res.json();
    document.getElementById("status").innerText = JSON.stringify(data, null, 2);
}

async function getRecommendation(){
    const res = await fetch(BASE + "/recommendation");
    const data = await res.json();
    document.getElementById("rec").innerText = data.recommended_zone;
}

async function checkin(){
    await fetch(BASE + "/checkin", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            user_id: getUser(),
            zone_id: document.getElementById("zone").value
        })
    });
    alert("Checked In");
}

async function checkout(){
    await fetch(BASE + "/checkout", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            log_id: document.getElementById("log_id").value
        })
    });
    alert("Checked Out");
}

async function getHistory(){
    const user = getUser();
    const res = await fetch(BASE + "/user-history/" + user);
    const data = await res.json();

    document.getElementById("history").innerText =
        JSON.stringify(data, null, 2);
}

async function getAnalytics(){
    const res = await fetch(BASE + "/analytics");
    const data = await res.json();

    document.getElementById("analytics").innerText =
        JSON.stringify(data, null, 2);
}