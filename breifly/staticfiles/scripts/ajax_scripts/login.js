function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

async function loginViaJSON() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    const loginURL = `/login/`;
    const redirect_url = `/home/`;

    try {
        const response = await fetch(loginURL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ email, password }),
        });

        console.log("Status Code:", response.status);
        console.log("Redirected:", response.redirected);
        console.log("Response URL:", response.url);

        const contentType = response.headers.get("Content-Type");
        console.log("Content-Type:", contentType);

        if (contentType && contentType.includes("application/json")) {
            const data = await response.json();
            console.log("Response JSON:", data);

            if (response.ok && data.success) {
                showMessage("Login successful!", "success");
                setTimeout(() => {
                    window.location.href = redirect_url;
                }, 1000);
            } else {
                const err = data.error || "Invalid credentials.";
                showMessage(err, "danger");
            }
        } else {
            const rawText = await response.text();
            console.error("Raw Response:", rawText);
            showMessage("Unexpected response format. Not JSON.", "danger");
        }
    } catch (error) {
        console.error("Fetch Error:", error);
        showMessage("Network error: " + error.message, "danger");
    }
}
