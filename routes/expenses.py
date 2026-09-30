from datetime import datetime, date
from flask import Blueprint, request, jsonify, session
from models import db, Expense
from models.expense import CATEGORIES
from routes.auth import login_required
from sqlalchemy import extract

expenses_bp = Blueprint("expenses", __name__)

@expenses_bp.route("/expenses", methods=["GET"])
@login_required
def get_expenses():
    user_id = session.get("user_id")
    month_param = request.args.get("month")
    category_param = request.args.get("category")

    query = Expense.query.filter_by(user_id=user_id)

    if month_param:
        try:
            year, month = map(int, month_param.split("-"))
            query = query.filter(
                extract("year", Expense.date) == year,
                extract("month", Expense.date) == month
            )
        except ValueError:
            return jsonify({"error": "Invalid month format. Expected YYYY-MM."}), 400

    if category_param and category_param in CATEGORIES:
        query = query.filter_by(category=category_param)

    expenses = query.order_by(Expense.date.desc(), Expense.id.desc()).all()
    return jsonify([exp.to_dict() for exp in expenses]), 200

@expenses_bp.route("/expenses", methods=["POST"])
@login_required
def create_expense():
    user_id = session.get("user_id")
    data = request.get_json() or {}

    amount = data.get("amount")
    category = data.get("category", "").strip()
    date_str = data.get("date")
    description = data.get("description", "").strip()

    if amount is None or not category or not date_str:
        return jsonify({"error": "Amount, category, and date are required fields."}), 400

    if category not in CATEGORIES:
        return jsonify({"error": f"Invalid category. Allowed: {', '.join(CATEGORIES)}"}), 400

    try:
        amount_val = float(amount)
        if amount_val <= 0:
            return jsonify({"error": "Expense amount must be greater than zero."}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Amount must be a valid number."}), 400

    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD."}), 400

    try:
        new_expense = Expense(
            user_id=user_id,
            amount=amount_val,
            category=category,
            date=parsed_date,
            description=description
        )
        db.session.add(new_expense)
        db.session.commit()
        return jsonify({"message": "Expense recorded successfully", "expense": new_expense.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to record expense: {str(e)}"}), 500

@expenses_bp.route("/expenses/<int:id>", methods=["PUT"])
@login_required
def update_expense(id: int):
    user_id = session.get("user_id")
    expense = Expense.query.filter_by(id=id, user_id=user_id).first()

    if not expense:
        return jsonify({"error": "Expense record not found."}), 404

    data = request.get_json() or {}

    if "amount" in data:
        try:
            amt = float(data["amount"])
            if amt <= 0:
                return jsonify({"error": "Amount must be greater than zero."}), 400
            expense.amount = amt
        except (ValueError, TypeError):
            return jsonify({"error": "Amount must be a valid number."}), 400

    if "category" in data:
        cat = data["category"].strip()
        if cat not in CATEGORIES:
            return jsonify({"error": f"Invalid category. Allowed: {', '.join(CATEGORIES)}"}), 400
        expense.category = cat

    if "date" in data:
        try:
            expense.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD."}), 400

    if "description" in data:
        expense.description = data["description"].strip()

    try:
        db.session.commit()
        return jsonify({"message": "Expense updated successfully", "expense": expense.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update expense: {str(e)}"}), 500

@expenses_bp.route("/expenses/<int:id>", methods=["DELETE"])
@login_required
def delete_expense(id: int):
    user_id = session.get("user_id")
    expense = Expense.query.filter_by(id=id, user_id=user_id).first()

    if not expense:
        return jsonify({"error": "Expense record not found."}), 404

    try:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({"message": "Expense record deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete expense: {str(e)}"}), 500
