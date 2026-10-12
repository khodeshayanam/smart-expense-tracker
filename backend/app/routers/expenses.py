from datetime import date
from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import Expense, Category
from ..schemas import ExpenseCreate, ExpenseUpdate, ExpenseOut
from ..analysis.insights import suggest_category

router = APIRouter(prefix="/expenses", tags=["Expenses"])


def _reload(db: Session, expense_id: int) -> Expense:
    return (
        db.query(Expense)
        .options(joinedload(Expense.category))
        .filter(Expense.id == expense_id)
        .first()
    )


@router.post("/", response_model=ExpenseOut, status_code=201)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    cat = db.get(Category, payload.category_id)
    if not cat:
        raise HTTPException(400, "Invalid category_id")

    # auto-mark salary category as income if client forgot
    data = payload.model_dump()
    if cat.name.strip().lower() in {"salary / income", "salary", "income", "حقوق و درآمد", "حقوق", "درآمد"}:
        data["tx_type"] = "income"

    expense = Expense(**data)
    db.add(expense)
    db.commit()
    return _reload(db, expense.id)


@router.get("/", response_model=list[ExpenseOut])
def list_expenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    tx_type: Optional[Literal["expense", "income"]] = None,
    db: Session = Depends(get_db),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(422, "start_date cannot be after end_date")

    q = db.query(Expense).options(joinedload(Expense.category))
    if category_id:
        q = q.filter(Expense.category_id == category_id)
    if start_date:
        q = q.filter(Expense.date >= start_date)
    if end_date:
        q = q.filter(Expense.date <= end_date)
    if tx_type:
        q = q.filter(Expense.tx_type == tx_type)
    return q.order_by(Expense.date.desc(), Expense.id.desc()).offset(skip).limit(limit).all()


@router.get("/suggest-category")
def auto_suggest_category(
    description: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
):
    suggestion = suggest_category(db, description)
    return {"suggested_category": suggestion}


@router.get("/{expense_id}", response_model=ExpenseOut)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = _reload(db, expense_id)
    if not expense:
        raise HTTPException(404, "Expense not found")
    return expense


@router.patch("/{expense_id}", response_model=ExpenseOut)
def update_expense(expense_id: int, payload: ExpenseUpdate, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(404, "Expense not found")

    data = payload.model_dump(exclude_unset=True)

    for field in ("amount", "description", "date", "category_id"):
        if field in data and data[field] is None:
            raise HTTPException(422, f"{field} cannot be null")

    if "category_id" in data:
        cat = db.get(Category, data["category_id"])
        if not cat:
            raise HTTPException(400, "Invalid category_id")

    for k, v in data.items():
        setattr(expense, k, v)

    db.commit()
    return _reload(db, expense.id)


@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(404, "Expense not found")
    db.delete(expense)
    db.commit()
