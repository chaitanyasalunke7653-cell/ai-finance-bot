from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from services.finance_service import FinanceService
from services.gemini_service import GeminiService

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/ai/status", methods=["GET"])
@login_required
def get_ai_status():
    """Checks whether the Gemini API key is configured."""
    return jsonify({
        "configured": GeminiService.is_configured(),
        "provider": "Google Gemini (Official SDK)"
    }), 200

@ai_bp.route("/ai/analyze", methods=["POST"])
@login_required
def analyze_finances():
    """
    Gathers user's financial summary and prompts Gemini AI for practical analysis.
    """
    user_id = session.get("user_id")
    data = request.get_json() or {}
    month_str = data.get("month")

    # Fetch live financial summary for the specified or current month
    financial_data = FinanceService.get_user_dashboard_summary(user_id=user_id, month_str=month_str)

    # Call Gemini Service
    ai_result = GeminiService.analyze_finances(financial_data)

    return jsonify(ai_result), 200
