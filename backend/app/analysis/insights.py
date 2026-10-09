"""
Advanced statistical & ML insights for expenses and habits.
"""
from __future__ import annotations

from datetime import date, timedelta
from collections import defaultdict
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sqlalchemy.orm import Session

from ..models import Expense, Category, Habit, HabitLog


def expenses_to_df(db: Session) -> pd.DataFrame:
    rows = (
        db.query(
            Expense.id,
            Expense.amount,
            Expense.description,
            Expense.date,
            Expense.notes,
            Category.name.label("category"),
            Category.color.label("color"),
        )
        .join(Category)
        .all()
    )
    if not rows:
        return pd.DataFrame(
            columns=["id", "amount", "description", "date", "notes", "category", "color"]
        )
    df = pd.DataFrame(rows, columns=["id", "amount", "description", "date", "notes", "category", "color"])
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["weekday"] = df["date"].dt.day_name()
    df["day"] = df["date"].dt.day
    return df


def monthly_summary(db: Session, months: int = 12) -> list[dict]:
    df = expenses_to_df(db)
    if df.empty:
        return []

    cutoff = pd.Timestamp.now() - pd.DateOffset(months=months)
    df = df[df["date"] >= cutoff]

    result = []
    for month, group in df.groupby("month"):
        by_cat = group.groupby("category")["amount"].sum().to_dict()
        result.append(
            {
                "month": month,
                "total": round(float(group["amount"].sum()), 2),
                "count": int(len(group)),
                "by_category": {k: round(v, 2) for k, v in by_cat.items()},
            }
        )
    return sorted(result, key=lambda x: x["month"])


def predict_next_month(db: Session) -> dict:
    """Linear regression on *complete* monthly totals only.

    The current (possibly incomplete) month is excluded so the model
    is not biased downward by partial data.
    """
    summary = monthly_summary(db, months=18)
    current_month = pd.Timestamp.now().to_period("M").strftime("%Y-%m")

    # keep only fully completed months
    complete = [s for s in summary if s["month"] != current_month]

    if len(complete) < 3:
        # fallback: simple average of whatever we have
        if not complete:
            return {
                "next_month_estimate": 0.0,
                "confidence": "low",
                "method": "insufficient_data",
                "details": {"message": "Need at least 3 complete months of data"},
            }
        avg = sum(s["total"] for s in complete) / len(complete)
        return {
            "next_month_estimate": round(avg, 2),
            "confidence": "low",
            "method": "simple_average",
            "details": {
                "message": f"Only {len(complete)} complete month(s); using average",
                "months_used": len(complete),
            },
        }

    totals = [s["total"] for s in complete]
    X = np.arange(len(totals)).reshape(-1, 1)
    y = np.array(totals)

    model = LinearRegression()
    model.fit(X, y)
    next_pred = float(model.predict([[len(totals)]])[0])
    next_pred = max(0.0, next_pred)

    r2 = float(model.score(X, y))

    # more honest confidence: R² alone is weak with few points
    n = len(totals)
    if n >= 8 and r2 > 0.6:
        confidence = "high"
    elif n >= 5 and r2 > 0.35:
        confidence = "medium"
    else:
        confidence = "low"

    # simple residual-based uncertainty band
    residuals = y - model.predict(X)
    residual_std = float(np.std(residuals)) if len(residuals) > 1 else 0.0

    return {
        "next_month_estimate": round(next_pred, 2),
        "confidence": confidence,
        "method": "linear_regression",
        "details": {
            "r2_score": round(r2, 3),
            "slope": round(float(model.coef_[0]), 2),
            "months_used": n,
            "excluded_current_month": current_month,
            "approx_uncertainty": round(residual_std, 2),
            "last_months": totals[-6:],
        },
    }


