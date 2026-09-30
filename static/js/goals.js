/**
 * Personal Finance Advisor Bot - Savings Goals Tracker
 */

let allGoalsCache = [];

/**
 * Loads user savings targets from API
 */
async function loadGoalsList() {
  const container = document.getElementById("goalsGridContainer");
  if (!container) return;

  try {
    const res = await fetch("/api/goals");
    if (!res.ok) throw new Error("Failed to load savings goals.");

    allGoalsCache = await res.json();

    if (allGoalsCache.length === 0) {
      container.innerHTML = `
        <div class="card p-4 text-center text-muted" style="grid-column: 1 / -1;">
          No savings goals created yet.
          <br><button class="btn btn-primary btn-sm mt-3" onclick="openGoalModal()">Create Your First Goal</button>
        </div>
      `;
      return;
    }

    let cardsHtml = "";
    allGoalsCache.forEach(g => {
      const isCompleted = g.percentage_completed >= 100;
      const statusBadge = isCompleted
        ? `<span class="badge badge-success">Achieved</span>`
        : `<span class="badge badge-neutral">${g.percentage_completed}%</span>`;

      cardsHtml += `
        <div class="goal-card">
          <div class="goal-header">
            <div>
              <h4 class="goal-name">${escapeHtml(g.name)}</h4>
              <span class="goal-meta">Target Date: ${formatDate(g.target_date)}</span>
            </div>
            ${statusBadge}
          </div>

          <div class="goal-figures">
            <span class="text-muted">Saved: <strong class="text-success">${formatINR(g.current_amount)}</strong></span>
            <span class="text-muted">Target: <strong>${formatINR(g.target_amount)}</strong></span>
          </div>

          <div class="progress-bar-container mb-2">
            <div class="progress-bar-fill bg-success" style="width: ${g.percentage_completed}%;"></div>
          </div>

          <div class="d-flex justify-between text-sm">
            <span class="text-muted">${formatINR(g.remaining_amount)} to target</span>
            <span class="text-muted font-medium">${g.percentage_completed}%</span>
          </div>

          <div class="goal-actions">
            <button class="btn btn-primary btn-sm" onclick="openDepositModal(${g.id})" title="Add Deposit">
              + Deposit Funds
            </button>
            <button class="btn btn-outline btn-sm mr-2" onclick="editGoalRecord(${g.id})" title="Edit Target">
              Edit
            </button>
            <button class="btn btn-danger btn-sm" onclick="deleteGoalRecord(${g.id})" title="Delete Target">
              Delete
            </button>
          </div>
        </div>
      `;
    });

    container.innerHTML = cardsHtml;
  } catch (err) {
    console.error("Goals loading error:", err);
    showToast("Failed to load savings goals.", "danger");
  }
}

/**
 * Opens Goal Modal in Add mode
 */
function openGoalModal() {
  document.getElementById("goalModalTitle").textContent = "Create Savings Goal";
  document.getElementById("goalId").value = "";
  document.getElementById("goalForm").reset();

  // Default target date to 6 months in future
  const d = new Date();
  d.setMonth(d.getMonth() + 6);
  document.getElementById("goalTargetDate").value = d.toISOString().split("T")[0];

  document.getElementById("goalModal").style.display = "flex";
}

/**
 * Closes Goal Modal
 */
function closeGoalModal() {
  document.getElementById("goalModal").style.display = "none";
}

/**
 * Populates Goal Modal for editing
 */
function editGoalRecord(id) {
  const item = allGoalsCache.find(x => x.id === id);
  if (!item) return;

  document.getElementById("goalModalTitle").textContent = "Edit Savings Goal";
  document.getElementById("goalId").value = item.id;
  document.getElementById("goalName").value = item.name;
  document.getElementById("goalTargetAmount").value = item.target_amount;
  document.getElementById("goalCurrentAmount").value = item.current_amount;
  document.getElementById("goalTargetDate").value = item.target_date;

  document.getElementById("goalModal").style.display = "flex";
}

/**
 * Submits Add or Edit Goal form
 */
async function submitGoalForm(e) {
  e.preventDefault();
  const id = document.getElementById("goalId").value;
  const name = document.getElementById("goalName").value.trim();
  const target_amount = parseFloat(document.getElementById("goalTargetAmount").value);
  const current_amount = parseFloat(document.getElementById("goalCurrentAmount").value || 0);
  const target_date = document.getElementById("goalTargetDate").value;

  const saveBtn = document.getElementById("goalSaveBtn");
  saveBtn.disabled = true;

  const payload = { name, target_amount, current_amount, target_date };
  const method = id ? "PUT" : "POST";
  const url = id ? `/api/goals/${id}` : "/api/goals";

  try {
    const res = await fetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to save savings goal.");

    closeGoalModal();
    showToast(data.message || "Savings goal saved.", "success");
    loadGoalsList();
    if (typeof loadDashboardData === "function") loadDashboardData();
  } catch (err) {
    showToast(err.message, "danger");
  } finally {
    saveBtn.disabled = false;
  }
}

/**
 * Opens Quick Deposit Modal
 */
function openDepositModal(id) {
  const goal = allGoalsCache.find(x => x.id === id);
  if (!goal) return;

  document.getElementById("depositGoalId").value = goal.id;
  document.getElementById("depositGoalPrompt").textContent = 
    `Deposit funds toward "${goal.name}". Currently saved: ${formatINR(goal.current_amount)} of ${formatINR(goal.target_amount)}.`;
  document.getElementById("depositAmount").value = "";

  document.getElementById("depositModal").style.display = "flex";
}

/**
 * Closes Quick Deposit Modal
 */
function closeDepositModal() {
  document.getElementById("depositModal").style.display = "none";
}

/**
 * Handles Deposit submission (adds to current saved amount)
 */
async function submitDepositForm(e) {
  e.preventDefault();
  const goalId = document.getElementById("depositGoalId").value;
  const depositAmt = parseFloat(document.getElementById("depositAmount").value);

  const goal = allGoalsCache.find(x => x.id == goalId);
  if (!goal) return;

  const updatedCurrent = goal.current_amount + depositAmt;

  try {
    const res = await fetch(`/api/goals/${goalId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ current_amount: updatedCurrent })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to record deposit.");

    closeDepositModal();
    showToast(`Added ${formatINR(depositAmt)} deposit to "${goal.name}".`, "success");
    loadGoalsList();
    if (typeof loadDashboardData === "function") loadDashboardData();
  } catch (err) {
    showToast(err.message, "danger");
  }
}

/**
 * Deletes a savings goal
 */
async function deleteGoalRecord(id) {
  if (!confirm("Are you sure you want to delete this savings goal?")) return;

  try {
    const res = await fetch(`/api/goals/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to delete goal.");

    showToast("Savings goal deleted.", "success");
    loadGoalsList();
    if (typeof loadDashboardData === "function") loadDashboardData();
  } catch (err) {
    showToast(err.message, "danger");
  }
}
