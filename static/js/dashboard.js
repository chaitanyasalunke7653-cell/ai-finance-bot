/**
 * Personal Finance Advisor Bot - Dashboard Overview & Chart Visualizations
 */

let categoryChartInstance = null;
let trendsChartInstance = null;

// Palette for Category Doughnut (Strictly professional financial colors - no purple gradients)
const CATEGORY_COLORS = [
  "#059669", // Emerald
  "#2563eb", // Royal Blue
  "#d97706", // Amber
  "#dc2626", // Crimson
  "#0891b2", // Cyan
  "#475569", // Slate
  "#ea580c", // Orange
  "#4f46e5", // Indigo
  "#0d9488"  // Teal
];

/**
 * Loads aggregated dashboard summary from backend API
 */
async function loadDashboardData() {
  const month = currentSelectedMonth || "";
  try {
    const res = await fetch(`/api/dashboard?month=${encodeURIComponent(month)}`);
    if (!res.ok) {
      if (res.status === 401) {
        window.location.href = "/login";
        return;
      }
      throw new Error("Failed to load dashboard metrics.");
    }

    const data = await res.json();
    renderKpiCards(data);
    renderCategoryChart(data.category_breakdown);
    renderTrendsChart(data.monthly_trends);
    renderRecentTransactions(data.recent_transactions);
    renderQuickGoals(data.savings_goals);
  } catch (err) {
    console.error("Dashboard load error:", err);
    showToast("Error retrieving financial metrics.", "danger");
  }
}

/**
 * Updates KPI Summary Cards
 */
function renderKpiCards(data) {
  const incomeEl = document.getElementById("kpiIncome");
  const expensesEl = document.getElementById("kpiExpenses");
  const savingsEl = document.getElementById("kpiSavings");
  const savingsRateEl = document.getElementById("kpiSavingsRate");
  const budgetRemEl = document.getElementById("kpiBudgetRemaining");
  const budgetLimitEl = document.getElementById("kpiBudgetLimit");

  if (incomeEl) incomeEl.textContent = formatINR(data.total_income);
  if (expensesEl) expensesEl.textContent = formatINR(data.total_expenses);
  if (savingsEl) {
    savingsEl.textContent = formatINR(data.savings);
    if (data.savings < 0) {
      savingsEl.classList.remove("text-primary");
      savingsEl.classList.add("text-danger");
    } else {
      savingsEl.classList.remove("text-danger");
      savingsEl.classList.add("text-primary");
    }
  }

  if (savingsRateEl) {
    savingsRateEl.textContent = `Savings Rate: ${data.savings_percentage}% of revenue`;
  }

  if (budgetRemEl) {
    budgetRemEl.textContent = formatINR(data.remaining_budget);
    if (data.remaining_budget < 0) {
      budgetRemEl.classList.add("text-danger");
    } else {
      budgetRemEl.classList.remove("text-danger");
    }
  }

  if (budgetLimitEl) {
    budgetLimitEl.textContent = `Budget Limit: ${formatINR(data.total_budget_limit)}`;
  }
}

/**
 * Renders Category Breakdown Doughnut Chart
 */
function renderCategoryChart(breakdown) {
  const canvas = document.getElementById("categoryChart");
  const emptyState = document.getElementById("categoryEmptyState");
  if (!canvas) return;

  if (!breakdown || breakdown.length === 0) {
    canvas.style.display = "none";
    if (emptyState) emptyState.style.display = "block";
    if (categoryChartInstance) {
      categoryChartInstance.destroy();
      categoryChartInstance = null;
    }
    return;
  }

  canvas.style.display = "block";
  if (emptyState) emptyState.style.display = "none";

  const labels = breakdown.map(item => item.category);
  const values = breakdown.map(item => item.amount);
  const colors = labels.map((_, i) => CATEGORY_COLORS[i % CATEGORY_COLORS.length]);

  if (categoryChartInstance) {
    categoryChartInstance.destroy();
  }

  const ctx = canvas.getContext("2d");
  categoryChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: "#ffffff"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            boxWidth: 12,
            font: { size: 11, family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" }
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const val = context.parsed;
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
              return ` ${context.label}: ${formatINR(val)} (${pct}%)`;
            }
          }
        }
      },
      cutout: "68%"
    }
  });
}

