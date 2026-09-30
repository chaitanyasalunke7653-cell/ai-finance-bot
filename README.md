# Personal Finance Advisor Bot

A production-ready, full-stack personal finance web application built with Python Flask, SQLite, and Google Gemini AI. Engineered specifically for tracking personal finances in Indian Rupees (INR - ₹) with server-side mathematical calculations, category budgeting, and structured AI financial audits.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Quick Start Installation](#quick-start-installation)
  - [Prerequisites](#prerequisites)
  - [Windows Setup](#windows-setup)
  - [Linux / macOS Setup](#linux--macos-setup)
- [Environment Configuration](#environment-configuration)
- [Database Initialization & Demo Data](#database-initialization--demo-data)
- [Running the Application](#running-the-application)
- [Running Verification Tests](#running-verification-tests)
- [Git Setup and GitHub Deployment](#git-setup-and-github-deployment)
- [Security & Architecture Practices](#security--architecture-practices)
- [Mandatory Financial Advisory Disclaimer](#mandatory-financial-advisory-disclaimer)

---

## Overview

Personal Finance Advisor Bot provides a self-hosted personal finance platform that puts user data privacy first. The application operates entirely on your local machine using SQLite, avoiding third-party analytics trackers, fake counters, or opaque automated trading.

Users can track monthly income streams, itemize categorized daily expenses in Indian Rupees, set monthly spending limits with automated overspending alerts, establish savings milestones, and request structured financial reviews powered by Google Gemini AI.

---

## Key Features

1. **Native Indian Currency (INR - ₹) Support**:
   - All monetary amounts, summaries, charts, and budget thresholds are formatted using standard Indian numbering and the ₹ symbol.
2. **Income Management**:
   - Record earnings from Salary, Freelance contracts, Business revenues, Dividends, and Rentals.
   - Filter records by month with full edit and delete capabilities.
3. **Categorized Expense Ledger**:
   - 9 predefined categories: Food, Rent, Transport, Education, Healthcare, Entertainment, Shopping, Utilities, and Other.
   - Server-side validation and monthly aggregation.
4. **Monthly Budget Planner**:
   - Set category-specific expenditure caps.
   - Visual progress indicators showing real-time threshold warnings (Normal, Warning >= 80%, Exceeded > 100%).
5. **Milestone Savings Goals**:
   - Define dedicated targets for Emergency Reserves, Tech Upgrades, Education, and Travel.
   - Quick deposit modal to add increments towards active targets.
6. **Gemini AI Financial Advisor**:
   - Integrates with the official Google GenAI SDK (`google-genai`).
   - Analyzes month-to-date spending distributions and returns structured, actionable recommendations.
   - Highlights high-burn categories and outlines weekly action steps.
   - Graceful offline fallback: If the API key is unconfigured or unavailable, deterministic analytical algorithms provide rule-based recommendations without crashing.
7. **Clean Enterprise UI Design**:
   - Free from purple gradients, pill-shaped buttons, emoji icons, fake reviews, or exaggerated marketing claims.
   - Clean, high-contrast Slate and Navy interface designed for clarity and desktop/mobile responsiveness.
   - Built-in Privacy Policy (`/privacy`) and Terms & Conditions (`/terms`) pages.

---

## Technology Stack

- **Backend**: Python 3.11+, Flask 3.1, Flask-SQLAlchemy 3.1, Flask-CORS, Werkzeug (Password Hashing)
- **Database**: SQLite3 (Local file-based storage at `instance/finance.db`)
- **AI Integration**: Official Google GenAI Python SDK (`google-genai`)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (ES6+), Chart.js (v4.4+)
- **Security**: PBKDF2-SHA256 password hashing, HttpOnly session cookies, parameter validation, environment secret isolation

---

## Project Structure

```text
c:\BFSI\
├── app.py                     # Flask application factory & entrypoint
├── config.py                  # Environment loader & SQLite configurations
├── seed.py                    # Database seeder with realistic Indian demo data
├── test_system.py             # Automated end-to-end integration test suite
├── requirements.txt           # Python dependency specifications
├── .env.example               # Template for environment configuration
├── .env                       # Local secret environment variables (Git-ignored)
├── .gitignore                 # Rules preventing secrets/caches from Git commits
├── models/                    # SQLAlchemy database models
│   ├── __init__.py            # Database instance initialization
│   ├── user.py                # User credentials & cascade relationships
│   ├── income.py              # Income stream model
│   ├── expense.py             # Categorized expense records
│   ├── budget.py              # Monthly category limits
│   └── savings_goal.py        # Milestone targets & progress
├── routes/                    # Flask REST API & Web Blueprints
│   ├── __init__.py            # Route aggregator
│   ├── auth.py                # Register, login, logout, session auth
│   ├── dashboard.py           # Dashboard aggregated statistics
│   ├── income.py              # Income CRUD endpoints
│   ├── expenses.py            # Expense CRUD endpoints
│   ├── budgets.py             # Budget planner endpoints
│   ├── goals.py               # Savings goals endpoints
│   ├── ai.py                  # Gemini AI analysis handler
│   └── web.py                 # HTML view routes (Dashboard, Landing, Legal)
├── services/                  # Business & mathematical logic layer
│   ├── __init__.py            # Service exporter
│   ├── finance_service.py     # Server-side calculations (zero-division safe)
│   └── gemini_service.py      # Google Gemini client with structured fallback
├── templates/                 # Server-rendered Jinja2 HTML templates
│   ├── base.html              # Common public layout (Header & Footer)
│   ├── index.html             # Product landing page
│   ├── login.html             # User login portal with Demo fill helper
│   ├── register.html          # New account registration form
│   ├── dashboard.html         # Main application dashboard shell
│   ├── privacy.html           # Comprehensive Privacy Policy
│   ├── terms.html             # Terms & Conditions with legal disclaimer
│   ├── 404.html               # 404 Not Found error template
│   └── 500.html               # 500 Server Error template
├── static/                    # Frontend client assets
│   ├── favicon.svg            # Crisp Rupee SVG favicon
│   ├── css/
│   │   └── style.css          # Professional financial stylesheet
│   └── js/
│       ├── app.js             # Global utilities, INR currency formatter, toasts
│       ├── dashboard.js       # Chart.js visualizer & KPI rendering
│       ├── income.js          # Income CRUD logic
│       ├── expenses.js        # Expense CRUD logic
│       ├── budgets.js         # Budget cards & limit comparisons
│       ├── goals.js           # Goals tracker & quick deposit logic
│       └── ai-advisor.js      # Gemini AI client integration
└── instance/
    └── finance.db             # Local SQLite database file (created automatically)
```

---

## Quick Start Installation

### Prerequisites

- Python 3.11 or higher installed on your system.
- Git (optional, for version control).

### Windows Setup

1. Open PowerShell or Command Prompt in the project folder:
   ```powershell
   cd c:\BFSI
   ```

2. Create a virtual environment:
   ```powershell
   py -m venv venv
   ```

3. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\activate
   ```

4. Install the required dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

5. Create your `.env` configuration file:
   ```powershell
   copy .env.example .env
   ```

### Linux / macOS Setup

1. Open Terminal in the project directory:
   ```bash
   cd personal-finance-advisor
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create your `.env` configuration file:
   ```bash
   cp .env.example .env
   ```

---

## Environment Configuration

Open the `.env` file in VS Code or your preferred text editor:

```env
# Flask Application Secret Key
SECRET_KEY=generate_a_random_secret_key_here

# Google Gemini API Key (Obtain from https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here

# Server Settings
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5000
```

> **Security Note:** The `.env` file is excluded from Git commits via `.gitignore`. Never share or commit your real API key.

---

## Database Initialization & Demo Data

The SQLite database file (`instance/finance.db`) is automatically generated the first time the application runs.

To populate realistic sample financial data in Indian Rupees (INR) for immediate testing, run the seed script:

```bash
# Windows
.\venv\Scripts\python.exe seed.py

# Linux / macOS
python seed.py
```

To reset and re-seed the demo account at any time:
```bash
python seed.py --reset
```

### Demo Login Credentials
- **Email:** `demo@example.com`
- **Password:** `DemoUser@123`

---

## Running the Application

Start the Flask development server:

```bash
# Windows
.\venv\Scripts\python.exe app.py

# Linux / macOS
python app.py
```

The application will be live at:
**http://127.0.0.1:5000**

- Open `http://127.0.0.1:5000` to view the landing page.
- Navigate to `http://127.0.0.1:5000/login` to sign in. Click **"Fill Demo Credentials"** for instant testing.
- View the full interactive dashboard at `http://127.0.0.1:5000/dashboard`.

---

## Running Verification Tests

To verify database operations, API routes, calculation logic, and Gemini integration, execute the automated test suite:

```bash
# Windows
.\venv\Scripts\python.exe test_system.py

# Linux / macOS
python test_system.py
```

All public pages, authentication states, CRUD endpoints, and AI analysis pipelines are tested automatically.

---

## Git Setup and GitHub Deployment

This project is completely GitHub-ready. Secret keys, database instances, and virtual environments are guarded by `.gitignore`.

1. Initialize a new Git repository:
   ```bash
   git init
   ```

2. Verify that sensitive files (`.env`, `instance/`, `venv/`) are ignored:
   ```bash
   git status
   ```

3. Stage and commit all files:
   ```bash
   git add .
   git commit -m "Initial commit: Complete Personal Finance Advisor Bot"
   ```

4. Link to your GitHub repository and push:
   ```bash
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/personal-finance-advisor.git
   git push -u origin main
   ```

---

## Security & Architecture Practices

- **Strict Server-Side Calculations:** All monetary totals, savings percentages, and budget overruns are computed directly in Python to prevent tampering from the frontend.
- **Data Isolation:** Every database query strictly filters by `user_id == session['user_id']`. Users cannot view or modify transactions belonging to other accounts.
- **Zero API Key Exposure:** The Google Gemini API key is loaded only inside Python backend services. It is never exposed in JavaScript, DOM attributes, or network responses.
- **Session Security:** Cookies use `HttpOnly` and `SameSite=Lax` flags to prevent cross-site token exfiltration.
- **Graceful Fault Tolerance:** If the Gemini API experiences network timeouts or rate limits, the application catches the error, serves structured rule-based recommendations, and continues running smoothly without crashing.

---

## Mandatory Financial Advisory Disclaimer

AI-generated summaries, budget suggestions, and calculations provided by Personal Finance Advisor Bot are for educational and personal planning purposes only. They do NOT constitute certified financial planning, tax guidance, investment recommendations, or legal financial advice.

This software does not execute financial transactions, trade securities, or access automated banking APIs. Always consult a certified financial advisor or chartered accountant before making significant financial commitments.
