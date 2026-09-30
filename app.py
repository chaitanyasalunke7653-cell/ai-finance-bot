import os
import sys
import io

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
elif hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from flask import Flask, render_template
from flask_cors import CORS
from config import Config
from models import db
from routes import (
    web_bp,
    auth_bp,
    dashboard_bp,
    income_bp,
    expenses_bp,
    budgets_bp,
    goals_bp,
    ai_bp
)

def create_app(config_class=Config) -> Flask:
    """Application factory for Personal Finance Advisor Bot."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Initialize database
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(income_bp, url_prefix="/api")
    app.register_blueprint(expenses_bp, url_prefix="/api")
    app.register_blueprint(budgets_bp, url_prefix="/api")
    app.register_blueprint(goals_bp, url_prefix="/api")
    app.register_blueprint(ai_bp, url_prefix="/api")

    # Template filters
    @app.template_filter("currency_inr")
    def currency_inr(value):
        try:
            val = float(value)
            # Format in Indian Rupee format with ₹
            return f"₹{val:,.2f}"
        except (ValueError, TypeError):
            return "₹0.00"

    # Context processor for global template variables
    @app.context_processor
    def inject_globals():
        return {
            "app_name": "Personal Finance Advisor Bot",
            "currency_symbol": "₹",
            "current_year": 2026
        }

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("500.html"), 500

    # Ensure tables are created
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    print(f"Personal Finance Advisor Bot starting on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
