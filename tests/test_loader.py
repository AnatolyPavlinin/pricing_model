import os
import tempfile
import pandas as pd
import pytest
from src.loader import load_csv


def test_load_csv_valid():
    """
    Тест валидной загрузки CSV: файл существует, все колонки на месте, типы корректны.
    Ожидаемый результат: DataFrame загружен, длина 2 строки.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
        tmp.write("price,count,add_cost,company,product\n100,5,10,A,X\n200,3,20,B,Y")
        tmp_path = tmp.name

    try:
        df = load_csv(tmp_path)
        assert len(df) == 2
        assert "price" in df.columns
    finally:
        os.unlink(tmp_path)


def test_load_csv_missing_column():
    """
    Тест на отсутствие обязательных колонок.
    Ожидаемый результат: функция выбрасывает ValueError.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
        tmp.write("price,count,add_cost,company\n100,5,10,A")
        tmp_path = tmp.name

    try:
        with pytest.raises(ValueError):
            load_csv(tmp_path)
    finally:
        os.unlink(tmp_path)


def test_load_csv_non_numeric():
    """
    Тест некорректных типов данных в числовых колонках.
    Ожидаемый результат: функция выбрасывает TypeError.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
        tmp.write("price,count,add_cost,company,product\n100,five,10,A,X")
        tmp_path = tmp.name

    try:
        with pytest.raises(TypeError):
            load_csv(tmp_path)
    finally:
        os.unlink(tmp_path)
