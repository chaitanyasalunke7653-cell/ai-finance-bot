from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from services.finance_service import FinanceService

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard", methods=["GET"])
@login_required
def get_dashboard():
    user_id = session.get("user_id")
    month_str = request.args.get("month")  # Optional "YYYY-MM"
    
    summary = FinanceService.get_user_dashboard_summary(user_id=user_id, month_str=month_str)
    return jsonify(summary), 200
