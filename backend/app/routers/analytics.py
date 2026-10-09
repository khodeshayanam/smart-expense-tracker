from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..analysis.insights import (
    monthly_summary,
    predict_next_month,
    detect_patterns,
    overall_stats,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
def get_summary(months: int = 12, db: Session = Depends(get_db)):
    return monthly_summary(db, months=months)


@router.get("/predict")
def get_prediction(db: Session = Depends(get_db)):
    return predict_next_month(db)


@router.get("/insights")
def get_insights(db: Session = Depends(get_db)):
    return detect_patterns(db)


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    return overall_stats(db)