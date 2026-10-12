from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _fk(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    from app import models  # noqa: F401
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    c = TestClient(app)
    c.post("/api/categories/seed")
    yield c
    app.dependency_overrides.clear()


def _expense(client, **kw):
    body = {
        "amount": 10,
        "description": "coffee",
        "date": "2026-01-01",
        "category_id": 1,
        "tx_type": "expense",
    }
    body.update(kw)
    return client.post("/api/expenses/", json=body)


def test_patch_can_change_date(client):
    eid = _expense(client).json()["id"]
    r = client.patch(f"/api/expenses/{eid}", json={"date": "2026-03-05"})
    assert r.status_code == 200
    assert r.json()["date"] == "2026-03-05"


@pytest.mark.parametrize("field", ["amount", "description", "date", "category_id"])
def test_patch_null_is_rejected_not_500(client, field):
    eid = _expense(client).json()["id"]
    assert client.patch(f"/api/expenses/{eid}", json={field: None}).status_code == 422


def test_patch_unknown_category_rejected(client):
    eid = _expense(client).json()["id"]
    assert client.patch(f"/api/expenses/{eid}", json={"category_id": 999}).status_code == 400


@pytest.mark.parametrize("bad", [
    {"amount": 1e30}, {"amount": -5}, {"description": "   "}, {"date": "2099-01-01"},
])
def test_create_validation(client, bad):
    assert _expense(client, **bad).status_code == 422


def test_suggest_route_not_shadowed_by_id_route(client):
    assert client.get("/api/expenses/suggest-category?description=pizza").status_code == 200


def test_duplicate_category_rejected_case_insensitive(client):
    assert client.post("/api/categories/", json={"name": "Food & Drink"}).status_code == 400
    assert client.post("/api/categories/", json={"name": "food & drink"}).status_code == 400


def test_streak_gap_breaks_streak(client):
    hid = client.post("/api/habits/", json={"name": "read"}).json()["id"]
    today = date.today()
    for n in (0, 2, 4):
        client.post("/api/habits/log", json={"habit_id": hid, "date": str(today - timedelta(days=n))})
    s = client.get(f"/api/habits/{hid}/streak").json()
    assert s["current_streak"] == 1
    assert s["longest_streak"] >= s["current_streak"]


def test_inactive_habit_is_hidden(client):
    hid = client.post("/api/habits/", json={"name": "x"}).json()["id"]
    client.delete(f"/api/habits/{hid}")
    assert client.get(f"/api/habits/{hid}").status_code == 404
    assert client.get(f"/api/habits/{hid}/streak").status_code == 404


def test_income_excluded_from_total_spent(client):
    # category 1 is Food; find Salary category
    cats = client.get("/api/categories/").json()
    salary = next(c for c in cats if "Salary" in c["name"] or "Income" in c["name"])
    food = next(c for c in cats if "Food" in c["name"])
    _expense(client, amount=100, category_id=food["id"], tx_type="expense")
    _expense(client, amount=5000, category_id=salary["id"], tx_type="income", description="pay")
    ov = client.get("/api/analytics/overview").json()
    assert ov["total_spent"] == 100
    assert ov["top_category"] != salary["name"]


def test_avg_daily_inclusive_span(client):
    food_id = 1
    for i in range(10):
        _expense(client, amount=100, date=f"2026-01-{i+1:02d}", category_id=food_id, description=f"d{i}")
    ov = client.get("/api/analytics/overview").json()
    # 10 days inclusive => avg 100
    assert ov["avg_daily"] == 100.0


def test_summary_months_bounds(client):
    assert client.get("/api/analytics/summary?months=1000000000").status_code == 422
    assert client.get("/api/analytics/summary?months=0").status_code == 422
    assert client.get("/api/analytics/summary?months=-5").status_code == 422
    assert client.get("/api/analytics/summary?months=12").status_code == 200


def test_habit_log_preserves_notes(client):
    hid = client.post("/api/habits/", json={"name": "notes-test"}).json()["id"]
    d = str(date.today())
    r1 = client.post("/api/habits/log", json={"habit_id": hid, "date": d, "notes": "first"})
    assert r1.status_code == 201
    assert r1.json()["notes"] == "first"
    # re-log without notes field — should keep existing notes
    r2 = client.post("/api/habits/log", json={"habit_id": hid, "date": d, "completed": True})
    assert r2.status_code == 201
    assert r2.json()["notes"] == "first"


def test_identical_amounts_not_all_outliers(client):
    for i in range(20):
        _expense(client, amount=100, description=f"same{i}", date=f"2026-02-{(i % 28) + 1:02d}")
    insights = client.get("/api/analytics/insights").json()
    outlier = [x for x in insights if x.get("type") == "outliers"]
    assert outlier == []  # IQR of identical values is 0 => no outliers


def test_start_after_end_rejected(client):
    r = client.get("/api/expenses/?start_date=2026-06-01&end_date=2026-01-01")
    assert r.status_code == 422
