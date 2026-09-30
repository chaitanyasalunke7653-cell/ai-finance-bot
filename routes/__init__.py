from .auth import auth_bp, login_required
from .dashboard import dashboard_bp
from .income import income_bp
from .expenses import expenses_bp
from .budgets import budgets_bp
from .goals import goals_bp
from .ai import ai_bp
from .web import web_bp

__all__ = [
    "auth_bp",
    "dashboard_bp",
    "income_bp",
    "expenses_bp",
    "budgets_bp",
    "goals_bp",
    "ai_bp",
    "web_bp",
    "login_required"
]
