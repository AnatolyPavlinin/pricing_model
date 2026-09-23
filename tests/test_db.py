import os
import tempfile
import pytest
from sqlalchemy import create_engine, text
from src.db import get_engine, init_db, save_records, PriceRecord
import pandas as pd


@pytest.fixture
def engine():
    """
    Создаёт временный движок SQLite в памяти.
    Это полностью избегает проблем с блокировкой файлов на Windows
    и не требует ручного удаления файлов.
    """
    url = "sqlite:///:memory:"
    engine = create_engine(url, connect_args={"check_same_thread": False})
    yield engine


def test_init_db_creates_table(engine):
    """
    Проверяет, что init_db создаёт таблицу price_records.
    Ожидаемый результат: таблица существует в БД.
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
    df = pd.DataFrame([
        {"price": 100.0, "count": 5, "add_cost": 10.0, "company": "A", "product": "X"},
        {"price": 200.0, "count": 3, "add_cost": 20.0, "company": "B", "product": "Y"},
    ])
    save_records(engine, df)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM price_records"))
        count = result.scalar()
        assert count == 2
