from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Category
from ..schemas import CategoryCreate, CategoryOut, name_key

router = APIRouter(prefix="/categories", tags=["Categories"])


# دسته‌های پیش‌فرض فارسی
DEFAULT_CATEGORIES = [
    {"name": "خوراک و نوشیدنی", "icon": "🍔", "color": "#ef4444"},
    {"name": "حمل‌ونقل", "icon": "🚗", "color": "#3b82f6"},
    {"name": "خرید", "icon": "🛍️", "color": "#a855f7"},
    {"name": "قبوض و خدمات", "icon": "💡", "color": "#f59e0b"},
    {"name": "تفریح", "icon": "🎬", "color": "#ec4899"},
    {"name": "سلامت", "icon": "💊", "color": "#10b981"},
    {"name": "آموزش", "icon": "📚", "color": "#6366f1"},
    {"name": "سفر", "icon": "✈️", "color": "#06b6d4"},
    {"name": "حقوق و درآمد", "icon": "💰", "color": "#22c55e"},
    {"name": "سایر", "icon": "📦", "color": "#64748b"},
]


def ensure_default_categories(db: Session) -> list:
    """اگر هیچ دسته‌ای نبود، پیش‌فرض‌ها را بساز."""
    if db.query(Category).count() > 0:
        return []
    created = []
    for item in DEFAULT_CATEGORIES:
        cat = Category(**item, is_system=True)
        db.add(cat)
        created.append(cat)
    db.commit()
    for c in created:
        db.refresh(c)
    return created


@router.post("/seed", response_model=list[CategoryOut])
def seed_categories(db: Session = Depends(get_db)):
    existing = {name_key(c.name) for c in db.query(Category).all()}
    created = []
    for item in DEFAULT_CATEGORIES:
        if name_key(item["name"]) not in existing:
            cat = Category(**item, is_system=True)
            db.add(cat)
            created.append(cat)
            existing.add(name_key(item["name"]))
    db.commit()
    for c in created:
        db.refresh(c)
    return created


@router.get("/", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    ensure_default_categories(db)
    return db.query(Category).order_by(Category.name).all()


@router.post("/", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    key = name_key(payload.name)
    for c in db.query(Category).all():
        if name_key(c.name) == key:
            raise HTTPException(400, "این دسته از قبل وجود دارد")
    cat = Category(**payload.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat
