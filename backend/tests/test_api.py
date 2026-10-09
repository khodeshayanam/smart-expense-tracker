from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    # fresh in-memory DB per test -> tests never touch the real data file
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    from app import models  # noqa: F401  (register tables)
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
    body = {"amount": 10, "description": "coffee", "date": "2026-01-01", "category_id": 1}
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
