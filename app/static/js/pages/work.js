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

// === CPS / income per second ===
const cpsEl = document.getElementById("cps");
let clicksThisSecond = 0;

function updateCps() {
    if (!cpsEl) return;
    const cps = clicksThisSecond;
    const incomePerSecond = cps * multiplier;
    cpsEl.textContent = `${cps.toFixed(1)} CPS \n~ +${incomePerSecond.toFixed(2)}/s`;
    clicksThisSecond = 0;
}
setInterval(updateCps, 1000);
// ================================

function postClicks() {
    if (clickBuffer <= 0) {
        clickBuffer = 0;
        return;
    }

    const amount = clickBuffer; // сохраняем, сколько отправляем
    clickBuffer = 0;

    fetch("/api/v1/work/clicks", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Token: localStorage.getItem("Token"),
        },
        body: JSON.stringify({ amount }),
    })
        .then((resp) => {
            if (!resp.ok) {
                throw new Error("Click fetch failed");
            }
            return resp.json();
        })
        .then((data) => {
            // считаем фактическую выплату по балансу
            // const oldHand = typeof hand !== "undefined" ? hand : 0;
            const gained = data.balance_hand - _hand;

            // крупная частица с суммарной выплатой
            spawnBigParticle(gained, data.limit);

            patchHand(data.balance_hand);
        });
}

const clickBtn = document.getElementById("clickme");
const particleTemplate = document.getElementById("particle-template");

function spawnParticle(val) {
    if (!particleTemplate || !clickBtn) return;

    const rect = clickBtn.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;

    const offsetX = (Math.random() - 0.5) * width;
    const offsetY = (Math.random() - 0.5) * height;

    const p = particleTemplate.cloneNode(true);
    p.removeAttribute("id");
    p.textContent = `+${(val * multiplier).toFixed(2)}`;

    const baseLeft = 50 + (offsetX / width) * 400;
    const baseTop = 50 + (offsetY / height) * 400;

    p.style.left = `${baseLeft}%`;
    p.style.top = `${baseTop}%`;

    p.style.animation = "none";
    void p.offsetWidth;
    p.style.animation = "";

    clickBtn.appendChild(p);

    p.addEventListener("animationend", () => {
        p.remove();
    });
}

// крупная частица с другим цветом и x2 размером
function spawnBigParticle(amount, mlt) {
    if (!particleTemplate || !clickBtn || !amount) return;

    const rect = clickBtn.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;

    const offsetX = (Math.random() - 0.5) * width * 0.3;
    const offsetY = (Math.random() - 0.5) * height * 0.3;

    const p = particleTemplate.cloneNode(true);
    p.removeAttribute("id");
    p.textContent = `+${amount.toFixed(2)}`;

    const baseLeft = 50 + (offsetX / width) * 400;
    const baseTop = 50 + (offsetY / height) * 400;

    p.style.left = `${baseLeft}%`;
    p.style.top = `${baseTop}%`;

    // базовые стили большой частицы
    p.style.fontSize = "2em";
    p.style.textShadow = "0 0 8px rgba(255, 204, 0, 0.8)";

    if (mlt < 1) {
        // красный оттенок для mlt < 1
        p.style.color = "#ff4444";
        p.style.textShadow = "0 0 8px rgba(255, 68, 68, 0.8)";
        p.style.animationDuration = "8s !important";
        // подпись множителя под частицей
        let multSpan = document.createElement("div");
        multSpan.textContent = `×${mlt.toFixed(2)}`;
        multSpan.style.fontSize = "0.7em";
        multSpan.style.marginTop = "0.2em";
        multSpan.style.textAlign = "center";
        multSpan.style.color = "#ff8888";
        
        p.appendChild(multSpan);
        multSpan = document.createElement("div");
        multSpan.textContent = `ВЫРУБИ АВТОКЛИКЕР!`;
        multSpan.style.fontSize = "0.7em";
        multSpan.style.marginTop = "0.2em";
        multSpan.style.textAlign = "center";
        multSpan.style.color = "#ff8888";
        
        p.appendChild(multSpan);
    } else {
        // как раньше: жёлтый цвет
        p.style.color = "#ffcc00";
    }

    p.style.animation = "none";
    void p.offsetWidth;
    p.style.animation = "";

    clickBtn.appendChild(p);

    p.addEventListener("animationend", () => {
        p.remove();
    });
}

function clickBehaviour() {
    clickBuffer += 1;
    clicksThisSecond += 1;
    spawnParticle(1);
}

clickBtn.addEventListener("click", () => {
    clickBehaviour();
});
clickBtn.addEventListener("contextmenu", (e) => {
    e.preventDefault();
    clickBehaviour();
});

setInterval(postClicks, 10000);