/**
 * Renders Monthly Trends Chart (Income vs Expense)
 */
function renderTrendsChart(trends) {
  const canvas = document.getElementById("trendsChart");
  if (!canvas || !trends) return;

  if (trendsChartInstance) {
    trendsChartInstance.destroy();
  }

  const ctx = canvas.getContext("2d");
  trendsChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: trends.labels || [],
      datasets: [
        {
          label: "Income (₹)",
          data: trends.income || [],
          backgroundColor: "#059669", // Emerald
          borderRadius: 4,
          borderSkipped: false
        },
        {
          label: "Expenses (₹)",
          data: trends.expense || [],
          backgroundColor: "#dc2626", // Crimson
          borderRadius: 4,
          borderSkipped: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { size: 11 } }
        },
        y: {
          grid: { color: "#f1f5f9" },
          ticks: {
            callback: function(val) {
              return "₹" + Number(val).toLocaleString("en-IN");
            },
            font: { size: 11 }
          }
        }
      },
      plugins: {
        legend: {
          position: "top",
          align: "end",
          labels: { boxWidth: 12, font: { size: 11 } }
        },
        tooltip: {
          callbacks: {
            label: function(ctx) {
              return ` ${ctx.dataset.label}: ${formatINR(ctx.raw)}`;
            }
          }
        }
      }
    }
  });
}

/**
 * Renders Recent Transactions Table in Overview Tab
 */
function renderRecentTransactions(transactions) {
  const tbody = document.getElementById("recentTransactionsTableBody");
  if (!tbody) return;

  if (!transactions || transactions.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="text-center py-4 text-muted">No transactions logged for this period.</td>
      </tr>
    `;
    return;
  }

  let html = "";
  transactions.forEach(t => {
    const isIncome = t.type === "income";
    const typeBadge = isIncome
      ? `<span class="badge badge-success">Income</span>`
      : `<span class="badge badge-danger">Expense</span>`;
    const amtColor = isIncome ? "text-success font-bold" : "text-danger font-bold";
    const amtSign = isIncome ? "+" : "-";

    html += `
      <tr>
        <td class="text-sm">${formatDate(t.date)}</td>
        <td>${typeBadge}</td>
        <td class="font-medium">${escapeHtml(t.category || t.title)}</td>
        <td class="text-muted text-sm">${escapeHtml(t.description || "-")}</td>
        <td class="text-right ${amtColor}">${amtSign} ${formatINR(t.amount)}</td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
}

/**
 * Renders Savings Goals Progress Widget in Overview Tab
 */
function renderQuickGoals(goals) {
  const container = document.getElementById("quickGoalsContainer");
  if (!container) return;

  if (!goals || goals.length === 0) {
    container.innerHTML = `
      <div class="text-center py-4 text-muted">
        No active savings targets set.
        <br><button class="btn btn-outline btn-sm mt-2" onclick="switchView('goals')">Create First Goal</button>
      </div>
    `;
    return;
  }

  let html = "";
  goals.slice(0, 3).forEach(g => {
    html += `
      <div class="mb-3">
        <div class="d-flex justify-between text-sm mb-1">
          <span class="font-medium text-dark">${escapeHtml(g.name)}</span>
          <span class="text-muted">${formatINR(g.current_amount)} / ${formatINR(g.target_amount)} (${g.percentage_completed}%)</span>
        </div>
        <div class="progress-bar-container">
          <div class="progress-bar-fill bg-success" style="width: ${g.percentage_completed}%;"></div>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}
