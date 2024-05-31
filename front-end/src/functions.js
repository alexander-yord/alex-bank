function isLoggedIn() {
    const requiredKeys = ['account_id', 'first_name', 'last_name', 'user_role', 'token'];
    
    return requiredKeys.every(key => sessionStorage.getItem(key) !== null);
}

API_BASE_URL = "http://127.0.0.1:8000"

try {
    if (window.location.hostname != '') {
        API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:${window.location.port}`
    }
} 
catch {
    console.log("You are probably running this as a local file");
}