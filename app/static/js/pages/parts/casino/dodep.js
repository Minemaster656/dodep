document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("amountInput").max = _hand;
    document.getElementById("deposit-button").addEventListener("click", function () {
        const amountInput = document.getElementById("amountInput");
        const amount = parseFloat(amountInput.value);

        if (isNaN(amount) || amount <= 0) {
            // alert("Please enter a valid amount greater than zero.");
            createToast({ title: `Не получилось депнуть ${amount}`, message: "Попробуйте числовые значения > 0!", type: "warning" });
            amountInput.value = 0;
            return;
        }

        if (amount > _hand) {
            // alert(`The maximum amount you can deposit is ${_hand}.`);
            createToast({ title: `Не получилось депнуть ${amount}`, message: `Вам не хватает примерно ${(amount - _hand).toFixed(2)} фантиков`, type: "warning" });
            amountInput.value = Math.floor(_hand);
            return;
        }
        deposit(amount);
    });
});
function response2message(json_data) {
    if (!json_data.user_message) return;
    createToast({
        title: "Произошла ошибка",
        message: json_data.user_message,
        headerClass: json_data.class,
    });
}
function deposit(val) {
    fetch("/api/v1/casino/dep", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Token: localStorage.getItem("Token"),
        },
        body: JSON.stringify({ value: val }),
    })
        .then((response) => {
            if (response.ok) {
                return response.json().then((data) => {
                    createToast({
                        title: `Успешно депнуто ${val.toFixed(2)} фантиков`,
                        message: `Наличка: ${_hand.toFixed(2)} -> ${data.hand.toFixed(2)} | Казино: ${_casino.toFixed(2)} -> ${data.casino.toFixed(2)}`,
                        type: "success",
                    });
                    updateBalance(data.hand, data.bank, data.casino, data.debt);
                });
            } else if (response.status === 400) {
                return response.json().then((data) => {
                    response2message(data);
                });
            } else {
                createToast({ title: "Ошибка", type: "error", message: response.status });
                throw new Error("Request failed");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
}
