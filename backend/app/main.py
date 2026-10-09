from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import expenses, categories, habits, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Smart Expense & Habit Tracker API",
    description="Expense tracking + statistical insights + habit streaks",
    version="1.1.0",
    lifespan=lifespan,
)

# Restrict CORS to local frontend only (safer for personal finance data)
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
        "message": "Smart Expense & Habit Tracker API is running",
        "docs": "/docs",
        "version": "1.1.0",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
