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

        window.location.href = `/auth?authreturnto=${encodeURIComponent(window.location.pathname)}`;

        throw new Error("Token renewal failed");
    })
    .then((data) => {
        // if (!data.token) return
        localStorage.setItem("Token", data.token);
    });
