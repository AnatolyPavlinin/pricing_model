import os
import tempfile
import pytest
from sqlalchemy import create_engine, text
from src.loader import load_csv
from src.db import init_db, save_records
from src.model import predict_price


def test_full_pipeline():
    """
    Интеграционный тест: полный цикл load_csv → init_db → save_records → predict_price.
    Ожидаемый результат: данные загружены, сохранены в БД, прогноз рассчитан корректно.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
        tmp.write("price,count,add_cost,company,product\n100,5,10,A,X\n200,3,20,B,Y\n150,4,15,A,Y")
        csv_path = tmp.name

    try:
        # 1. Загрузка
        df = load_csv(csv_path)
        assert len(df) == 3

        # 2. Инициализация БД (in-memory)
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        init_db(engine)

        # 3. Сохранение
        save_records(engine, df)
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM price_records")).scalar()
            assert count == 3

        # 4. Прогноз
        result = predict_price(df, season_factor=1.0, competitor_factor=1.0)
        assert "predicted_price" in result.columns
        assert len(result) == 3

        # Product X: base=100, predicted=100+10=110
        x_rows = result[result["product"] == "X"]
        assert x_rows["predicted_price"].iloc[0] == 110.0

        # Product Y: base=mean(200,150)=175
        # add_cost=20: 175+20=195, add_cost=15: 175+15=190
        y_rows = result[result["product"] == "Y"].sort_values("add_cost")
        assert y_rows["predicted_price"].iloc[0] == 190.0
        assert y_rows["predicted_price"].iloc[1] == 195.0

    finally:
        os.unlink(csv_path)


def test_run_pipeline_missing_file():
    """
    Запуск пайплайна с несуществующим файлом — FileNotFoundError.
    """
    from main import run_pipeline

    with pytest.raises(FileNotFoundError):
        run_pipeline("does/not/exist.csv", db_url="sqlite:///:memory:")
