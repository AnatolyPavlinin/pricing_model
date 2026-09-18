import os
import tempfile
import pytest
from sqlalchemy import create_engine
from src.db import get_engine, init_db, save_records, PriceRecord
import pandas as pd


@pytest.fixture
def engine():
    # Используем SQLite для тестов (чтобы не зависеть от PostgreSQL на CI)
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    url = f"sqlite:///{db_path}"
    engine = create_engine(url, echo=False)
    yield engine
    os.unlink(db_path)


def test_init_db_creates_table(engine):
    init_db(engine)
    # Проверяем, что таблица создана
    inspector = engine.dialect.has_table(engine, "price_records")
    assert inspector is True


def test_save_records(engine):
    init_db(engine)
    df = pd.DataFrame([
        {"price": 100.0, "count": 5, "add_cost": 10.0, "company": "A", "product": "X"},
        {"price": 200.0, "count": 3, "add_cost": 20.0, "company": "B", "product": "Y"},
    ])
    save_records(engine, df)

    with engine.connect() as conn:
        result = conn.execute("SELECT COUNT(*) FROM price_records").scalar()
        assert result == 2
