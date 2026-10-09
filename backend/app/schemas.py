from datetime import date as dt_date, datetime
import datetime as dt
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Literal
import re


# ──────────── Category ────────────
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    icon: str = "📦"
    color: str = "#6366f1"

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name cannot be empty or whitespace only")
        return v

    @field_validator("color")
    @classmethod
    def validate_hex_color(cls, v: str) -> str:
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", v):
            raise ValueError("color must be a valid hex like #6366f1")
        return v.lower()


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    id: int
    is_system: bool = False

    model_config = ConfigDict(from_attributes=True)


# ──────────── Expense ────────────
class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0, le=1_000_000_000)
    description: str = Field(..., min_length=1, max_length=255)
    date: dt_date
    category_id: int
    notes: Optional[str] = None

    @field_validator("description")
    @classmethod
    def strip_description(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("description cannot be empty or whitespace only")
        return v

    @field_validator("date")
    @classmethod
    def no_far_future(cls, v: dt_date) -> dt_date:
        from datetime import timedelta
        if v > dt_date.today() + timedelta(days=365):
            raise ValueError("date cannot be more than 1 year in the future")
        return v


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0, le=1_000_000_000)
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    date: Optional[dt_date] = None
    category_id: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("description")
    @classmethod
    def strip_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("description cannot be empty or whitespace only")
        return v

    @field_validator("date")
    @classmethod
    def no_far_future_update(cls, v: Optional[dt_date]) -> Optional[dt_date]:
        if v is None:
            return v
        from datetime import timedelta
        if v > dt_date.today() + timedelta(days=365):
            raise ValueError("date cannot be more than 1 year in the future")
        return v


class ExpenseOut(ExpenseBase):
    id: int
    created_at: datetime
    category: Optional[CategoryOut] = None

    model_config = ConfigDict(from_attributes=True)


# ──────────── Habit ────────────
class HabitBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = None
    target_frequency: Literal["daily", "weekly"] = "daily"
    icon: str = "✅"

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name cannot be empty or whitespace only")
        return v


class HabitCreate(HabitBase):
    pass


class HabitOut(HabitBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HabitLogCreate(BaseModel):
    habit_id: int
    date: dt_date
    completed: bool = True
    notes: Optional[str] = None

    @field_validator("date")
    @classmethod
    def no_future_log(cls, v: dt_date) -> dt_date:
        if v > dt_date.today():
            raise ValueError("cannot log habit for a future date")
        return v


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
