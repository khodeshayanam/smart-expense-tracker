from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import Expense, Category
from ..schemas import ExpenseCreate, ExpenseUpdate, ExpenseOut
from ..analysis.insights import suggest_category

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/", response_model=ExpenseOut, status_code=201)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    cat = db.get(Category, payload.category_id)
    if not cat:
        raise HTTPException(400, "Invalid category_id")

    expense = Expense(**payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/", response_model=list[ExpenseOut])
def list_expenses(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Expense).options(joinedload(Expense.category))
    if category_id:
        q = q.filter(Expense.category_id == category_id)
    if start_date:
        q = q.filter(Expense.date >= start_date)
    if end_date:
        q = q.filter(Expense.date <= end_date)
    return q.order_by(Expense.date.desc()).offset(skip).limit(limit).all()


@router.get("/{expense_id}", response_model=ExpenseOut)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = (
        db.query(Expense)
        .options(joinedload(Expense.category))
        .filter(Expense.id == expense_id)
        .first()
    )
    if not expense:
        raise HTTPException(404, "Expense not found")
    return expense


@router.patch("/{expense_id}", response_model=ExpenseOut)
def update_expense(expense_id: int, payload: ExpenseUpdate, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(404, "Expense not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(expense, k, v)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(404, "Expense not found")
    db.delete(expense)
    db.commit()


@router.get("/suggest-category/")
def auto_suggest_category(description: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    suggestion = suggest_category(db, description)
    return {"suggested_category": suggestion}