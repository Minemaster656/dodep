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
        updateBalance(balance.hand, balance.bank, balance.casino, balance.debt);
    })
    .catch((error) => console.error("Error:", error));

document.getElementById("account-logout-button").addEventListener("click", () => {
    localStorage.removeItem("Token");
    localStorage.removeItem("UID");
    window.location.reload();
});

let _hand, _bank, _casino, _debt;
function updateBalance(hand, bank, casino, debt) {
    const text = "🍬" + hand.toFixed(1) + " 🏦" + bank.toFixed(1) + " 🎰" + casino.toFixed(1) + " 💰" + debt.toFixed(1);
    _hand = hand
    _bank = bank
    _casino = casino
    _debt = debt
    document.getElementById("account-balance").textContent = text;
}

function refreshBalance() {
    fetch("/api/v1/bank/balance", {
        method: "GET",
        headers: {
            Token: localStorage.getItem("Token"),
        },
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error("Balance fetch failed");
        }
        return response.json();
    })
    .then((balance) => {
        updateBalance(balance.hand, balance.bank, balance.casino, balance.debt);
    })
    .catch((error) => console.error("Error:", error));
}

function patchHand(newHand) {
    updateBalance(newHand, _bank, _casino, _debt);
}

function patchBank(newBank) {
    updateBalance(_hand, newBank, _casino, _debt);
}

function patchCasino(newCasino) {
    updateBalance(_hand, _bank, newCasino, _debt);
}

function patchDebt(newDebt) {
    updateBalance(_hand, _bank, _casino, newDebt);
}