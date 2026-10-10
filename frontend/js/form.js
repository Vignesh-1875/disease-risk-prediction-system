document.querySelector("#prediction-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(event.target));
  for (const key of Object.keys(data)) data[key] = Number(data[key]);
  try {
    const result = await apiRequest("/prediction/heart", {method: "POST", body: JSON.stringify(data)});
    localStorage.setItem("last_result", JSON.stringify(result));
    location.href = "results.html";
  } catch (error) { document.querySelector("#message").textContent = error.message; }
});