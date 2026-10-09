from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Category
from ..schemas import CategoryCreate, CategoryOut

router = APIRouter(prefix="/categories", tags=["Categories"])


DEFAULT_CATEGORIES = [
    {"name": "Food & Drink", "icon": "🍔", "color": "#ef4444"},
    {"name": "Transport", "icon": "🚗", "color": "#3b82f6"},
    {"name": "Shopping", "icon": "🛍️", "color": "#a855f7"},
    {"name": "Bills & Utilities", "icon": "💡", "color": "#f59e0b"},
    {"name": "Entertainment", "icon": "🎬", "color": "#ec4899"},
    {"name": "Health", "icon": "💊", "color": "#10b981"},
    {"name": "Education", "icon": "📚", "color": "#6366f1"},
    {"name": "Travel", "icon": "✈️", "color": "#06b6d4"},
    {"name": "Salary / Income", "icon": "💰", "color": "#22c55e"},
    {"name": "Other", "icon": "📦", "color": "#64748b"},
]


@router.post("/seed", response_model=list[CategoryOut])
def seed_categories(db: Session = Depends(get_db)):
    existing = {c.name for c in db.query(Category).all()}
    created = []
    for item in DEFAULT_CATEGORIES:
        if item["name"] not in existing:
            cat = Category(**item, is_system=True)
            db.add(cat)
            created.append(cat)
    db.commit()
    for c in created:
        db.refresh(c)
    return created


@router.get("/", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name).all()


@router.post("/", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    if db.query(Category).filter(Category.name == payload.name).first():
        raise HTTPException(400, "Category already exists")
    cat = Category(**payload.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat