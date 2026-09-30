from datetime import datetime
from flask import Blueprint, request, jsonify, session
from models import db, SavingsGoal
from routes.auth import login_required

goals_bp = Blueprint("goals", __name__)

@goals_bp.route("/goals", methods=["GET"])
@login_required
def get_goals():
    user_id = session.get("user_id")
    goals = SavingsGoal.query.filter_by(user_id=user_id).order_by(SavingsGoal.target_date.asc()).all()
    return jsonify([g.to_dict() for g in goals]), 200

@goals_bp.route("/goals", methods=["POST"])
@login_required
def create_goal():
    user_id = session.get("user_id")
    data = request.get_json() or {}

    name = data.get("name", "").strip()
    target_amount = data.get("target_amount")
    current_amount = data.get("current_amount", 0.0)
    target_date_str = data.get("target_date")

    if not name or target_amount is None or not target_date_str:
        return jsonify({"error": "Goal name, target amount, and target date are required."}), 400

    try:
        t_amt = float(target_amount)
        c_amt = float(current_amount)
        if t_amt <= 0:
            return jsonify({"error": "Target amount must be greater than zero."}), 400
        if c_amt < 0:
            return jsonify({"error": "Current amount cannot be negative."}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Amounts must be valid numbers."}), 400

    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD."}), 400

    try:
        goal = SavingsGoal(
            user_id=user_id,
            name=name,
            target_amount=t_amt,
            current_amount=c_amt,
            target_date=target_date
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify({"message": "Savings goal created successfully", "goal": goal.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create savings goal: {str(e)}"}), 500

@goals_bp.route("/goals/<int:id>", methods=["PUT"])
@login_required
def update_goal(id: int):
    user_id = session.get("user_id")
    goal = SavingsGoal.query.filter_by(id=id, user_id=user_id).first()

    if not goal:
        return jsonify({"error": "Savings goal not found."}), 404

    data = request.get_json() or {}

    if "name" in data and data["name"].strip():
        goal.name = data["name"].strip()

    if "target_amount" in data:
        try:
            t = float(data["target_amount"])
            if t <= 0:
                return jsonify({"error": "Target amount must be greater than zero."}), 400
            goal.target_amount = t
        except (ValueError, TypeError):
            return jsonify({"error": "Target amount must be a number."}), 400

    if "current_amount" in data:
        try:
            c = float(data["current_amount"])
            if c < 0:
                return jsonify({"error": "Current amount cannot be negative."}), 400
            goal.current_amount = c
        except (ValueError, TypeError):
            return jsonify({"error": "Current amount must be a number."}), 400

    if "target_date" in data:
        try:
            goal.target_date = datetime.strptime(data["target_date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD."}), 400

    try:
        db.session.commit()
        return jsonify({"message": "Savings goal updated successfully", "goal": goal.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update savings goal: {str(e)}"}), 500

@goals_bp.route("/goals/<int:id>", methods=["DELETE"])
@login_required
def delete_goal(id: int):
    user_id = session.get("user_id")
    goal = SavingsGoal.query.filter_by(id=id, user_id=user_id).first()

    if not goal:
        return jsonify({"error": "Savings goal not found."}), 404

    try:
        db.session.delete(goal)
        db.session.commit()
        return jsonify({"message": "Savings goal deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete savings goal: {str(e)}"}), 500
