import pytest
from sqlalchemy import create_engine, text
from src.db import init_db, save_records, get_engine
import pandas as pd


@pytest.fixture
def engine():
    """
    Создаёт временный движок SQLite в памяти.
    """
    url = "sqlite:///:memory:"
    engine = create_engine(url, connect_args={"check_same_thread": False})
    yield engine


def test_init_db_creates_table(engine):
    """
    Проверяет, что init_db создаёт таблицу price_records.
    """
    init_db(engine)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='price_records'"))
        tables = result.fetchall()
        assert len(tables) == 1


def test_save_records(engine):
    """
    Проверяет сохранение DataFrame в БД и подсчёт строк.
    Ожидаемый результат: в таблице ровно 2 строки.
    """
    init_db(engine)
    df = pd.DataFrame(
        [
            {"price": 100.0, "count": 5, "add_cost": 10.0, "company": "A", "product": "X"},
            {"price": 200.0, "count": 3, "add_cost": 20.0, "company": "B", "product": "Y"},
        ]
    )
    save_records(engine, df)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM price_records"))
        count = result.scalar()
        assert count == 2


def test_get_engine_no_url(monkeypatch):
    """
    Нет db_url и нет переменной окружения DATABASE_URL — ValueError.
    """
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError):
        get_engine()


def test_get_engine_with_explicit_url():
    """
    Явная передача sqlite-URL — движок создаётся корректно.
    """
    engine = get_engine("sqlite:///:memory:")
    assert engine is not None


def test_save_records_correct_data(engine):
    """
    Проверяет, что сохранённые данные совпадают с исходными.
    Ожидаемый результат: price=150, count=10, company=TestCo.
    """
    init_db(engine)
    df = pd.DataFrame(
        [
            {"price": 150.0, "count": 10, "add_cost": 5.0, "company": "TestCo", "product": "Widget"},
        ]
    )
    save_records(engine, df)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT price, count, add_cost, company, product FROM price_records"))
        row = result.fetchone()
        assert row.price == 150.0
        assert row.count == 10
        assert row.add_cost == 5.0
        assert row.company == "TestCo"
        assert row.product == "Widget"
