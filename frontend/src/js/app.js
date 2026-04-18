const API_BASE = window.location.origin.includes("8080")
  ? "http://localhost:8000"
  : window.location.origin;

const state = {
  charts: {},
  loading: false,
  requestToken: 0
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
  document.querySelector("#location").value = "kharkiv";
}

function diffDaysInclusive(from, to) {
  const millisecondsPerDay = 24 * 60 * 60 * 1000;
  const fromDate = new Date(`${from}T00:00:00`);
  const toDate = new Date(`${to}T00:00:00`);
  return Math.floor((toDate - fromDate) / millisecondsPerDay) + 1;
}

function validateFilters(from, to) {
  if (!from || !to) {
    return "Choose both From and To dates.";
  }

  if (from > to) {
    return "From date must be earlier than or equal to To date.";
  }

  const rangeDays = diffDaysInclusive(from, to);
  if (rangeDays < 7 || rangeDays > 365) {
    return "Date range must be between 7 and 365 days.";
  }

  return null;
}

async function fetchJson(path, params) {
  const url = new URL(`${API_BASE}${path}`);
  Object.entries(params).forEach(([key, value]) => url.searchParams.set(key, value));
  const response = await fetch(url);
  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const payload = await response.json();
      if (payload?.detail) {
        detail = payload.detail;
      }
    } catch (error) {
      console.debug("Could not parse error response", error);
    }
    throw new Error(detail);
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

function setRequestStatus(message, tone = "muted") {
  const element = document.querySelector("#requestStatus");
  element.textContent = message;
  element.dataset.tone = tone;
}

function setControlsDisabled(disabled) {
  document.querySelector("#fromDate").disabled = disabled;
  document.querySelector("#toDate").disabled = disabled;
  document.querySelector("#location").disabled = disabled;
  document.querySelector("#applyFilters").disabled = disabled;
}

function setButtonLoading(loading) {
  const button = document.querySelector("#applyFilters");
  button.dataset.loading = loading ? "true" : "false";
  const label = button.querySelector(".button-label");
  label.textContent = loading ? "Processing..." : "Apply filters";
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

function resetCharts() {
  Object.values(state.charts).forEach((chart) => chart.destroy());
  state.charts = {};
}

function upsertChart(key, canvasId, config) {
  if (state.charts[key]) {
    state.charts[key].destroy();
  }
  const ctx = document.getElementById(canvasId);
  state.charts[key] = new Chart(ctx, config);
}

function renderCharts(records) {
  if (!records.length) {
    resetCharts();
    return;
  }

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
  if (state.loading) {
    return;
  }

  const from = document.querySelector("#fromDate").value;
  const to = document.querySelector("#toDate").value;
  const location = document.querySelector("#location").value;
  const validationError = validateFilters(from, to);

  if (validationError) {
    setRequestStatus(validationError, "error");
    return;
  }

  state.loading = true;
  state.requestToken += 1;
  const requestToken = state.requestToken;
  setControlsDisabled(true);
  setButtonLoading(true);
  setRequestStatus("Refreshing analytics for the selected range...", "muted");

  try {
    const [summary, correlation] = await Promise.all([
      fetchJson("/api/v1/summary", { from, to, location }),
      fetchJson("/api/v1/correlation", { from, to, location })
    ]);

    if (requestToken !== state.requestToken) {
      return;
    }

    renderSummary(summary.cards);
    renderTable(correlation.records);
    renderCharts(correlation.records);
    renderList("#insightsList", correlation.insights, (item) => item);
    renderList("#sourcesList", summary.sources, (item) => `<a href="${item.url}" target="_blank" rel="noreferrer">${item.name}</a>`);
    renderList("#limitationsList", summary.limitations, (item) => item);

    if (!correlation.records.length) {
      setRequestStatus("No overlapping records were found for this filter combination.", "warning");
    } else {
      setRequestStatus(`Loaded ${correlation.records.length} daily records for ${location}.`, "success");
    }
  } catch (error) {
    if (requestToken !== state.requestToken) {
      return;
    }
    console.error(error);
    setRequestStatus(error.message || "Could not refresh analytics. Please try again.", "error");
  } finally {
    if (requestToken === state.requestToken) {
      state.loading = false;
      setControlsDisabled(false);
      setButtonLoading(false);
    }
  }
}

function bindEvents() {
  document.querySelector("#applyFilters").addEventListener("click", () => {
    loadDashboard();
  });
}

setDefaultControls();
bindEvents();
loadDashboard();
