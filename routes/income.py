from datetime import datetime, date
from flask import Blueprint, request, jsonify, session
from models import db, Income
from routes.auth import login_required
from sqlalchemy import extract

income_bp = Blueprint("income", __name__)

@income_bp.route("/income", methods=["GET"])
@login_required
def get_incomes():
    user_id = session.get("user_id")
    month_param = request.args.get("month")

    query = Income.query.filter_by(user_id=user_id)

    if month_param:
        try:
            year, month = map(int, month_param.split("-"))
            query = query.filter(
                extract("year", Income.date) == year,
                extract("month", Income.date) == month
            )
        except ValueError:
            return jsonify({"error": "Invalid month format. Expected YYYY-MM."}), 400

    incomes = query.order_by(Income.date.desc(), Income.id.desc()).all()
    return jsonify([inc.to_dict() for inc in incomes]), 200

@income_bp.route("/income", methods=["POST"])
@login_required
def create_income():
    user_id = session.get("user_id")
    data = request.get_json() or {}

    amount = data.get("amount")
    source = data.get("source", "").strip()
    date_str = data.get("date")
    description = data.get("description", "").strip()

    if amount is None or not source or not date_str:
        return jsonify({"error": "Amount, source, and date are required fields."}), 400

    try:
        amount_val = float(amount)
        if amount_val <= 0:
            return jsonify({"error": "Income amount must be greater than zero."}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Amount must be a valid number."}), 400

    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD."}), 400

    try:
        new_income = Income(
            user_id=user_id,
            amount=amount_val,
            source=source,
            date=parsed_date,
            description=description
        )
        db.session.add(new_income)
        db.session.commit()
        return jsonify({"message": "Income recorded successfully", "income": new_income.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to record income: {str(e)}"}), 500

@income_bp.route("/income/<int:id>", methods=["PUT"])
@login_required
def update_income(id: int):
    user_id = session.get("user_id")
    income = Income.query.filter_by(id=id, user_id=user_id).first()

    if not income:
        return jsonify({"error": "Income record not found."}), 404

    data = request.get_json() or {}

    if "amount" in data:
        try:
            amt = float(data["amount"])
            if amt <= 0:
                return jsonify({"error": "Amount must be greater than zero."}), 400
            income.amount = amt
        except (ValueError, TypeError):
            return jsonify({"error": "Amount must be a valid number."}), 400

    if "source" in data and data["source"].strip():
        income.source = data["source"].strip()

    if "date" in data:
        try:
            income.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD."}), 400

    if "description" in data:
        income.description = data["description"].strip()

    try:
        db.session.commit()
        return jsonify({"message": "Income updated successfully", "income": income.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update income: {str(e)}"}), 500

@income_bp.route("/income/<int:id>", methods=["DELETE"])
@login_required
def delete_income(id: int):
    user_id = session.get("user_id")
    income = Income.query.filter_by(id=id, user_id=user_id).first()

    if not income:
        return jsonify({"error": "Income record not found."}), 404

    try:
        db.session.delete(income)
        db.session.commit()
        return jsonify({"message": "Income record deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete income: {str(e)}"}), 500
