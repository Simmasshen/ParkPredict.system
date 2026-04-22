async function register(){
    const data = await fetch("http://127.0.0.1:5000/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            username: username.value,
            password: password.value
        })
    });

    const res = await data.json();
    document.getElementById("msg").innerText = res.message;
}

async function login(){
    const res = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            username: username.value,
            password: password.value
        })
    });

    const data = await res.json();

    if(res.status === 200){
        localStorage.setItem("user_id", data.user_id);
        window.location.href = "dashboard.html";
    } else {
        document.getElementById("msg").innerText = data.message;
    }
}