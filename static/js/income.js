/**
 * Personal Finance Advisor Bot - Income Management
 */

let allIncomesCache = [];

/**
 * Loads user incomes from API
 */
async function loadIncomeList() {
  const monthFilter = document.getElementById("incomeMonthFilter");
  const month = monthFilter ? monthFilter.value : currentSelectedMonth;

  const tbody = document.getElementById("incomeTableBody");
  const totalDisplay = document.getElementById("incomeViewTotal");

  if (!tbody) return;

  try {
    const res = await fetch(`/api/income?month=${encodeURIComponent(month)}`);
    if (!res.ok) throw new Error("Failed to fetch income data.");

    allIncomesCache = await res.json();
    let total = 0;

    if (allIncomesCache.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" class="text-center py-4 text-muted">No income records found for ${month || "all time"}.</td>
        </tr>
      `;
      if (totalDisplay) totalDisplay.textContent = formatINR(0);
      return;
    }

    let rowsHtml = "";
    allIncomesCache.forEach(inc => {
      total += inc.amount;
      rowsHtml += `
        <tr>
          <td>${formatDate(inc.date)}</td>
          <td><span class="badge badge-success">${escapeHtml(inc.source)}</span></td>
          <td class="text-muted">${escapeHtml(inc.description || "-")}</td>
          <td class="text-right font-bold text-success">+ ${formatINR(inc.amount)}</td>
          <td class="text-right">
            <button class="btn btn-outline btn-sm mr-2" onclick="editIncomeRecord(${inc.id})" title="Edit">
              Edit
            </button>
            <button class="btn btn-danger btn-sm" onclick="deleteIncomeRecord(${inc.id})" title="Delete">
              Delete
            </button>
          </td>
        </tr>
      `;
    });

    tbody.innerHTML = rowsHtml;
    if (totalDisplay) totalDisplay.textContent = formatINR(total);
  } catch (err) {
    console.error("Error loading income list:", err);
    showToast("Failed to load income records.", "danger");
  }
}

/**
 * Opens Income Modal in Add mode
 */
function openIncomeModal() {
  document.getElementById("incomeModalTitle").textContent = "Record Income";
  document.getElementById("incomeId").value = "";
  document.getElementById("incomeForm").reset();

  // Default to today
  const todayStr = new Date().toISOString().split("T")[0];
  document.getElementById("incomeDate").value = todayStr;

  document.getElementById("incomeModal").style.display = "flex";
}

/**
 * Closes Income Modal
 */
function closeIncomeModal() {
  document.getElementById("incomeModal").style.display = "none";
}

/**
 * Opens modal populated with existing record data
 */
function editIncomeRecord(id) {
  const item = allIncomesCache.find(x => x.id === id);
  if (!item) return;

  document.getElementById("incomeModalTitle").textContent = "Edit Income Record";
  document.getElementById("incomeId").value = item.id;
  document.getElementById("incomeSource").value = item.source;
  document.getElementById("incomeAmount").value = item.amount;
  document.getElementById("incomeDate").value = item.date;
  document.getElementById("incomeDescription").value = item.description || "";

  document.getElementById("incomeModal").style.display = "flex";
}

/**
 * Submits Add or Edit income form
 */
async function submitIncomeForm(e) {
  e.preventDefault();
  const id = document.getElementById("incomeId").value;
  const source = document.getElementById("incomeSource").value;
  const amount = parseFloat(document.getElementById("incomeAmount").value);
  const dateVal = document.getElementById("incomeDate").value;
  const description = document.getElementById("incomeDescription").value.trim();

  const saveBtn = document.getElementById("incomeSaveBtn");
  saveBtn.disabled = true;

  const payload = { source, amount, date: dateVal, description };
  const method = id ? "PUT" : "POST";
  const url = id ? `/api/income/${id}` : "/api/income";

  try {
    const res = await fetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to save income record.");

    closeIncomeModal();
    showToast(data.message || "Income recorded successfully.", "success");
    loadIncomeList();
    if (typeof loadDashboardData === "function") loadDashboardData();
  } catch (err) {
    showToast(err.message, "danger");
  } finally {
    saveBtn.disabled = false;
  }
}

/**
 * Deletes an income record after confirmation
 */
async function deleteIncomeRecord(id) {
  if (!confirm("Are you sure you want to delete this income record?")) return;

  try {
    const res = await fetch(`/api/income/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to delete income.");

    showToast("Income record deleted.", "success");
    loadIncomeList();
    if (typeof loadDashboardData === "function") loadDashboardData();
  } catch (err) {
    showToast(err.message, "danger");
  }
}
