"""
داده‌های نمونه برای نمایش داشبورد.
اجرا: python seed_demo_data.py
بازنشانی کامل: python seed_demo_data.py --reset
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
    "خوراک و نوشیدنی": ["ناهار رستوران", "خرید سوپرمارکت", "قهوه", "شام با دوستان", "پیتزا", "صبحانه", "تنقلات"],
    "حمل‌ونقل": ["اسنپ", "مترو", "تاکسی", "بنزین", "پارکینگ"],
    "خرید": ["لباس", "سفارش اینترنتی", "کفش", "هدیه"],
    "قبوض و خدمات": ["برق", "اینترنت", "شارژ موبایل", "آب"],
    "تفریح": ["سینما", "اشتراک موسیقی", "کنسرت", "بازی"],
    "سلامت": ["داروخانه", "ویزیت پزشک", "ویتامین", "باشگاه"],
    "آموزش": ["دوره آنلاین", "کتاب", "لوازم التحریر"],
    "سفر": ["هتل", "بلیط هواپیما", "بیمه سفر"],
    "سایر": ["متفرقه", "کمک مالی", "تعمیرات"],
}


def seed(reset: bool = False):
    init_db()
    db = SessionLocal()

    if reset:
        print("در حال پاک‌سازی داده‌ها...")
        db.query(HabitLog).delete()
        db.query(Habit).delete()
        db.query(Expense).delete()
        db.query(Category).delete()
        db.commit()

    existing = {c.name: c for c in db.query(Category).all()}
    for item in DEFAULT_CATEGORIES:
        if item["name"] not in existing:
            cat = Category(**item, is_system=True)
            db.add(cat)
            db.flush()
            existing[item["name"]] = cat
    db.commit()

    if db.query(Expense).count() == 0:
        print("در حال ساخت تراکنش‌های نمونه...")
        today = date.today()
        for i in range(90):
            d = today - timedelta(days=i)
            for _ in range(random.randint(0, 3)):
                cat_name = random.choice(list(DESCRIPTIONS.keys()))
                cat = existing[cat_name]
                desc = random.choice(DESCRIPTIONS[cat_name])
                amount = int(round(random.uniform(50000, 850000) * random.choice([1, 1, 1, 2]), 0))
                db.add(Expense(
                    amount=amount,
                    description=desc,
                    date=d,
                    category_id=cat.id,
                    notes=None,
                    tx_type="expense",
                ))
            if d.day == 1 and "حقوق و درآمد" in existing:
                db.add(Expense(
                    amount=25000000,
                    description="حقوق ماهانه",
                    date=d,
                    category_id=existing["حقوق و درآمد"].id,
                    notes=None,
                    tx_type="income",
                ))
        db.commit()
        print(f"{db.query(Expense).count()} تراکنش ساخته شد")

    if db.query(Habit).count() == 0:
        print("در حال ساخت عادت‌های نمونه...")
        habits_data = [
            {"name": "ورزش صبحگاهی", "icon": "🏋️", "description": "۳۰ دقیقه حرکت"},
            {"name": "مطالعه ۲۰ صفحه", "icon": "📖", "description": "عادت مطالعه روزانه"},
            {"name": "بدون فست‌فود", "icon": "🥗", "description": "غذای سالم"},
            {"name": "یک ساعت کدنویسی", "icon": "💻", "description": "پروژه شخصی"},
        ]
        for h in habits_data:
            habit = Habit(**h, target_frequency="daily")
            db.add(habit)
            db.flush()
            for i in range(25):
                d = date.today() - timedelta(days=i)
                if random.random() > 0.25:
                    db.add(HabitLog(habit_id=habit.id, date=d, completed=True))
        db.commit()
        print("عادت‌ها ساخته شدند")

    db.close()
    print("داده‌های نمونه آماده است.")


if __name__ == "__main__":
    seed(reset="--reset" in sys.argv)
