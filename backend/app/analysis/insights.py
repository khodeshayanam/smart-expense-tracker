"""
Statistical & ML insights for expenses and habits.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats
from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sqlalchemy.orm import Session

from ..models import Expense, Category, HabitLog

# Categories treated as income when tx_type is missing (legacy rows)
INCOME_CATEGORY_NAMES = {"salary / income", "salary", "income", "حقوق و درآمد", "حقوق", "درآمد"}


def expenses_to_df(db: Session, expenses_only: bool = True) -> pd.DataFrame:
    """Load expenses into a DataFrame.

    If expenses_only=True, income rows are excluded from spending analytics.
    """
    rows = (
        db.query(
            Expense.id,
            Expense.amount,
            Expense.description,
            Expense.date,
            Expense.notes,
            Expense.tx_type,
            Category.name.label("category"),
            Category.color.label("color"),
        )
        .join(Category)
        .all()
    )
    cols = ["id", "amount", "description", "date", "notes", "tx_type", "category", "color"]
    if not rows:
        return pd.DataFrame(columns=cols)

    df = pd.DataFrame(rows, columns=cols)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["weekday"] = df["date"].dt.day_name()
    df["day"] = df["date"].dt.day

    # Normalize legacy rows: missing/blank tx_type + salary category => income
    def _is_expense(row) -> bool:
        t = (row["tx_type"] or "expense").lower()
        if t == "income":
            return False
        if str(row["category"]).strip().lower() in INCOME_CATEGORY_NAMES:
            return False
        return True

    df["_is_expense"] = df.apply(_is_expense, axis=1)

    if expenses_only:
        df = df[df["_is_expense"]].copy()

    return df


def monthly_summary(db: Session, months: int = 12) -> list[dict]:
    df = expenses_to_df(db, expenses_only=True)
    if df.empty:
        return []

    months = max(1, min(int(months), 120))
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


def _month_index(month_str: str) -> int:
    """Convert 'YYYY-MM' to ordinal months since year 0."""
    y, m = month_str.split("-")
    return int(y) * 12 + int(m)


def predict_next_month(db: Session) -> dict:
    """Predict next month spend using complete months only.

    - Drops current incomplete month
    - Drops first month if it has fewer than half the median transaction count
      (guards against partial first-month seed data)
    - Uses calendar month index so gaps are preserved
    - Falls back to simple average when < 6 complete months
    - Reports a proper residual-based SE (ddof = n-2) when using regression
    """
    summary = monthly_summary(db, months=18)
    current_month = pd.Timestamp.now().to_period("M").strftime("%Y-%m")
    complete = [s for s in summary if s["month"] != current_month]

    if not complete:
        return {
            "next_month_estimate": 0.0,
            "confidence": "low",
            "method": "insufficient_data",
            "details": {"message": "Need at least some complete months of data"},
        }

    # Drop partial first month: if its count is < 50% of median count, exclude it
    if len(complete) >= 2:
        counts = [s["count"] for s in complete]
        med = float(np.median(counts))
        if complete[0]["count"] < max(med * 0.5, 3):
            complete = complete[1:]

    if len(complete) < 6:
        avg = sum(s["total"] for s in complete) / len(complete)
        return {
            "next_month_estimate": round(avg, 2),
            "confidence": "low",
            "method": "simple_average",
            "details": {
                "message": f"Only {len(complete)} complete month(s) (need 6+ for regression); using average",
                "months_used": len(complete),
                "last_months": [s["total"] for s in complete[-6:]],
            },
        }

    # Calendar-aware X so missing months keep their gap
    indices = np.array([_month_index(s["month"]) for s in complete], dtype=float)
    y = np.array([s["total"] for s in complete], dtype=float)
    X = (indices - indices.min()).reshape(-1, 1)  # relative month index

    model = LinearRegression()
    model.fit(X, y)

    next_x = float(X.max()) + 1.0
    next_pred = float(model.predict([[next_x]])[0])
    next_pred = max(0.0, next_pred)

    n = len(y)
    r2 = float(model.score(X, y))
    residuals = y - model.predict(X)
    # unbiased residual SE with n-2 degrees of freedom
    dof = max(n - 2, 1)
    residual_se = float(np.sqrt(np.sum(residuals ** 2) / dof))

    # leverage for the next point
    x_mean = float(X.mean())
    ssx = float(np.sum((X.flatten() - x_mean) ** 2)) or 1.0
    lev = 1.0 / n + ((next_x - x_mean) ** 2) / ssx
    # prediction SE (includes residual noise + parameter uncertainty)
    pred_se = residual_se * float(np.sqrt(1.0 + lev))
    t_crit = float(scipy_stats.t.ppf(0.975, dof)) if n > 2 else 1.96
    half_width = t_crit * pred_se

    if n >= 8 and r2 > 0.6:
        confidence = "high"
    elif n >= 6 and r2 > 0.35:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "next_month_estimate": round(next_pred, 2),
        "confidence": confidence,
        "method": "linear_regression",
        "details": {
            "r2_score": round(r2, 3),
            "slope": round(float(model.coef_[0]), 2),
            "months_used": n,
            "excluded_current_month": current_month,
            "approx_uncertainty": round(pred_se, 2),
            "prediction_interval_95": [
                round(max(0.0, next_pred - half_width), 2),
                round(next_pred + half_width, 2),
            ],
            "last_months": [round(float(v), 2) for v in y[-6:]],
        },
    }


def detect_patterns(db: Session) -> list[dict]:
    """Pattern detection with minimum-sample guards."""
    df = expenses_to_df(db, expenses_only=True)
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

    MIN_TX = 15  # global minimum before most insights fire
    n = len(df)

    # 1. Weekday pattern — need enough data and enough days represented
    if n >= MIN_TX and df["weekday"].nunique() >= 4:
        weekday_avg = df.groupby("weekday")["amount"].mean().sort_values(ascending=False)
        overall = float(weekday_avg.mean())
        if overall > 0 and weekday_avg.iloc[0] > overall * 1.5:
            top_day = weekday_avg.index[0]
            pct = (weekday_avg.iloc[0] / overall - 1) * 100
            # require at least 3 tx on that day
            if (df["weekday"] == top_day).sum() >= 3:
                insights.append(
                    {
                        "type": "weekday",
                        "title": f"High spending on {top_day}s",
                        "description": (
                            f"Average {weekday_avg.iloc[0]:.0f} on {top_day}s — "
                            f"{pct:.0f}% above the weekday average."
                        ),
                        "severity": "warning",
                    }
                )

    # 2. Category concentration
    if n >= MIN_TX:
        cat_total = df.groupby("category")["amount"].sum().sort_values(ascending=False)
        total = float(cat_total.sum())
        if total > 0:
            top_cat = cat_total.index[0]
            share = cat_total.iloc[0] / total
            if share > 0.45 and len(cat_total) >= 2:
                insights.append(
                    {
                        "type": "category",
                        "title": f"Heavy focus on «{top_cat}»",
                        "description": (
                            f"{share * 100:.0f}% of spending goes to {top_cat}. "
                            "Consider reviewing this category."
                        ),
                        "severity": "warning",
                    }
                )
            elif share <= 0.45:
                insights.append(
                    {
                        "type": "category",
                        "title": "Balanced categories",
                        "description": (
                            f"Top category ({top_cat}) is only {share * 100:.0f}% — good diversity."
                        ),
                        "severity": "success",
                    }
                )

    # 3. Recent trend — need enough transactions in both windows
    recent = df[df["date"] >= (pd.Timestamp.now() - pd.Timedelta(days=30))]
    prev = df[
        (df["date"] >= (pd.Timestamp.now() - pd.Timedelta(days=60)))
        & (df["date"] < (pd.Timestamp.now() - pd.Timedelta(days=30)))
    ]
    if len(recent) >= 5 and len(prev) >= 5:
        recent_sum = float(recent["amount"].sum())
        prev_sum = float(prev["amount"].sum())
        if prev_sum > 0:
            change = (recent_sum - prev_sum) / prev_sum * 100
            # cap absurd percentages from tiny bases
            if abs(change) < 500:
                if change > 25:
                    insights.append(
                        {
                            "type": "trend",
                            "title": "Spending increased recently",
                            "description": (
                                f"You spent {change:.0f}% more in the last 30 days "
                                "vs the previous 30 days."
                            ),
                            "severity": "warning",
                        }
                    )
                elif change < -15:
                    insights.append(
                        {
                            "type": "trend",
                            "title": "Great control recently!",
                            "description": (
                                f"Spending is down {abs(change):.0f}% vs the previous 30 days."
                            ),
                            "severity": "success",
                        }
                    )

    # 4. Outliers via IQR (robust) — not quantile which fails on identical values
    if n >= MIN_TX:
        q1 = float(df["amount"].quantile(0.25))
        q3 = float(df["amount"].quantile(0.75))
        iqr = q3 - q1
        if iqr > 0:
            threshold = q3 + 1.5 * iqr
            big = df[df["amount"] > threshold]
            if 0 < len(big) <= max(n * 0.15, 1):  # not "everything"
                insights.append(
                    {
                        "type": "outliers",
                        "title": f"{len(big)} large transaction(s) detected",
                        "description": (
                            f"Amounts above {threshold:.0f} stand out from the rest. "
                            "Review them if unexpected."
                        ),
                        "severity": "info",
                    }
                )

    if not insights and n < MIN_TX:
        insights.append(
            {
                "type": "info",
                "title": "Not enough data yet",
                "description": f"Log at least {MIN_TX} expenses to unlock pattern insights.",
                "severity": "info",
            }
        )

    return insights


def suggest_category(db: Session, description: str) -> str | None:
    """TF-IDF + Naive Bayes category suggestion (expenses only)."""
    df = expenses_to_df(db, expenses_only=True)
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
        proba = pipeline.predict_proba([description])[0]
        best_idx = int(np.argmax(proba))
        if proba[best_idx] < 0.35:
            return None  # not confident enough
        return str(pipeline.classes_[best_idx])
    except Exception:
        return None


def habit_streak(db: Session, habit_id: int) -> dict:
    """Current and longest consecutive daily streaks."""
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
    dates_set = set(dates)
    today = date.today()

    if today in dates_set:
        cursor = today
    elif (today - timedelta(days=1)) in dates_set:
        cursor = today - timedelta(days=1)
    else:
        cursor = None

    current = 0
    if cursor is not None:
        while cursor in dates_set:
            current += 1
            cursor -= timedelta(days=1)

    longest = 1 if dates else 0
    temp = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            temp += 1
            longest = max(longest, temp)
        else:
            temp = 1

    longest = max(longest, current)

    return {
        "current_streak": current,
        "longest_streak": longest,
        "total_completed": total_completed,
    }


def overall_stats(db: Session) -> dict[str, Any]:
    df = expenses_to_df(db, expenses_only=True)
    if df.empty:
        return {
            "total_spent": 0,
            "avg_daily": 0,
            "transaction_count": 0,
            "top_category": None,
            "this_month": 0,
        }

    span_days = (df["date"].max() - df["date"].min()).days + 1  # inclusive
    this_month = df[df["date"].dt.to_period("M") == pd.Timestamp.now().to_period("M")]
    return {
        "total_spent": round(float(df["amount"].sum()), 2),
        "avg_daily": round(float(df["amount"].sum() / max(span_days, 1)), 2),
        "transaction_count": int(len(df)),
        "top_category": df.groupby("category")["amount"].sum().idxmax(),
        "this_month": round(float(this_month["amount"].sum()), 2),
    }
