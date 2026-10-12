from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db, SessionLocal
from .routers import expenses, categories, habits, analytics
from .routers.categories import ensure_default_categories


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # هنگام اولین اجرا، دسته‌های پیش‌فرض فارسی ساخته می‌شوند
    db = SessionLocal()
    try:
        ensure_default_categories(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="مدیریت هزینه هوشمند",
    description="ثبت هزینه، عادت‌ها و تحلیل آماری",
    version="1.6.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(habits.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "API مدیریت هزینه در حال اجراست",
        "docs": "/docs",
        "version": "1.6.0",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
