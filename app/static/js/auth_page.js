// document.addEventListener("DOMContentLoaded", function () {
const tabs = document.querySelectorAll(".tab");
const loginTab = document.getElementById("tab-header-login");
const registerTab = document.getElementById("tab-header-register");
const loginInput = document.getElementById("login");
const nameInput = document.getElementById("name");
const passwordInput = document.getElementById("password");
const showPasswordButton = document.getElementById("show-password-button");
let capchaInput = document.getElementById("capcha-text");
let authButton = document.getElementById("auth-button");
let isRegister = false;

tabs.forEach((tab) => {
    tab.addEventListener("click", function () {
        tabs.forEach((t) => t.classList.remove("active"));
        this.classList.add("active");
        isRegister = this.dataset.tab == "register";
        if (this.dataset.tab === "login") {
            nameInput.classList.add("hidden");
        } else {
            nameInput.classList.remove("hidden");
        }
    });
});

showPasswordButton.addEventListener("click", function () {
    if (passwordInput.type === "password") {
        passwordInput.type = "text";
    } else {
        passwordInput.type = "password";
    }
});

// Initialize
if (loginTab.classList.contains("active")) {
    nameInput.classList.add("hidden");
}

authButton.addEventListener("click", async () => {
    const payload = {
        password: passwordInput.value,
        login: loginInput.value,
        capcha: capchaInput.value,
    };

    if (isRegister) {
        payload.name = nameInput.value;
    }
    console.log(payload)
    try {
        const response = await fetch("/api/v1/auth/auth", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        const data = await response.json();
        console.log(data);
    } catch (error) {
        console.error("Error during authentication:", error);
    } finally {
        getCaptcha();
    }
});

async function getCaptcha() {
    capchaInput.value = "";
    try {
        const response = await fetch("/api/v1/auth/getcapcha");
        const data = await response.json();
        // console.log(data)
        document.getElementById("capcha-img").src = data.img;
        return data.uuid;
    } catch (error) {
        console.error("Error fetching captcha:", error);
    }
}

let captchaUuid = null;

document.addEventListener("DOMContentLoaded", async function () {
    captchaUuid = await getCaptcha();
});
// });
