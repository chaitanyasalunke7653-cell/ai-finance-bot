from datetime import datetime
from flask import Blueprint, request, jsonify, session
from models import db, Budget, Expense
from models.expense import CATEGORIES
from routes.auth import login_required
from sqlalchemy import extract

budgets_bp = Blueprint("budgets", __name__)

@budgets_bp.route("/budgets", methods=["GET"])
@login_required
def get_budgets():
    user_id = session.get("user_id")
    month_param = request.args.get("month") or datetime.now().strftime("%Y-%m")

    budgets = Budget.query.filter_by(user_id=user_id, month=month_param).all()

    # Calculate actual spending for each category in this month
    try:
        year, month = map(int, month_param.split("-"))
    except ValueError:
        return jsonify({"error": "Invalid month format. Expected YYYY-MM."}), 400

    expenses = Expense.query.filter(
        Expense.user_id == user_id,
        extract("year", Expense.date) == year,
        extract("month", Expense.date) == month
    ).all()

    spending_by_category = {}
    for exp in expenses:
        spending_by_category[exp.category] = spending_by_category.get(exp.category, 0.0) + exp.amount

    result = []
    for b in budgets:
        spent = round(spending_by_category.get(b.category, 0.0), 2)
        remaining = round(b.limit - spent, 2)
        pct = round((spent / b.limit * 100), 1) if b.limit > 0 else 0.0
        
        status = "normal"
        if pct > 100:
            status = "exceeded"
        elif pct >= 80:
            status = "warning"

        item = b.to_dict()
        item.update({
            "spent": spent,
            "remaining": remaining,
            "percentage_used": pct,
            "status": status
        })
        result.append(item)

    return jsonify({
        "month": month_param,
        "budgets": result
    }), 200

@budgets_bp.route("/budgets", methods=["POST"])
@login_required
def create_or_update_budget():
    user_id = session.get("user_id")
    data = request.get_json() or {}

    month = data.get("month", "").strip()
    category = data.get("category", "").strip()
    limit = data.get("limit")

    if not month or not category or limit is None:
        return jsonify({"error": "Month (YYYY-MM), category, and limit are required."}), 400

    if category not in CATEGORIES and category != "Total":
        return jsonify({"error": f"Invalid category. Allowed: {', '.join(CATEGORIES)} or 'Total'"}), 400

    try:
        limit_val = float(limit)
        if limit_val <= 0:
            return jsonify({"error": "Budget limit must be greater than zero."}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Limit must be a valid number."}), 400

    # Upsert: If budget already exists for this user, month, and category, update limit
    existing = Budget.query.filter_by(user_id=user_id, month=month, category=category).first()
    try:
        if existing:
            existing.limit = limit_val
            db.session.commit()
            return jsonify({"message": "Budget limit updated successfully", "budget": existing.to_dict()}), 200
        else:
            budget = Budget(
                user_id=user_id,
                month=month,
                category=category,
                limit=limit_val
            )
            db.session.add(budget)
            db.session.commit()
            return jsonify({"message": "Budget limit set successfully", "budget": budget.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save budget: {str(e)}"}), 500

@budgets_bp.route("/budgets/<int:id>", methods=["PUT"])
@login_required
def update_budget(id: int):
    user_id = session.get("user_id")
    budget = Budget.query.filter_by(id=id, user_id=user_id).first()

    if not budget:
        return jsonify({"error": "Budget record not found."}), 404

    data = request.get_json() or {}

    if "limit" in data:
        try:
            lim = float(data["limit"])
            if lim <= 0:
                return jsonify({"error": "Limit must be greater than zero."}), 400
            budget.limit = lim
        except (ValueError, TypeError):
            return jsonify({"error": "Limit must be a valid number."}), 400

    try:
        db.session.commit()
        return jsonify({"message": "Budget updated successfully", "budget": budget.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update budget: {str(e)}"}), 500

@budgets_bp.route("/budgets/<int:id>", methods=["DELETE"])
@login_required
def delete_budget(id: int):
    user_id = session.get("user_id")
    budget = Budget.query.filter_by(id=id, user_id=user_id).first()

    if not budget:
        return jsonify({"error": "Budget record not found."}), 404

    try:
        db.session.delete(budget)
        db.session.commit()
        return jsonify({"message": "Budget limit deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete budget: {str(e)}"}), 500
