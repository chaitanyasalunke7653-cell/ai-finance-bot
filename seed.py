import sys
import io

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
elif hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from datetime import date, timedelta
from app import create_app
from models import db, User, Income, Expense, Budget, SavingsGoal

def seed_database():
    app = create_app()
    with app.app_context():
        print("Initializing database tables...")
        db.create_all()

        demo_email = "demo@example.com"
        demo_password = "DemoUser@123"

        # Check if user already exists
        user = User.query.filter_by(email=demo_email).first()
        if user:
            print(f"Demo user '{demo_email}' already exists.")
            if "--reset" in sys.argv:
                print("Resetting existing demo user data...")
                db.session.delete(user)
                db.session.commit()
                user = None
            else:
                print("Skipping seed. Run 'python seed.py --reset' to clear and re-populate.")
                return

        if not user:
            print("Creating demo account...")
            user = User(
                name="Aarav Sharma",
                email=demo_email
            )
            user.set_password(demo_password)
            db.session.add(user)
            db.session.commit()
            print(f"Created demo user: {demo_email} (Password: {demo_password})")

        today = date.today()
        current_month = today.strftime("%Y-%m")

        # Previous month calculation
        first_of_this_month = date(today.year, today.month, 1)
        last_month_end = first_of_this_month - timedelta(days=1)
        prev_month = last_month_end.strftime("%Y-%m")

        print("Seeding monthly income records in INR (₹)...")
        incomes = [
            # Current Month Incomes
            Income(
                user_id=user.id,
                amount=85000.0,
                source="Salary",
                date=date(today.year, today.month, 1),
                description="Monthly Primary Employment Salary"
            ),
            Income(
                user_id=user.id,
                amount=18500.0,
                source="Freelance",
                date=date(today.year, today.month, 12) if today.day >= 12 else today,
                description="Web Development Consulting Contract"
            ),
            Income(
                user_id=user.id,
                amount=4200.0,
                source="Investment",
                date=date(today.year, today.month, 15) if today.day >= 15 else today,
                description="Quarterly Mutual Fund Dividend"
            ),
            # Previous Month Incomes
            Income(
                user_id=user.id,
                amount=85000.0,
                source="Salary",
                date=date(last_month_end.year, last_month_end.month, 1),
                description="Previous Month Salary"
            ),
            Income(
                user_id=user.id,
                amount=15000.0,
                source="Freelance",
                date=date(last_month_end.year, last_month_end.month, 18),
                description="Technical Writing Project"
            )
        ]
        db.session.add_all(incomes)

        print("Seeding realistic categorized expenses...")
        expenses = [
            # Current Month
            Expense(
                user_id=user.id,
                amount=22000.0,
                category="Rent",
                date=date(today.year, today.month, 2),
                description="Apartment Monthly Rent"
            ),
            Expense(
                user_id=user.id,
                amount=8400.0,
                category="Food",
                date=date(today.year, today.month, 5),
                description="Monthly Grocery & Pantry Restock"
            ),
            Expense(
                user_id=user.id,
                amount=3150.0,
                category="Food",
                date=date(today.year, today.month, 11) if today.day >= 11 else today,
                description="Weekend Family Dinner"
            ),
            Expense(
                user_id=user.id,
                amount=4200.0,
                category="Transport",
                date=date(today.year, today.month, 8),
                description="Metro Card Recharge & Fuel"
            ),
            Expense(
                user_id=user.id,
                amount=2800.0,
                category="Utilities",
                date=date(today.year, today.month, 7),
                description="Electricity & High-speed Broadband"
            ),
            Expense(
                user_id=user.id,
                amount=6200.0,
                category="Shopping",
                date=date(today.year, today.month, 14) if today.day >= 14 else today,
                description="Apparel and work footwear"
            ),
            Expense(
                user_id=user.id,
                amount=1800.0,
                category="Entertainment",
                date=date(today.year, today.month, 10),
                description="Streaming subscriptions & cinema"
            ),
            Expense(
                user_id=user.id,
                amount=2100.0,
                category="Healthcare",
                date=date(today.year, today.month, 16) if today.day >= 16 else today,
                description="Health checkup and supplements"
            ),
            # Previous Month
            Expense(
                user_id=user.id,
                amount=22000.0,
                category="Rent",
                date=date(last_month_end.year, last_month_end.month, 2),
                description="Previous Month Rent"
            ),
            Expense(
                user_id=user.id,
                amount=11500.0,
                category="Food",
                date=date(last_month_end.year, last_month_end.month, 12),
                description="Groceries and weekly dining"
            ),
            Expense(
                user_id=user.id,
                amount=4800.0,
                category="Transport",
                date=date(last_month_end.year, last_month_end.month, 14),
                description="Cab rides and public transit"
            )
        ]
        db.session.add_all(expenses)

        print("Seeding monthly budget limits...")
        budgets = [
            Budget(user_id=user.id, month=current_month, category="Rent", limit=22000.0),
            Budget(user_id=user.id, month=current_month, category="Food", limit=14000.0),
            Budget(user_id=user.id, month=current_month, category="Transport", limit=5000.0),
            Budget(user_id=user.id, month=current_month, category="Shopping", limit=8000.0),
            Budget(user_id=user.id, month=current_month, category="Utilities", limit=3500.0),
            Budget(user_id=user.id, month=current_month, category="Entertainment", limit=4000.0),
            Budget(user_id=user.id, month=current_month, category="Healthcare", limit=3000.0),
        ]
        db.session.add_all(budgets)

        print("Seeding savings goals...")
        goals = [
            SavingsGoal(
                user_id=user.id,
                name="Emergency Reserve Fund",
                target_amount=300000.0,
                current_amount=155000.0,
                target_date=date(today.year + 1, 3, 31)
            ),
            SavingsGoal(
                user_id=user.id,
                name="Workstation Laptop Upgrade",
                target_amount=95000.0,
                current_amount=62000.0,
                target_date=date(today.year, 11, 30)
            ),
            SavingsGoal(
                user_id=user.id,
                name="Annual Family Travel",
                target_amount=50000.0,
                current_amount=22500.0,
                target_date=date(today.year, 12, 25)
            )
        ]
        db.session.add_all(goals)

        db.session.commit()
        print("\nSeed completed successfully!")
        print(f"Login Credentials:")
        print(f"Email:    {demo_email}")
        print(f"Password: {demo_password}")
        print(f"Currency: INR (₹)")

if __name__ == "__main__":
    seed_database()
