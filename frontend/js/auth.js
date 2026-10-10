const form = document.querySelector("form");
if (form) form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(form));
  try {
    const result = await apiRequest(location.pathname.includes("register") ? "/auth/register" : "/auth/login", {method: "POST", body: JSON.stringify(data)});
    if (result.token) localStorage.setItem("heart_token", result.token);
    location.href = result.token ? "dashboard.html" : "login.html";
  } catch (error) { document.querySelector("#message").textContent = error.message; }
});