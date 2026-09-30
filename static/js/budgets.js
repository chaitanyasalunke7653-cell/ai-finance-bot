/**
 * Personal Finance Advisor Bot - Budget Planner
 */

let allBudgetsCache = [];

/**
 * Loads monthly budget allocations and actual category expenditures
 */
async function loadBudgetsList() {
  const monthFilter = document.getElementById("budgetMonthFilter");
  const month = monthFilter ? monthFilter.value : currentSelectedMonth;

  const container = document.getElementById("budgetCardsGrid");
  const totalCapEl = document.getElementById("budgetTotalCap");
  const totalSpentEl = document.getElementById("budgetTotalSpent");

  if (!container) return;

  try {
    const res = await fetch(`/api/budgets?month=${encodeURIComponent(month)}`);
    if (!res.ok) throw new Error("Failed to load budget data.");

    const data = await res.json();
    allBudgetsCache = data.budgets || [];

    let totalCap = 0;
    let totalSpent = 0;

    if (allBudgetsCache.length === 0) {
      container.innerHTML = `
        <div class="card p-4 text-center text-muted" style="grid-column: 1 / -1;">
          No budget limits defined for ${month}.
          <br><button class="btn btn-primary btn-sm mt-3" onclick="openBudgetModal()">Set Category Budget</button>
        </div>
      `;
      if (totalCapEl) totalCapEl.textContent = formatINR(0);
      if (totalSpentEl) totalSpentEl.textContent = formatINR(0);
      return;
    }

    let cardsHtml = "";
    allBudgetsCache.forEach(b => {
      totalCap += b.limit;
      totalSpent += b.spent;

      let badgeClass = "badge-success";
      let barColor = "bg-success";
      let statusLabel = "Normal";

      if (b.status === "exceeded") {
        badgeClass = "badge-danger";
        barColor = "bg-danger";
        statusLabel = "Exceeded";
      } else if (b.status === "warning") {
        badgeClass = "badge-warning";
        barColor = "bg-warning";
        statusLabel = "Warning (>=80%)";
      }

      const clampedPct = Math.min(b.percentage_used, 100);

      cardsHtml += `
        <div class="budget-card">
          <div class="budget-card-header">
            <h4 class="budget-card-title">${escapeHtml(b.category)}</h4>
            <span class="badge ${badgeClass}">${statusLabel}</span>
          </div>

          <div class="budget-card-figures">
            <span class="text-muted">Spent: <strong class="text-dark">${formatINR(b.spent)}</strong></span>
            <span class="text-muted">Limit: <strong>${formatINR(b.limit)}</strong></span>
          </div>

          <div class="progress-bar-container mb-2">
            <div class="progress-bar-fill ${barColor}" style="width: ${clampedPct}%;"></div>
          </div>

          <div class="d-flex justify-between text-sm">
            <span class="text-muted">${b.percentage_used}% used</span>
            <span class="${b.remaining < 0 ? 'text-danger font-bold' : 'text-muted'}">
              ${b.remaining < 0 ? 'Over by ' + formatINR(Math.abs(b.remaining)) : formatINR(b.remaining) + ' remaining'}
            </span>
          </div>

          <div class="budget-actions">
            <button class="btn btn-outline btn-sm mr-2" onclick="editBudgetRecord(${b.id})" title="Update Limit">
              Update Limit
            </button>
            <button class="btn btn-danger btn-sm" onclick="deleteBudgetRecord(${b.id})" title="Remove Limit">
              Remove
            </button>
          </div>
        </div>
      `;
    });

    container.innerHTML = cardsHtml;
    if (totalCapEl) totalCapEl.textContent = formatINR(totalCap);
    if (totalSpentEl) totalSpentEl.textContent = formatINR(totalSpent);
  } catch (err) {
    console.error("Budget loading error:", err);
    showToast("Failed to load budget data.", "danger");
  }
}

/**
 * Opens Budget Modal in Create mode
 */
function openBudgetModal() {
  document.getElementById("budgetModalTitle").textContent = "Set Category Budget";
  document.getElementById("budgetId").value = "";
  document.getElementById("budgetForm").reset();

  const monthFilter = document.getElementById("budgetMonthFilter");
  document.getElementById("budgetMonth").value = monthFilter ? monthFilter.value : currentSelectedMonth;

  document.getElementById("budgetModal").style.display = "flex";
}

/**
 * Closes Budget Modal
 */
function closeBudgetModal() {
  document.getElementById("budgetModal").style.display = "none";
}

/**
 * Opens Budget Modal for editing limit
 */
function editBudgetRecord(id) {
  const item = allBudgetsCache.find(x => x.id === id);
  if (!item) return;

  document.getElementById("budgetModalTitle").textContent = `Update Limit for ${item.category}`;
  document.getElementById("budgetId").value = item.id;
  document.getElementById("budgetMonth").value = item.month;
  document.getElementById("budgetCategory").value = item.category;
  document.getElementById("budgetLimit").value = item.limit;

  document.getElementById("budgetModal").style.display = "flex";
}

/**
 * Submits Budget create or update form
 */
async function submitBudgetForm(e) {
  e.preventDefault();
  const id = document.getElementById("budgetId").value;
  const month = document.getElementById("budgetMonth").value;
  const category = document.getElementById("budgetCategory").value;
  const limit = parseFloat(document.getElementById("budgetLimit").value);

  const saveBtn = document.getElementById("budgetSaveBtn");
  saveBtn.disabled = true;

  const payload = { month, category, limit };
  const method = id ? "PUT" : "POST";
  const url = id ? `/api/budgets/${id}` : "/api/budgets";

  try {
    const res = await fetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to save budget limit.");

    closeBudgetModal();
    showToast(data.message || "Budget limit saved.", "success");
    loadBudgetsList();
    if (typeof loadDashboardData === "function") loadDashboardData();
  } catch (err) {
    showToast(err.message, "danger");
  } finally {
    saveBtn.disabled = false;
  }
}

/**
 * Deletes budget record
 */
async function deleteBudgetRecord(id) {
  if (!confirm("Are you sure you want to remove this budget limit?")) return;

  try {
    const res = await fetch(`/api/budgets/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to remove budget.");

    showToast("Budget limit deleted.", "success");
    loadBudgetsList();
    if (typeof loadDashboardData === "function") loadDashboardData();
  } catch (err) {
    showToast(err.message, "danger");
  }
}
