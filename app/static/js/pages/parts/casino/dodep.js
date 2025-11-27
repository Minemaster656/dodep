document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("amountInput").max = _hand;
    document.getElementById("deposit-button").addEventListener("click", function () {
        const amountInput = document.getElementById("amountInput");
        const amount = parseFloat(amountInput.value);

        if (isNaN(amount) || amount <= 0) {
            // alert("Please enter a valid amount greater than zero.");
            amountInput.value = 0;
            return;
        }

        if (amount > _hand) {
            // alert(`The maximum amount you can deposit is ${_hand}.`);
            amountInput.value = Math.floor(_hand);
            return;
        }
    });
});
