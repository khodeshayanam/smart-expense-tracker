from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# ──────────── Category ────────────
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    icon: str = "📦"
    color: str = "#6366f1"


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    id: int
    is_system: bool = False

    model_config = ConfigDict(from_attributes=True)


# ──────────── Expense ────────────
class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=255)
    date: date
    category_id: int
    notes: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    date: Optional[date] = None
    category_id: Optional[int] = None
    notes: Optional[str] = None


class ExpenseOut(ExpenseBase):
    id: int
    created_at: datetime
    category: Optional[CategoryOut] = None

    model_config = ConfigDict(from_attributes=True)


# ──────────── Habit ────────────
class HabitBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = None
    target_frequency: str = "daily"
    icon: str = "✅"


class HabitCreate(HabitBase):
    pass


class HabitOut(HabitBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HabitLogCreate(BaseModel):
    habit_id: int
    date: date
    completed: bool = True
    notes: Optional[str] = None


class HabitLogOut(HabitLogCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ──────────── Analytics responses ────────────
class MonthlySummary(BaseModel):
    month: str
    total: float
    count: int
    by_category: dict[str, float]


class PredictionResult(BaseModel):
    next_month_estimate: float
    confidence: str
    method: str
    details: dict


class PatternInsight(BaseModel):
    type: str
    title: str
    description: str
    severity: str  # info / warning / success