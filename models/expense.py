from datetime import datetime, date
from . import db

CATEGORIES = [
    "Food",
    "Rent",
    "Transport",
    "Education",
    "Healthcare",
    "Entertainment",
    "Shopping",
    "Utilities",
    "Other"
]

class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": float(self.amount),
            "category": self.category,
            "date": self.date.isoformat() if self.date else None,
            "description": self.description or "",
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return f"<Expense ₹{self.amount} ({self.category})>"
