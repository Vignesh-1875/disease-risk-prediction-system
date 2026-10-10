apiRequest("/auth/me").then(({user}) => document.querySelector("#welcome").textContent = `Welcome, ${user.name}`).catch(() => location.href = "login.html");
apiRequest("/prediction/history").then(({predictions}) => {
  const counts = ["Low", "Medium", "High"].map(level => predictions.filter(item => item.risk_level === level).length);
  document.querySelector("#stats").innerHTML = `<div>Total: ${predictions.length}</div><div>High: ${counts[2]}</div><div>Medium: ${counts[1]}</div><div>Low: ${counts[0]}</div>`;
  document.querySelector("#recent").innerHTML = predictions.slice(0, 5).map(item => `<article>${item.risk_level} — ${Math.round(item.probability * 100)}%</article>`).join("");
  new Chart(document.querySelector("#risk-chart"), {type: "doughnut", data: {labels: ["Low", "Medium", "High"], datasets: [{data: counts, backgroundColor: ["#3aa981", "#e8b04b", "#dd6670"]}]}});
}).catch(error => document.querySelector("#recent").textContent = error.message);
