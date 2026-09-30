/**
 * Personal Finance Advisor Bot - Expense Management
 */

let allExpensesCache = [];

/**
 * Loads user expenses with active month and category filters
 */
async function loadExpenseList() {
  const monthFilter = document.getElementById("expenseMonthFilter");
  const catFilter = document.getElementById("expenseCategoryFilter");

  const month = monthFilter ? monthFilter.value : currentSelectedMonth;
  const category = catFilter ? catFilter.value : "";

  const tbody = document.getElementById("expenseTableBody");
  const totalDisplay = document.getElementById("expenseViewTotal");

  if (!tbody) return;

  let url = `/api/expenses?month=${encodeURIComponent(month)}`;
  if (category) {
    url += `&category=${encodeURIComponent(category)}`;
  }

  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch expense records.");

    allExpensesCache = await res.json();
    let total = 0;

    if (allExpensesCache.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" class="text-center py-4 text-muted">No expense records found matching criteria.</td>
        </tr>
      `;
      if (totalDisplay) totalDisplay.textContent = formatINR(0);
      return;
    }

    let rowsHtml = "";
    allExpensesCache.forEach(exp => {
      total += exp.amount;
      rowsHtml += `
        <tr>
          <td>${formatDate(exp.date)}</td>
          <td><span class="badge badge-neutral">${escapeHtml(exp.category)}</span></td>
          <td class="text-muted">${escapeHtml(exp.description || "-")}</td>
          <td class="text-right font-bold text-danger">- ${formatINR(exp.amount)}</td>
          <td class="text-right">
            <button class="btn btn-outline btn-sm mr-2" onclick="editExpenseRecord(${exp.id})" title="Edit">
              Edit
            </button>
            <button class="btn btn-danger btn-sm" onclick="deleteExpenseRecord(${exp.id})" title="Delete">
              Delete
            </button>
          </td>
        </tr>
      `;
    });

    tbody.innerHTML = rowsHtml;
    if (totalDisplay) totalDisplay.textContent = formatINR(total);
  } catch (err) {
    console.error("Error loading expenses:", err);
    showToast("Failed to load expense records.", "danger");
  }
}

/**
 * Opens Expense Modal in Add mode
 */
function openExpenseModal() {
  document.getElementById("expenseModalTitle").textContent = "Record Expense";
  document.getElementById("expenseId").value = "";
  document.getElementById("expenseForm").reset();

  // Default to today
  const todayStr = new Date().toISOString().split("T")[0];
  document.getElementById("expenseDate").value = todayStr;

  document.getElementById("expenseModal").style.display = "flex";
}

/**
 * Closes Expense Modal
 */
function closeExpenseModal() {
  document.getElementById("expenseModal").style.display = "none";
}

/**
 * Populates modal for editing
 */
function editExpenseRecord(id) {
  const item = allExpensesCache.find(x => x.id === id);
  if (!item) return;

  document.getElementById("expenseModalTitle").textContent = "Edit Expense Record";
  document.getElementById("expenseId").value = item.id;
  document.getElementById("expenseCategory").value = item.category;
  document.getElementById("expenseAmount").value = item.amount;
  document.getElementById("expenseDate").value = item.date;
  document.getElementById("expenseDescription").value = item.description || "";

  document.getElementById("expenseModal").style.display = "flex";
}

/**
 * Submits Add / Edit expense form
 */
async function submitExpenseForm(e) {
  e.preventDefault();
  const id = document.getElementById("expenseId").value;
  const category = document.getElementById("expenseCategory").value;
  const amount = parseFloat(document.getElementById("expenseAmount").value);
  const dateVal = document.getElementById("expenseDate").value;
  const description = document.getElementById("expenseDescription").value.trim();

  const saveBtn = document.getElementById("expenseSaveBtn");
  saveBtn.disabled = true;

  const payload = { category, amount, date: dateVal, description };
  const method = id ? "PUT" : "POST";
  const url = id ? `/api/expenses/${id}` : "/api/expenses";

  try {
    const res = await fetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to save expense record.");

    closeExpenseModal();
    showToast(data.message || "Expense recorded successfully.", "success");
    loadExpenseList();
    if (typeof loadDashboardData === "function") loadDashboardData();
  } catch (err) {
    showToast(err.message, "danger");
  } finally {
    saveBtn.disabled = false;
  }
}

/**
 * Deletes expense record
 */
async function deleteExpenseRecord(id) {
  if (!confirm("Are you sure you want to delete this expense record?")) return;

  try {
    const res = await fetch(`/api/expenses/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to delete expense.");

    showToast("Expense record deleted.", "success");
    loadExpenseList();
    if (typeof loadDashboardData === "function") loadDashboardData();
  } catch (err) {
    showToast(err.message, "danger");
  }
}
