"""
هوش مصنوعی مولد (Generative AI) روی داده‌های هزینه.
از Google Gemini (رایگان) استفاده می‌کند. کلید API را در فایل .env
با نام GEMINI_API_KEY تنظیم کنید (رایگان از aistudio.google.com/apikey).
"""
from __future__ import annotations

import os
import json
import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..analysis.insights import (
    overall_stats,
    monthly_summary,
    predict_next_month,
    detect_patterns,
)

router = APIRouter(prefix="/ai", tags=["AI"])

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)


class ChatRequest(BaseModel):
    message: str


def _build_context(db: Session) -> dict:
    """خلاصه‌ای عددی از وضعیت مالی کاربر که به مدل زبانی پاس داده می‌شود."""
    return {
        "overview": overall_stats(db),
        "monthly_summary": monthly_summary(db, months=6),
        "prediction": predict_next_month(db),
        "patterns": detect_patterns(db),
    }


def _call_gemini(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            503,
            "کلید GEMINI_API_KEY تنظیم نشده است. یک کلید رایگان از "
            "aistudio.google.com/apikey بگیرید و در فایل backend/.env قرار دهید.",
        )

    try:
        resp = requests.post(
            f"{GEMINI_URL}?key={api_key}",
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.4, "maxOutputTokens": 700},
            },
            timeout=20,
        )
    except requests.RequestException as exc:
        raise HTTPException(502, f"خطا در ارتباط با سرویس هوش مصنوعی: {exc}")

    if resp.status_code != 200:
        raise HTTPException(502, f"سرویس هوش مصنوعی خطا داد: {resp.text[:300]}")

    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise HTTPException(502, "پاسخ نامعتبر از سرویس هوش مصنوعی")


@router.get("/smart-insights")
def smart_insights(db: Session = Depends(get_db)):
    """یک تحلیل متنی هوشمند و کوتاه از وضعیت مالی اخیر کاربر تولید می‌کند."""
    context = _build_context(db)
    prompt = (
        "تو یک مشاور مالی شخصی فارسی‌زبان هستی. بر اساس داده‌های JSON زیر "
        "(که خلاصه هزینه‌های یک کاربر است)، یک تحلیل کوتاه (حداکثر ۵ جمله)، "
        "دوستانه و عملی به فارسی بنویس. روی مهم‌ترین نکته یا هشدار تمرکز کن و "
        "یک پیشنهاد عملی بده. فقط متن تحلیل را بنویس، بدون مقدمه یا فرمت اضافه.\n\n"
        f"داده‌ها:\n{json.dumps(context, ensure_ascii=False, default=str)}"
    )
    text = _call_gemini(prompt)
    return {"insight": text, "based_on": context["overview"]}


@router.post("/chat")
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    """پرسش و پاسخ آزاد درباره وضعیت مالی کاربر."""
    context = _build_context(db)
    prompt = (
        "تو دستیار مالی شخصی فارسی‌زبان یک اپ مدیریت هزینه هستی. فقط بر اساس "
        "داده‌های JSON زیر به سؤال کاربر پاسخ بده. اگر داده کافی برای پاسخ دقیق "
        "نیست، صادقانه بگو. پاسخ را کوتاه، مفید و به فارسی بنویس.\n\n"
        f"داده‌های کاربر:\n{json.dumps(context, ensure_ascii=False, default=str)}\n\n"
        f"سؤال کاربر: {payload.message}"
    )
    answer = _call_gemini(prompt)
    return {"answer": answer}
