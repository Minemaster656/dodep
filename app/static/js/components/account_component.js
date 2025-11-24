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
        localStorage.setItem("Token", data.token);
        document.getElementById("account-component-logged").classList.remove("hidden");
        document.getElementById("account-component-login").classList.add("hidden");

        // тянем данные пользователя
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

        // тянем баланс
        return fetch("/api/v1/bank/balance", {
            method: "GET",
            headers: {
                Token: localStorage.getItem("Token"),
            },
        });
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error("Balance fetch failed");
        }
        return response.json();
    })
    .then((balance) => {
        // форматируй как хочешь, пример:
        const text =
            "🍬" + balance.hand.toFixed(1) + " 🏦" + balance.bank.toFixed(1) + " 🎰" + balance.casino.toFixed(1) + " 💰" + balance.debt.toFixed(1);

        document.getElementById("account-balance").textContent = text;
    })
    .catch((error) => console.error("Error:", error));

document.getElementById("account-logout-button").addEventListener("click", () => {
    localStorage.removeItem("Token");
    localStorage.removeItem("UID");
    window.location.reload();
});
