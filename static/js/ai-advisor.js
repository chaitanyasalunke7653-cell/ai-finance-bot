/**
 * Personal Finance Advisor Bot - Gemini AI Advisor Integration
 */

/**
 * Checks backend status for Gemini API Key configuration
 */
async function checkAiStatus() {
  const statusAlert = document.getElementById("aiStatusAlert");
  const settingsStatus = document.getElementById("settingsAiStatus");
  const settingsBadge = document.getElementById("settingsAiBadge");

  try {
    const res = await fetch("/api/ai/status");
    if (!res.ok) return;

    const data = await res.json();
    if (data.configured) {
      if (statusAlert) {
        statusAlert.className = "alert alert-success mb-4";
        statusAlert.innerHTML = `<strong>Gemini AI Active:</strong> Official Google GenAI SDK connected. Live financial analysis is ready.`;
        statusAlert.style.display = "block";
      }
      if (settingsStatus) settingsStatus.textContent = "Google Gemini SDK Configured & Authenticated";
      if (settingsBadge) {
        settingsBadge.className = "badge badge-success";
        settingsBadge.textContent = "Active";
      }
    } else {
      if (statusAlert) {
        statusAlert.className = "alert alert-warning mb-4";
        statusAlert.innerHTML = `<strong>Note:</strong> GEMINI_API_KEY is not configured in .env. Falling back to analytical rule-based financial algorithms.`;
        statusAlert.style.display = "block";
      }
      if (settingsStatus) settingsStatus.textContent = "No GEMINI_API_KEY detected in .env file.";
      if (settingsBadge) {
        settingsBadge.className = "badge badge-warning";
        settingsBadge.textContent = "Unconfigured";
      }
    }
  } catch (err) {
    console.error("Error checking AI status:", err);
  }
}

/**
 * Executes structured financial analysis using Gemini AI
 */
async function runAiAnalysis() {
  const btn = document.getElementById("runAiBtn");
  const btnText = document.getElementById("runAiBtnText");
  const container = document.getElementById("aiOutputContainer");

  btn.disabled = true;
  btnText.textContent = "Analyzing Spending Patterns...";

  container.innerHTML = `
    <div class="card p-4 text-center">
      <div style="font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-bottom: 0.5rem;">
        Reviewing Financial Records...
      </div>
      <p class="text-sm text-muted">
        Evaluating month-to-date inflows, category expenditures, and budget caps via Google Gemini AI SDK.
      </p>
    </div>
  `;

  try {
    const res = await fetch("/api/ai/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ month: currentSelectedMonth })
    });

    const result = await res.json();
    renderAiAnalysisResults(result);

    // Sync quick summary in dashboard overview card
    const overviewSummary = document.getElementById("aiQuickSummary");
    if (overviewSummary && result.insights && result.insights.summary) {
      overviewSummary.textContent = result.insights.summary;
    }
  } catch (err) {
    console.error("AI Analysis error:", err);
    container.innerHTML = `
      <div class="card p-4 text-center">
        <div class="text-danger font-bold mb-2">Analysis Temporarily Unavailable</div>
        <p class="text-muted text-sm">${escapeHtml(err.message || "Network error communicating with AI advisor service.")}</p>
        <button class="btn btn-secondary btn-sm mt-3" onclick="runAiAnalysis()">Retry Analysis</button>
      </div>
    `;
    showToast("Failed to complete AI financial review.", "danger");
  } finally {
    btn.disabled = false;
    btnText.textContent = "Run Gemini Financial Analysis";
  }
}

/**
 * Renders structured AI response components
 */
function renderAiAnalysisResults(result) {
  const container = document.getElementById("aiOutputContainer");
  if (!container) return;

  const insights = result.insights || {};
  const summary = insights.summary || "Analysis completed for current period.";
  const alerts = insights.overspending_alerts || [];
  const recs = insights.budget_recommendations || [];
  const savings = insights.savings_opportunities || [];
  const checklist = insights.action_checklist || [];
  const modelInfo = result.model_used ? `<span class="badge badge-info">${escapeHtml(result.model_used)}</span>` : "";

  let alertsHtml = alerts.map(a => `<li>${escapeHtml(a)}</li>`).join("");
  let recsHtml = recs.map(r => `<li>${escapeHtml(r)}</li>`).join("");
  let savingsHtml = savings.map(s => `<li>${escapeHtml(s)}</li>`).join("");
  let checklistHtml = checklist.map(c => `<li>${escapeHtml(c)}</li>`).join("");

  container.innerHTML = `
    <div class="ai-review-card">
      <div class="card-header d-flex justify-between align-center">
        <div>
          <h3 class="card-title">Executive Financial Assessment</h3>
          <span class="card-subtitle">Month: ${escapeHtml(currentSelectedMonth || "Current")}</span>
        </div>
        <div>${modelInfo}</div>
      </div>

      <div class="ai-summary-highlight">
        ${escapeHtml(summary)}
      </div>

      <div class="ai-section-grid">
        <!-- Overspending Warnings -->
        <div class="ai-sub-card">
          <h4 class="ai-sub-title text-danger">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            Overspending & High Burn
          </h4>
          <ul class="ai-list">
            ${alertsHtml || "<li>No significant overspending detected.</li>"}
          </ul>
        </div>

        <!-- Budget Recommendations -->
        <div class="ai-sub-card">
          <h4 class="ai-sub-title text-primary">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
            Budget Recalibrations
          </h4>
          <ul class="ai-list">
            ${recsHtml || "<li>Maintain current category limits.</li>"}
          </ul>
        </div>

        <!-- Savings Opportunities -->
        <div class="ai-sub-card">
          <h4 class="ai-sub-title text-success">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"></rect><line x1="6" y1="12" x2="18" y2="12"></line></svg>
            Savings Acceleration
          </h4>
          <ul class="ai-list">
            ${savingsHtml || "<li>Surplus funds can be deployed to active savings goals.</li>"}
          </ul>
        </div>

        <!-- Action Checklist -->
        <div class="ai-sub-card">
          <h4 class="ai-sub-title text-dark">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 11 12 14 22 4"></polyline><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>
            Weekly Action Steps
          </h4>
          <ul class="ai-list ai-checklist">
            ${checklistHtml || "<li>Continue recording daily transactions.</li>"}
          </ul>
        </div>
      </div>
    </div>
  `;

  showToast("Gemini financial analysis complete.", "success");
}
