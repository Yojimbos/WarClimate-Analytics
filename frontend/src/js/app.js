const API_BASE = window.location.origin.includes("8080")
  ? "http://localhost:8000"
  : window.location.origin;

const state = {
  charts: {}
};

function defaultDateRange() {
  const end = new Date();
  const start = new Date();
  start.setDate(end.getDate() - 6);
  return {
    from: start.toISOString().slice(0, 10),
    to: end.toISOString().slice(0, 10)
  };
}

function setDefaultControls() {
  const range = defaultDateRange();
  document.querySelector("#fromDate").value = range.from;
  document.querySelector("#toDate").value = range.to;
}

async function fetchJson(path, params) {
  const url = new URL(`${API_BASE}${path}`);
  Object.entries(params).forEach(([key, value]) => url.searchParams.set(key, value));
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return response.json();
}

function renderSummary(cards) {
  const root = document.querySelector("#summaryCards");
  root.innerHTML = "";
  cards.forEach((card) => {
    const article = document.createElement("article");
    article.className = "card summary-card";
    article.innerHTML = `
      <p class="summary-label">${card.label}</p>
      <p class="summary-value">${card.value}</p>
      <p class="summary-context">${card.context ?? ""}</p>
    `;
    root.appendChild(article);
  });
}

function renderList(elementId, items, render) {
  const root = document.querySelector(elementId);
  root.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.innerHTML = render(item);
    root.appendChild(li);
  });
}

function renderTable(records) {
  const body = document.querySelector("#recordsTable");
  body.innerHTML = "";
  records.forEach((record) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${record.date}</td>
      <td>${record.personnel_losses}</td>
      <td>${record.avg_temperature_c ?? "n/a"} C</td>
      <td>${record.precipitation_mm ?? "n/a"} mm</td>
      <td>${record.weather_summary ?? "n/a"}</td>
      <td>${record.rolling_losses_7d ?? "n/a"}</td>
    `;
    body.appendChild(row);
  });
}

function upsertChart(key, canvasId, config) {
  if (state.charts[key]) {
    state.charts[key].destroy();
  }
  const ctx = document.getElementById(canvasId);
  state.charts[key] = new Chart(ctx, config);
}

function renderCharts(records) {
  const labels = records.map((item) => item.date);
  upsertChart("timeseries", "timeseriesChart", {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Personnel losses",
          data: records.map((item) => item.personnel_losses),
          borderColor: "#d9485f",
          backgroundColor: "rgba(217, 72, 95, 0.15)",
          yAxisID: "y"
        },
        {
          label: "Avg temperature C",
          data: records.map((item) => item.avg_temperature_c),
          borderColor: "#0d6e6e",
          backgroundColor: "rgba(13, 110, 110, 0.15)",
          yAxisID: "y1"
        },
        {
          label: "7-day rolling losses",
          data: records.map((item) => item.rolling_losses_7d),
          borderColor: "#f1a548",
          borderDash: [8, 4],
          yAxisID: "y"
        }
      ]
    },
    options: {
      responsive: true,
      interaction: { mode: "index", intersect: false },
      scales: {
        y: { position: "left" },
        y1: { position: "right", grid: { drawOnChartArea: false } }
      }
    }
  });

  upsertChart("tempScatter", "temperatureScatter", {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Temperature vs losses",
          data: records.map((item) => ({ x: item.avg_temperature_c, y: item.personnel_losses })),
          backgroundColor: "#0d6e6e"
        }
      ]
    }
  });

  upsertChart("precipScatter", "precipitationScatter", {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Precipitation vs losses",
          data: records.map((item) => ({ x: item.precipitation_mm, y: item.personnel_losses })),
          backgroundColor: "#315cfd"
        }
      ]
    }
  });
}

async function loadDashboard() {
  const from = document.querySelector("#fromDate").value;
  const to = document.querySelector("#toDate").value;
  const location = document.querySelector("#location").value;
  const [summary, correlation] = await Promise.all([
    fetchJson("/api/v1/summary", { from, to, location }),
    fetchJson("/api/v1/correlation", { from, to, location })
  ]);
  renderSummary(summary.cards);
  renderTable(correlation.records);
  renderCharts(correlation.records);
  renderList("#insightsList", correlation.insights, (item) => item);
  renderList("#sourcesList", summary.sources, (item) => `<a href="${item.url}" target="_blank" rel="noreferrer">${item.name}</a>`);
  renderList("#limitationsList", summary.limitations, (item) => item);
}

function bindEvents() {
  document.querySelector("#applyFilters").addEventListener("click", () => {
    loadDashboard().catch(console.error);
  });
}

setDefaultControls();
bindEvents();
loadDashboard().catch(console.error);

