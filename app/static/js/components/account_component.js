fetch("/api/v1/auth/renewtoken", {
    method: "GET",
    headers: {
        Token: localStorage.getItem("Token"),
    },
})
    .then((response) => {
        if (response.status === 200) {
            return response.json();
        }
        throw new Error("Token renewal failed");
    })
    .then((data) => {
        // if (!data.token) return
        localStorage.setItem("Token", data.token);
        document.getElementById("account-component-logged").classList.remove("hidden");
        document.getElementById("account-component-login").classList.add("hidden");
        return fetch("/api/v1/auth/fetchuser", {
            method: "GET",
            headers: {
                UID: localStorage.getItem("UID"),
            },
        });
    })
    .then((response) => response.json())
    .then((data) => {
        document.getElementById("account-name").textContent = data.name;
        document.getElementById("account-login").textContent = data.login;
    })
    .catch((error) => console.error("Error:", error));

document.getElementById("account-logout-button").addEventListener("click", () => {
    localStorage.removeItem("Token");
    localStorage.removeItem("UID");
    window.location.reload();
});