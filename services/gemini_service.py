import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

DISCLAIMER_TEXT = (
    "AI-generated information is for educational and planning purposes and "
    "should not be considered professional financial advice."
)

class GeminiService:
    """
    Service wrapper for Google Gemini AI integration.
    Communicates via the official google-genai SDK.
    Never exposes API keys and handles network/rate-limit errors gracefully.
    """

    @staticmethod
    def get_api_key() -> str:
        return os.environ.get("GEMINI_API_KEY", "").strip()

    @staticmethod
    def is_configured() -> bool:
        key = GeminiService.get_api_key()
        return bool(key and key != "your_gemini_api_key_here")

    @classmethod
    def analyze_finances(cls, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends user financial summary to Gemini and extracts structured recommendations.
        Returns a dictionary with status, insights, and disclaimer.
        """
        if not cls.is_configured():
            logger.warning("Gemini API key is missing or not configured.")
            return {
                "success": False,
                "configured": False,
                "error": "Gemini API key is not configured. Please add GEMINI_API_KEY to your .env file to enable live AI analysis.",
                "disclaimer": DISCLAIMER_TEXT,
                "insights": cls._generate_fallback_insights(financial_data)
            }

        api_key = cls.get_api_key()

        # Build prompt
        prompt = cls._build_financial_prompt(financial_data)

        # Candidates to try in order of latency and availability
        models_to_try = [
            "gemini-3.5-flash-lite",
            "gemini-3.8-flash",
            "gemini-2.5-flash",
            "gemini-flash-latest"
        ]

        last_error = None

        try:
            from google import genai
            client = genai.Client(api_key=api_key)

            for model_name in models_to_try:
                try:
                    logger.info(f"Calling Gemini model: {model_name}")
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    
                    if response and response.text:
                        parsed = cls._parse_ai_response(response.text)
                        return {
                            "success": True,
                            "configured": True,
                            "model_used": model_name,
                            "insights": parsed,
                            "disclaimer": DISCLAIMER_TEXT
                        }
                except Exception as model_err:
                    last_error = str(model_err)
                    logger.warning(f"Failed with model {model_name}: {model_err}")
                    continue

            # If all model attempts failed
            return {
                "success": False,
                "configured": True,
                "error": f"Gemini API service temporarily unavailable: {last_error}",
                "disclaimer": DISCLAIMER_TEXT,
                "insights": cls._generate_fallback_insights(financial_data)
            }

        except ImportError:
            return {
                "success": False,
                "configured": True,
                "error": "google-genai SDK is not installed in the environment.",
                "disclaimer": DISCLAIMER_TEXT,
                "insights": cls._generate_fallback_insights(financial_data)
            }
        except Exception as e:
            logger.error(f"Unexpected error calling Gemini API: {e}", exc_info=True)
            return {
                "success": False,
                "configured": True,
                "error": f"An error occurred while connecting to AI advisor: {str(e)}",
                "disclaimer": DISCLAIMER_TEXT,
                "insights": cls._generate_fallback_insights(financial_data)
            }

    @staticmethod
    def _build_financial_prompt(data: Dict[str, Any]) -> str:
        """
        Builds a concise, structured prompt without marketing buzzwords.
        """
        income = data.get("total_income", 0.0)
        expenses = data.get("total_expenses", 0.0)
        savings = data.get("savings", 0.0)
        savings_pct = data.get("savings_percentage", 0.0)
        categories = data.get("category_breakdown", [])
        budgets = data.get("budgets", [])
        goals = data.get("savings_goals", [])

        cat_summary = ", ".join([f"{c['category']}: ₹{c['amount']} ({c['percentage']}%)" for c in categories]) or "None"
        budget_summary = ", ".join([f"{b['category']}: spent ₹{b['spent']} of ₹{b['limit']} limit ({b['actual_percentage']}%)" for b in budgets]) or "None set"
        goals_summary = ", ".join([f"{g['name']}: ₹{g['current_amount']}/₹{g['target_amount']} ({g['percentage_completed']}%)" for g in goals]) or "None"

        return f"""You are an objective, disciplined personal finance analytical assistant for users in India.
Currency: Indian Rupees (₹ - INR).

User Financial Data for Current Period:
- Total Income: ₹{income:,.2f}
- Total Expenses: ₹{expenses:,.2f}
- Net Savings: ₹{savings:,.2f}
- Savings Rate: {savings_pct}%
- Category Breakdown: {cat_summary}
- Budgets: {budget_summary}
- Active Savings Goals: {goals_summary}

Task:
Analyze this financial situation strictly and practically.
Do NOT use vague hype, fluff, or em-dashes.
Do NOT pretend to be a certified financial planner.
Return ONLY valid JSON matching this exact structure:
{{
  "summary": "2-3 sentences evaluating the current financial position realistically.",
  "overspending_alerts": [
    "Alert item 1 describing category overruns or high burn",
    "Alert item 2"
  ],
  "budget_recommendations": [
    "Concrete, realistic recommendation 1 with specific ₹ amounts",
    "Concrete, realistic recommendation 2 with specific ₹ amounts"
  ],
  "savings_opportunities": [
    "Tactical way to reduce discretionary expense 1",
    "Tactical way to accelerate savings goal progress"
  ],
  "action_checklist": [
    "Immediate step 1 to take this week",
    "Immediate step 2 to take this week"
  ]
}}
"""

    @classmethod
    def _parse_ai_response(cls, text: str) -> Dict[str, Any]:
        """
        Cleans and parses JSON output from Gemini response.
        """
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
            # Ensure standard keys exist
            return {
                "summary": data.get("summary", "Analysis completed based on current records."),
                "overspending_alerts": data.get("overspending_alerts", []),
                "budget_recommendations": data.get("budget_recommendations", []),
                "savings_opportunities": data.get("savings_opportunities", []),
                "action_checklist": data.get("action_checklist", [])
            }
        except json.JSONDecodeError:
            # Fallback if AI returned raw text instead of pure JSON
            return {
                "summary": cleaned[:300] + "...",
                "overspending_alerts": ["Review recurring expenses in your top spending categories."],
                "budget_recommendations": ["Establish monthly spending ceilings for discretionary categories."],
                "savings_opportunities": ["Automate monthly transfers to emergency fund immediately after salary credit."],
                "action_checklist": ["Review category allocations and maintain current record keeping."]
            }

    @staticmethod
    def _generate_fallback_insights(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic, rule-based financial analysis when Gemini API is unreachable or unconfigured.
        """
        income = data.get("total_income", 0.0)
        expenses = data.get("total_expenses", 0.0)
        savings = data.get("savings", 0.0)
        savings_pct = data.get("savings_percentage", 0.0)
        categories = data.get("category_breakdown", [])
        budgets = data.get("budgets", [])

        alerts = []
        recommendations = []
        savings_opps = []
        checklist = []

        if income == 0:
            summary = "No income has been recorded for this period. Add your salary or secondary earnings to calculate realistic savings ratios."
            checklist.append("Log your primary income source to activate full financial tracking.")
        elif expenses > income:
            summary = f"Expenses (₹{expenses:,.2f}) exceed income (₹{income:,.2f}), resulting in a deficit of ₹{abs(savings):,.2f}. Discretionary expenditures require immediate moderation."
            alerts.append(f"Spending exceeds total revenue by ₹{abs(savings):,.2f} this period.")
            checklist.append("Halt non-essential shopping and entertainment purchases until cash flow stabilizes.")
        else:
            summary = f"Total income stands at ₹{income:,.2f} with expenses at ₹{expenses:,.2f}, delivering a savings rate of {savings_pct}%. Your net savings is ₹{savings:,.2f}."
            if savings_pct < 20:
                recommendations.append("Aim for at least a 20% savings rate as recommended by standard 50/30/20 guidelines.")
            else:
                savings_opps.append(f"Healthy savings rate of {savings_pct}%. Allocate surplus toward long-term savings goals.")

        # Check category budget overruns
        for b in budgets:
            pct = b.get("actual_percentage", 0)
            cat = b.get("category", "")
            limit = b.get("limit", 0)
            spent = b.get("spent", 0)
            if pct > 100:
                alerts.append(f"Category '{cat}' is over budget by ₹{spent - limit:,.2f} ({pct}% of ₹{limit:,.2f} limit).")
            elif pct >= 80:
                alerts.append(f"Category '{cat}' has utilized {pct}% of its ₹{limit:,.2f} budget limit.")

        if categories:
            top_cat = categories[0]
            if top_cat["percentage"] > 35:
                recommendations.append(f"Top category '{top_cat['category']}' accounts for {top_cat['percentage']}% of total expenditures. Look for alternatives to lower this concentration.")

        if not checklist:
            checklist.append("Track every expense daily to keep category metrics accurate.")
            checklist.append("Review budget limits at the start of each calendar month.")

        return {
            "summary": summary,
            "overspending_alerts": alerts or ["No critical overspending detected based on current records."],
            "budget_recommendations": recommendations or ["Continue monitoring category allocations against set limits."],
            "savings_opportunities": savings_opps or ["Direct monthly surplus into your defined savings targets."],
            "action_checklist": checklist
        }
