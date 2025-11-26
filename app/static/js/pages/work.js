let multiplier = 0.1;
fetch("/api/v1/work/multiplier")
    .then((resp) => {
        if (!resp.ok) {
            throw new Error("Multiplier fetch failed");
        }
        return resp.json();
    })
    .then((data) => {
        multiplier = data.profit;
    });

let clickBuffer = 0;
function postClicks() {
    if (clickBuffer <= 0) {
        clickBuffer = 0;
        return;
    }
    fetch("/api/v1/work/clicks", {
        method: "POST",
        headers: { Token: localStorage.getItem("Token") },
        body: JSON.stringify({ amount: clickBuffer }),
    })
        .then((resp) => {
            if (!resp.ok) {
                throw new Error("Click fetch failed");
            }
            return resp.json();
        })
        .then((data) => {
            patchHand(data.balance_hand);
        });
    clickBuffer = 0;
}
document.getElementById("clickme").addEventListener("click", () => {
    clickBuffer += 1;
});
setInterval(postClicks, 30000);
