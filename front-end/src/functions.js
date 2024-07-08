API_BASE_URL = "http://127.0.0.1:8000/api"

function isLoggedIn() {
    const requiredKeys = ['account_id', 'first_name', 'last_name', 'user_role', 'token'];
    
    return requiredKeys.every(key => sessionStorage.getItem(key) !== null);
}

async function redirectIfNotLoggedIn() {
    const response = await fetch(`${API_BASE_URL}/auth/verify`, {
        method: "GET", 
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${sessionStorage.getItem("token")}`
        }
    });
    if (response.status == 401) {
        sessionStorage.setItem("redirectURL", window.location.href);
        window.location.href = "/login/index.html";
        return;
    }
    return ;
}

try {
    if (window.location.hostname != '' && window.location.hostname != '127.0.0.1') {
        API_BASE_URL = `${window.location.protocol}//${window.location.hostname}/api`
    }
} 
catch {
    console.log("You are probably running this as a local file");
}