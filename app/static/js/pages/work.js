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
        headers: {
            "Content-Type": "application/json",
            Token: localStorage.getItem("Token"),
        },
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

const clickBtn = document.getElementById("clickme");
const particleTemplate = document.getElementById("particle-template");

function spawnParticle(val) {
    if (!particleTemplate || !clickBtn) return;

    const rect = clickBtn.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;

    // диапазон смещения: от -0.5 до 0.5 ширины/высоты
    const offsetX = (Math.random() - 0.5) * width;
    const offsetY = (Math.random() - 0.5) * height;

    const p = particleTemplate.cloneNode(true);
    p.removeAttribute("id");
    p.textContent = `+${(val * multiplier).toFixed(2)}`;

    // позиция от центра кнопки плюс случайное смещение
    // центр кнопки в её системе координат: left = 50%, top = 50%
    const baseLeft = 50 + (offsetX / width) * 400; // в процентах
    const baseTop = 50 + (offsetY / height) * 400; // в процентах

    p.style.left = `${baseLeft}%`;
    p.style.top = `${baseTop}%`;

    // сброс/перезапуск анимации
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
