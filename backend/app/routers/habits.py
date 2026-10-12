from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Habit, HabitLog
from ..schemas import HabitCreate, HabitOut, HabitLogCreate, HabitLogOut
from ..analysis.insights import habit_streak

router = APIRouter(prefix="/habits", tags=["Habits"])


@router.post("/", response_model=HabitOut, status_code=201)
def create_habit(payload: HabitCreate, db: Session = Depends(get_db)):
    dup = (
        db.query(Habit)
        .filter(Habit.is_active == True, Habit.name == payload.name)
        .first()
    )
    if dup:
        raise HTTPException(400, "An active habit with this name already exists")
    habit = Habit(**payload.model_dump())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


@router.get("/", response_model=list[HabitOut])
def list_habits(active_only: bool = True, db: Session = Depends(get_db)):
    q = db.query(Habit)
    if active_only:
        q = q.filter(Habit.is_active == True)
    return q.order_by(Habit.created_at.desc()).all()


@router.get("/{habit_id}", response_model=HabitOut)
def get_habit(habit_id: int, db: Session = Depends(get_db)):
    habit = db.get(Habit, habit_id)
    if not habit or not habit.is_active:
        raise HTTPException(404, "Habit not found")
    return habit


@router.post("/log", response_model=HabitLogOut, status_code=201)
def log_habit(payload: HabitLogCreate, db: Session = Depends(get_db)):
    habit = db.get(Habit, payload.habit_id)
    if not habit:
        raise HTTPException(400, "Invalid habit_id")
    if not habit.is_active:
        raise HTTPException(400, "Habit is inactive")

    existing = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id == payload.habit_id, HabitLog.date == payload.date)
        .first()
    )
    if existing:
        data = payload.model_dump(exclude_unset=True)
        existing.completed = data.get("completed", existing.completed)
        if "notes" in data:
            existing.notes = data["notes"]
        db.commit()
        db.refresh(existing)
        return existing

    log = HabitLog(**payload.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/{habit_id}/streak")
def get_streak(habit_id: int, db: Session = Depends(get_db)):
    habit = db.get(Habit, habit_id)
    if not habit or not habit.is_active:
        raise HTTPException(404, "Habit not found")
    return habit_streak(db, habit_id)


@router.delete("/{habit_id}", status_code=204)
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    habit = db.get(Habit, habit_id)
    if not habit:
        raise HTTPException(404, "Habit not found")
    habit.is_active = False
    db.commit()