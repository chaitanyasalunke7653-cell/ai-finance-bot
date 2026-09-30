from datetime import datetime, date
from typing import Dict, Any, List, Optional
from sqlalchemy import func, extract
from models import db, Income, Expense, Budget, SavingsGoal

class FinanceService:
    """
    Centralized financial calculations and data aggregation service.
    Ensures calculations are performed server-side with zero division errors handled safely.
    All figures are in Indian Rupees (INR - ₹).
    """

    @staticmethod
    def get_user_dashboard_summary(user_id: int, month_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculates all key metrics for the user dashboard.
        month_str format: "YYYY-MM". If omitted, defaults to current month.
        """
        now = datetime.now()
        target_month_str = month_str or now.strftime("%Y-%m")
        year, month = map(int, target_month_str.split("-"))

        # Incomes for the selected month
        month_incomes = Income.query.filter(
            Income.user_id == user_id,
            extract("year", Income.date) == year,
            extract("month", Income.date) == month
        ).all()
        total_income = round(sum(inc.amount for inc in month_incomes), 2)

        # Expenses for the selected month
        month_expenses = Expense.query.filter(
            Expense.user_id == user_id,
            extract("year", Expense.date) == year,
            extract("month", Expense.date) == month
        ).all()
        total_expenses = round(sum(exp.amount for exp in month_expenses), 2)

        # Savings and rate
        savings = round(total_income - total_expenses, 2)
        if total_income > 0:
            savings_percentage = round((savings / total_income) * 100, 1)
        else:
            savings_percentage = 0.0

        # Category spending breakdown
        category_spending_dict: Dict[str, float] = {}
        for exp in month_expenses:
            category_spending_dict[exp.category] = round(
                category_spending_dict.get(exp.category, 0.0) + exp.amount, 2
            )

        category_breakdown = []
        for cat, amt in sorted(category_spending_dict.items(), key=lambda x: x[1], reverse=True):
            pct = round((amt / total_expenses * 100), 1) if total_expenses > 0 else 0.0
            category_breakdown.append({
                "category": cat,
                "amount": amt,
                "percentage": pct
            })

        # Budgets for the month
        month_budgets = Budget.query.filter(
            Budget.user_id == user_id,
            Budget.month == target_month_str
        ).all()

        total_budget_limit = 0.0
        budget_items = []
        for b in month_budgets:
            cat_spent = category_spending_dict.get(b.category, 0.0)
            remaining = round(b.limit - cat_spent, 2)
            pct_used = round((cat_spent / b.limit * 100), 1) if b.limit > 0 else 0.0
            
            # Status badge
            if pct_used > 100:
                status = "exceeded"
            elif pct_used >= 80:
                status = "warning"
            else:
                status = "good"

            total_budget_limit += b.limit
            budget_items.append({
                "id": b.id,
                "category": b.category,
                "limit": b.limit,
                "spent": cat_spent,
                "remaining": remaining,
                "percentage_used": min(pct_used, 150.0),
                "actual_percentage": pct_used,
                "status": status
            })

        remaining_budget = round(total_budget_limit - total_expenses, 2) if total_budget_limit > 0 else 0.0

        # Active savings goals
        goals = SavingsGoal.query.filter(SavingsGoal.user_id == user_id).order_by(SavingsGoal.target_date.asc()).all()
        goals_data = [g.to_dict() for g in goals]

        # Recent transactions (latest 10 combined income + expenses)
        recent_incomes = [
            {
                "id": inc.id,
                "type": "income",
                "title": inc.source,
                "category": inc.source,
                "amount": inc.amount,
                "date": inc.date.isoformat(),
                "description": inc.description or ""
            }
            for inc in month_incomes
        ]
        recent_expenses = [
            {
                "id": exp.id,
                "type": "expense",
                "title": exp.category,
                "category": exp.category,
                "amount": exp.amount,
                "date": exp.date.isoformat(),
                "description": exp.description or ""
            }
            for exp in month_expenses
        ]

        all_transactions = sorted(recent_incomes + recent_expenses, key=lambda x: x["date"], reverse=True)[:10]

        # Historical monthly trends (past 6 months)
        trends = FinanceService.get_monthly_trends(user_id, count=6)

        return {
            "selected_month": target_month_str,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "savings": savings,
            "savings_percentage": savings_percentage,
            "total_budget_limit": round(total_budget_limit, 2),
            "remaining_budget": remaining_budget,
            "category_breakdown": category_breakdown,
            "budgets": budget_items,
            "savings_goals": goals_data,
            "recent_transactions": all_transactions,
            "monthly_trends": trends,
            "currency": "INR",
            "currency_symbol": "₹"
        }

    @staticmethod
    def get_monthly_trends(user_id: int, count: int = 6) -> Dict[str, Any]:
        """
        Fetches income and expense aggregates for the last `count` months.
        """
        now = datetime.now()
        months_labels = []
        months_keys = []

        # Generate month list backward from now
        curr_year = now.year
        curr_month = now.month
        for _ in range(count):
            months_keys.append(f"{curr_year:04d}-{curr_month:02d}")
            dt_obj = date(curr_year, curr_month, 1)
            months_labels.append(dt_obj.strftime("%b %Y"))
            curr_month -= 1
            if curr_month == 0:
                curr_month = 12
                curr_year -= 1

        months_keys.reverse()
        months_labels.reverse()

        incomes_by_month = {k: 0.0 for k in months_keys}
        expenses_by_month = {k: 0.0 for k in months_keys}

        # Query incomes
        all_incomes = Income.query.filter(Income.user_id == user_id).all()
        for inc in all_incomes:
            k = inc.date.strftime("%Y-%m")
            if k in incomes_by_month:
                incomes_by_month[k] += inc.amount

        # Query expenses
        all_expenses = Expense.query.filter(Expense.user_id == user_id).all()
        for exp in all_expenses:
            k = exp.date.strftime("%Y-%m")
            if k in expenses_by_month:
                expenses_by_month[k] += exp.amount

        return {
            "labels": months_labels,
            "income": [round(incomes_by_month[k], 2) for k in months_keys],
            "expense": [round(expenses_by_month[k], 2) for k in months_keys]
        }
