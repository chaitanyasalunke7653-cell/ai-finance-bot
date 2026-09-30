from flask import Blueprint, render_template, session, redirect, url_for
from models import User
from routes.auth import login_required

web_bp = Blueprint("web", __name__)

@web_bp.route("/")
def landing_page():
    return render_template("index.html")

@web_bp.route("/login")
def login_page():
    if "user_id" in session:
        return redirect(url_for("web.dashboard_page"))
    return render_template("login.html")

@web_bp.route("/register")
def register_page():
    if "user_id" in session:
        return redirect(url_for("web.dashboard_page"))
    return render_template("register.html")

@web_bp.route("/dashboard")
@login_required
def dashboard_page():
    user = User.query.get(session["user_id"])
    return render_template("dashboard.html", user=user)

@web_bp.route("/privacy")
def privacy_page():
    return render_template("privacy.html")

@web_bp.route("/terms")
def terms_page():
    return render_template("terms.html")
