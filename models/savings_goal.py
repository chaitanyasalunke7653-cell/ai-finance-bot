from datetime import datetime, date
from . import db

class SavingsGoal(db.Model):
    __tablename__ = "savings_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        target = float(self.target_amount)
        current = float(self.current_amount)
        pct = round((current / target * 100), 1) if target > 0 else 0.0
        remaining = max(0.0, target - current)
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "target_amount": target,
            "current_amount": current,
            "remaining_amount": remaining,
            "percentage_completed": min(pct, 100.0),
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return f"<SavingsGoal {self.name}: ₹{self.current_amount}/₹{self.target_amount}>"