def detect_patterns(db: Session) -> list[dict]:
    """Rule + statistical pattern detection."""
    df = expenses_to_df(db)
    insights: list[dict] = []

    if df.empty:
        return [
            {
                "type": "info",
                "title": "No data yet",
                "description": "Start logging expenses to unlock smart insights.",
                "severity": "info",
            }
        ]

    # 1. Weekday spending pattern
    weekday_avg = df.groupby("weekday")["amount"].mean().sort_values(ascending=False)
    top_day = weekday_avg.index[0]
    if weekday_avg.iloc[0] > weekday_avg.mean() * 1.4:
        insights.append(
            {
                "type": "weekday",
                "title": f"High spending on {top_day}s",
                "description": f"You spend on average {weekday_avg.iloc[0]:.0f} on {top_day}s — "
                f"{((weekday_avg.iloc[0] / weekday_avg.mean() - 1) * 100):.0f}% above average.",
                "severity": "warning",
            }
        )

    # 2. Category concentration
    cat_total = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    total = cat_total.sum()
    if total > 0:
        top_cat = cat_total.index[0]
        share = cat_total.iloc[0] / total
        if share > 0.45:
            insights.append(
                {
                    "type": "category",
                    "title": f"Heavy focus on «{top_cat}»",
                    "description": f"{share*100:.0f}% of your money goes to {top_cat}. "
                    "Consider reviewing this category.",
                    "severity": "warning",
                }
            )
        else:
            insights.append(
                {
                    "type": "category",
                    "title": "Balanced categories",
                    "description": f"Your top category ({top_cat}) is only {share*100:.0f}% — good diversity.",
                    "severity": "success",
                }
            )

    # 3. Recent trend
    recent = df[df["date"] >= (pd.Timestamp.now() - pd.Timedelta(days=30))]
    prev = df[
        (df["date"] >= (pd.Timestamp.now() - pd.Timedelta(days=60)))
        & (df["date"] < (pd.Timestamp.now() - pd.Timedelta(days=30)))
    ]
    if not recent.empty and not prev.empty:
        recent_sum = recent["amount"].sum()
        prev_sum = prev["amount"].sum()
        change = (recent_sum - prev_sum) / prev_sum * 100 if prev_sum else 0
        if change > 25:
            insights.append(
                {
                    "type": "trend",
                    "title": "Spending increased this month",
                    "description": f"You spent {change:.0f}% more in the last 30 days compared to the previous period.",
                    "severity": "warning",
                }
            )
        elif change < -15:
            insights.append(
                {
                    "type": "trend",
                    "title": "Great control this month!",
                    "description": f"Spending is down {abs(change):.0f}% compared to the previous 30 days.",
                    "severity": "success",
                }
            )

    # 4. Large single transactions
    if not df.empty:
        threshold = df["amount"].quantile(0.95)
        big = df[df["amount"] >= threshold]
        if len(big) > 0:
            insights.append(
                {
                    "type": "outliers",
                    "title": f"{len(big)} large transactions detected",
                    "description": f"Transactions above {threshold:.0f} stand out. Review them if unexpected.",
                    "severity": "info",
                }
            )

    return insights


def suggest_category(db: Session, description: str) -> str | None:
    """Naive Bayes + TF-IDF for auto-categorization suggestion."""
    df = expenses_to_df(db)
    if len(df) < 15:
        return None

    try:
        pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer(max_features=500, ngram_range=(1, 2))),
                ("clf", MultinomialNB()),
            ]
        )
        pipeline.fit(df["description"].fillna(""), df["category"])
        pred = pipeline.predict([description])[0]
        return str(pred)
    except Exception:
        return None


def habit_streak(db: Session, habit_id: int) -> dict:
    """Calculate current and longest consecutive daily streaks.

    Rules:
    - Only completed logs count
    - Current streak: consecutive days ending today or yesterday
    - Gaps break the streak
    - longest_streak is always >= current_streak
    """
    logs = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id == habit_id, HabitLog.completed == True)
        .order_by(HabitLog.date.desc())
        .all()
    )
    if not logs:
        return {"current_streak": 0, "longest_streak": 0, "total_completed": 0}

    dates = sorted({log.date for log in logs})
    total_completed = len(dates)

    # --- current streak ---
    today = date.today()
    dates_set = set(dates)

    # streak must end on today or yesterday (grace for not-yet-logged today)
    if today in dates_set:
        cursor = today
    elif (today - timedelta(days=1)) in dates_set:
        cursor = today - timedelta(days=1)
    else:
        current = 0
        # fall through to longest calculation
        current = 0
        cursor = None

    current = 0
    if cursor is not None:
        while cursor in dates_set:
            current += 1
            cursor -= timedelta(days=1)

    # --- longest streak ---
    longest = 1 if dates else 0
    temp = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            temp += 1
            longest = max(longest, temp)
        else:
            temp = 1

    # invariant: longest >= current
    longest = max(longest, current)

    return {
        "current_streak": current,
        "longest_streak": longest,
        "total_completed": total_completed,
    }


def overall_stats(db: Session) -> dict[str, Any]:
    df = expenses_to_df(db)
    if df.empty:
        return {
            "total_spent": 0,
            "avg_daily": 0,
            "transaction_count": 0,
            "top_category": None,
            "this_month": 0,
        }

    this_month = df[df["date"].dt.to_period("M") == pd.Timestamp.now().to_period("M")]
    return {
        "total_spent": round(float(df["amount"].sum()), 2),
        "avg_daily": round(float(df["amount"].sum() / max((df["date"].max() - df["date"].min()).days, 1)), 2),
        "transaction_count": int(len(df)),
        "top_category": df.groupby("category")["amount"].sum().idxmax(),  # highest spend, not frequency
        "this_month": round(float(this_month["amount"].sum()), 2),
    }