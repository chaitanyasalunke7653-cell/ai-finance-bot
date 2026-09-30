/**
 * Personal Finance Advisor Bot - Core Application Utilities
 * Currency: Indian Rupee (INR - ₹)
 */

// Global State
let currentSelectedMonth = "";

// Initialize upon DOM load
document.addEventListener("DOMContentLoaded", () => {
  // Set default month to current YYYY-MM
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  currentSelectedMonth = `${year}-${month}`;

  const monthFilter = document.getElementById("monthFilter");
  if (monthFilter) {
    monthFilter.value = currentSelectedMonth;
  }

  // Pre-fill modal date pickers with today
  const todayStr = now.toISOString().split("T")[0];
  const incDate = document.getElementById("incomeDate");
  const expDate = document.getElementById("expenseDate");
  const budMonth = document.getElementById("budgetMonth");
  if (incDate) incDate.value = todayStr;
  if (expDate) expDate.value = todayStr;
  if (budMonth) budMonth.value = currentSelectedMonth;

  // Initial dashboard load
  if (typeof loadDashboardData === "function") {
    loadDashboardData();
  }
  if (typeof checkAiStatus === "function") {
    checkAiStatus();
  }
});

/**
 * Formats numeric values to Indian Rupee (₹) standard currency representation.
 * Example: 150000 -> "₹1,50,000.00"
 */
function formatINR(val) {
  const num = parseFloat(val);
  if (isNaN(num)) return "₹0.00";
  return "₹" + num.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

/**
 * Formats dates into readable format e.g. "15 Oct 2026"
 */
function formatDate(dateStr) {
  if (!dateStr) return "-";
  const parts = dateStr.split("-");
  if (parts.length !== 3) return dateStr;
  const d = new Date(parts[0], parts[1] - 1, parts[2]);
  return d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

/**
 * Toast notification dispatcher
 */
function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${escapeHtml(message)}</span>
    <button style="background:none;border:none;color:#94a3b8;cursor:pointer;margin-left:8px;" onclick="this.parentElement.remove()">&times;</button>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 4000);
}

/**
 * Escape HTML utility to prevent XSS in dynamic renders
 */
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Topbar Period Selector change handler
 */
function onPeriodChange() {
  const monthInput = document.getElementById("monthFilter");
  if (monthInput && monthInput.value) {
    currentSelectedMonth = monthInput.value;
    
    // Sync other month filters
    const incFilter = document.getElementById("incomeMonthFilter");
    const expFilter = document.getElementById("expenseMonthFilter");
    const budFilter = document.getElementById("budgetMonthFilter");
    if (incFilter) incFilter.value = currentSelectedMonth;
    if (expFilter) expFilter.value = currentSelectedMonth;
    if (budFilter) budFilter.value = currentSelectedMonth;

    // Reload active view
    const activeSection = document.querySelector(".view-section.active");
    if (activeSection) {
      const viewId = activeSection.id.replace("view-", "");
      refreshViewData(viewId);
    }
  }
}

/**
 * View switcher for navigation tabs
 */
function switchView(viewName) {
  // Update sidebar buttons
  document.querySelectorAll(".nav-button").forEach(btn => btn.classList.remove("active"));
  const targetBtn = document.getElementById(`nav-${viewName}`);
  if (targetBtn) targetBtn.classList.add("active");

  // Update section containers
  document.querySelectorAll(".view-section").forEach(sec => sec.classList.remove("active"));
  const targetSection = document.getElementById(`view-${viewName}`);
  if (targetSection) targetSection.classList.add("active");

  // Update header title
  const titles = {
    overview: "Dashboard Overview",
    income: "Income Management",
    expenses: "Expense Management",
    budgets: "Monthly Budget Planner",
    goals: "Savings Goals",
    ai: "Gemini AI Advisor",
    settings: "Account & System Configuration"
  };
  const heading = document.getElementById("pageHeading");
  if (heading && titles[viewName]) {
    heading.textContent = titles[viewName];
  }

  // Refresh view data
  refreshViewData(viewName);

  // Close mobile sidebar if open
  const sidebar = document.getElementById("appSidebar");
  if (sidebar) sidebar.classList.remove("open");
}

function refreshViewData(viewName) {
  if (viewName === "overview" && typeof loadDashboardData === "function") {
    loadDashboardData();
  } else if (viewName === "income" && typeof loadIncomeList === "function") {
    loadIncomeList();
  } else if (viewName === "expenses" && typeof loadExpenseList === "function") {
    loadExpenseList();
  } else if (viewName === "budgets" && typeof loadBudgetsList === "function") {
    loadBudgetsList();
  } else if (viewName === "goals" && typeof loadGoalsList === "function") {
    loadGoalsList();
  } else if (viewName === "settings" && typeof checkAiStatus === "function") {
    checkAiStatus();
  }
}

/**
 * Mobile sidebar toggle
 */
function toggleSidebar() {
  const sidebar = document.getElementById("appSidebar");
  if (sidebar) {
    sidebar.classList.toggle("open");
  }
}

/**
 * Logout handler
 */
async function handleLogout() {
  try {
    const res = await fetch("/api/auth/logout", { method: "POST" });
    if (res.ok) {
      window.location.href = "/login";
    } else {
      showToast("Failed to sign out.", "danger");
    }
  } catch (err) {
    showToast("Network error during sign out.", "danger");
  }
}
