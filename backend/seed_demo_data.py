"""
Seed realistic demo data so the dashboard looks impressive immediately.
Run: python -m seed_demo_data  (from backend folder)
"""
import random
from datetime import date, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal, init_db
from app.models import Category, Expense, Habit, HabitLog
from app.routers.categories import DEFAULT_CATEGORIES

random.seed(42)

DESCRIPTIONS = {
    "Food & Drink": [
        "Lunch at cafe", "Grocery shopping", "Coffee", "Dinner with friends",
        "Pizza delivery", "Breakfast", "Snacks", "Restaurant",
    ],
    "Transport": [
        "Uber ride", "Metro ticket", "Taxi", "Gas station", "Parking fee",
    ],
    "Shopping": [
        "Clothes", "Online order", "Electronics", "Shoes", "Gift",
    ],
    "Bills & Utilities": [
        "Electricity bill", "Internet", "Mobile credit", "Water bill",
    ],
    "Entertainment": [
        "Cinema ticket", "Spotify", "Game purchase", "Concert",
    ],
    "Health": [
        "Pharmacy", "Doctor visit", "Vitamins", "Gym membership",
    ],
    "Education": [
        "Online course", "Book", "Stationery", "Workshop fee",
    ],
    "Travel": [
        "Hotel booking", "Flight ticket", "Travel insurance",
    ],
    "Other": [
        "Miscellaneous", "Donation", "Repair",
    ],
}


def seed():
    init_db()
    db = SessionLocal()

    # Categories
    existing = {c.name: c for c in db.query(Category).all()}
    for item in DEFAULT_CATEGORIES:
        if item["name"] not in existing:
            cat = Category(**item, is_system=True)
            db.add(cat)
            db.flush()
            existing[item["name"]] = cat
    db.commit()

    # Clear old demo expenses (optional)
    if db.query(Expense).count() < 30:
        print("Seeding expenses...")
        today = date.today()
        for i in range(90):  # ~3 months
            d = today - timedelta(days=i)
            # 1-4 expenses per day
            for _ in range(random.randint(0, 3)):
                cat_name = random.choice(list(DESCRIPTIONS.keys()))
                cat = existing[cat_name]
                desc = random.choice(DESCRIPTIONS[cat_name])
                amount = round(random.uniform(50, 850) * random.choice([1, 1, 1, 2, 3]), 0)
                exp = Expense(
                    amount=amount,
                    description=desc,
                    date=d,
                    category_id=cat.id,
                    notes=None,
                )
                db.add(exp)
        db.commit()
        print(f"Created {db.query(Expense).count()} expenses")

    # Habits
    if db.query(Habit).count() == 0:
        print("Seeding habits...")
        habits_data = [
            {"name": "Morning Workout", "icon": "🏋️", "description": "30 min exercise"},
            {"name": "Read 20 pages", "icon": "📖", "description": "Daily reading habit"},
            {"name": "No junk food", "icon": "🥗", "description": "Stay healthy"},
            {"name": "Code 1 hour", "icon": "💻", "description": "Side project time"},
        ]
        for h in habits_data:
            habit = Habit(**h, target_frequency="daily")
            db.add(habit)
            db.flush()
            # log some history
            for i in range(25):
                d = date.today() - timedelta(days=i)
                if random.random() > 0.25:  # 75% completion
                    log = HabitLog(habit_id=habit.id, date=d, completed=True)
                    db.add(log)
        db.commit()
        print("Habits created with streaks")

    db.close()
    print("✅ Demo data ready!")


if __name__ == "__main__":
    seed()