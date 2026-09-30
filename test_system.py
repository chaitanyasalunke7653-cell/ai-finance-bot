import os
import sys
import io

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
elif hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from app import create_app
from models import db, User, Income, Expense, Budget, SavingsGoal

app = create_app()
client = app.test_client()

print("--- 1. Testing Public HTML Routes ---")
for path in ["/", "/login", "/register", "/privacy", "/terms"]:
    res = client.get(path)
    assert res.status_code == 200, f"Path {path} returned {res.status_code}"
    print(f"  GET {path} -> 200 OK")

print("\n--- 2. Testing Authentication ---")
# Register new test user
res = client.post("/api/auth/register", json={
    "name": "Priya Patel",
    "email": "priya@example.com",
    "password": "Password@123"
})
if res.status_code == 201:
    print("  POST /api/auth/register -> 201 Created")
elif res.status_code == 409:
    print("  POST /api/auth/register -> User already exists (409)")

# Login with Demo User
res = client.post("/api/auth/login", json={
    "email": "demo@example.com",
    "password": "DemoUser@123"
})
assert res.status_code == 200, f"Demo login failed: {res.data}"
print("  POST /api/auth/login -> 200 OK (Demo User Logged In)")

# Test Dashboard Protected Page
res = client.get("/dashboard")
assert res.status_code == 200, f"Dashboard page returned {res.status_code}"
print("  GET /dashboard -> 200 OK")

print("\n--- 3. Testing Dashboard API & Calculations ---")
res = client.get("/api/dashboard")
assert res.status_code == 200, f"Dashboard API failed: {res.data}"
data = res.get_json()
assert "total_income" in data
assert "total_expenses" in data
assert "savings" in data
assert "category_breakdown" in data
assert "budgets" in data
assert "savings_goals" in data
assert "monthly_trends" in data
print(f"  Monthly Income:   INR {data['total_income']:,.2f}")
print(f"  Monthly Expenses: INR {data['total_expenses']:,.2f}")
print(f"  Net Savings:      INR {data['savings']:,.2f} ({data['savings_percentage']}%)")
print(f"  Remaining Budget: INR {data['remaining_budget']:,.2f}")
print(f"  Categories Tracked: {len(data['category_breakdown'])}")

print("\n--- 4. Testing CRUD Operations ---")
# Income CRUD
res = client.post("/api/income", json={
    "amount": 12500.0,
    "source": "Freelance",
    "date": "2026-09-20",
    "description": "API Test Project"
})
assert res.status_code == 201, f"Create income failed: {res.data}"
inc_id = res.get_json()["income"]["id"]
print(f"  POST /api/income -> 201 Created (ID: {inc_id})")

res = client.put(f"/api/income/{inc_id}", json={"amount": 13000.0})
assert res.status_code == 200
print(f"  PUT /api/income/{inc_id} -> 200 OK")

res = client.delete(f"/api/income/{inc_id}")
assert res.status_code == 200
print(f"  DELETE /api/income/{inc_id} -> 200 OK")

# Expense CRUD
res = client.post("/api/expenses", json={
    "amount": 750.0,
    "category": "Food",
    "date": "2026-09-21",
    "description": "Lunch meeting"
})
assert res.status_code == 201, f"Create expense failed: {res.data}"
exp_id = res.get_json()["expense"]["id"]
print(f"  POST /api/expenses -> 201 Created (ID: {exp_id})")

res = client.put(f"/api/expenses/{exp_id}", json={"amount": 800.0})
assert res.status_code == 200
print(f"  PUT /api/expenses/{exp_id} -> 200 OK")

res = client.delete(f"/api/expenses/{exp_id}")
assert res.status_code == 200
print(f"  DELETE /api/expenses/{exp_id} -> 200 OK")

# Budget CRUD
res = client.post("/api/budgets", json={
    "month": "2026-09",
    "category": "Education",
    "limit": 6000.0
})
assert res.status_code in (200, 201), f"Save budget failed: {res.data}"
b_id = res.get_json()["budget"]["id"]
print(f"  POST /api/budgets -> 200/201 Saved (ID: {b_id})")

res = client.delete(f"/api/budgets/{b_id}")
assert res.status_code == 200
print(f"  DELETE /api/budgets/{b_id} -> 200 OK")

# Goals CRUD
res = client.post("/api/goals", json={
    "name": "Certification Course",
    "target_amount": 25000.0,
    "current_amount": 5000.0,
    "target_date": "2026-12-31"
})
assert res.status_code == 201, f"Create goal failed: {res.data}"
g_id = res.get_json()["goal"]["id"]
print(f"  POST /api/goals -> 201 Created (ID: {g_id})")

res = client.put(f"/api/goals/{g_id}", json={"current_amount": 10000.0})
assert res.status_code == 200
print(f"  PUT /api/goals/{g_id} -> 200 OK (Updated deposit)")

res = client.delete(f"/api/goals/{g_id}")
assert res.status_code == 200
print(f"  DELETE /api/goals/{g_id} -> 200 OK")

print("\n--- 5. Testing Gemini AI Advisor ---")
res = client.get("/api/ai/status")
assert res.status_code == 200
status_data = res.get_json()
print(f"  GET /api/ai/status -> {status_data}")

print("  Triggering live Gemini analysis (POST /api/ai/analyze)...")
res = client.post("/api/ai/analyze", json={})
assert res.status_code == 200
ai_data = res.get_json()
print(f"  AI Success: {ai_data.get('success')}")
if ai_data.get("model_used"):
    print(f"  Model Used: {ai_data.get('model_used')}")
print(f"  Disclaimer: {ai_data.get('disclaimer')}")
insights = ai_data.get("insights", {})
print(f"  Summary: {insights.get('summary')}")
print(f"  Overspending Alerts ({len(insights.get('overspending_alerts', []))}): {insights.get('overspending_alerts')[:2]}")
print(f"  Budget Recs ({len(insights.get('budget_recommendations', []))}): {insights.get('budget_recommendations')[:2]}")
print("\n--- 6. Testing Graceful Fallback without Gemini API Key ---")
from services.gemini_service import GeminiService
original_getter = GeminiService.get_api_key
GeminiService.get_api_key = staticmethod(lambda: "")
fallback_res = GeminiService.analyze_finances({
    "total_income": 50000.0,
    "total_expenses": 35000.0,
    "savings": 15000.0,
    "savings_percentage": 30.0,
    "category_breakdown": [{"category": "Food", "amount": 15000.0, "percentage": 42.9}],
    "budgets": [{"category": "Food", "spent": 15000.0, "limit": 12000.0, "actual_percentage": 125.0}],
    "savings_goals": []
})
assert fallback_res["success"] is False
assert "error" in fallback_res
assert "insights" in fallback_res
assert "disclaimer" in fallback_res
assert len(fallback_res["insights"]["overspending_alerts"]) > 0
print("  Graceful offline fallback returned valid insights without crashing.")
GeminiService.get_api_key = original_getter

print("\nALL AUTOMATED VERIFICATION TESTS PASSED SUCCESSFULLY!")
