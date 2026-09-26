import os
import tempfile
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


def test_load_csv_missing_file():
    """
    Файла нет на диске — FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError):
        load_csv("does/not/exist.csv")


def test_load_csv_drops_nan_rows():
    """
    Строка с пропуском в price удаляется из выборки.
    Ожидаемый результат: 1 строка вместо 2.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
        tmp.write("price,count,add_cost,company,product\n100,5,10,A,X\n,3,20,B,Y")
        tmp_path = tmp.name

    try:
        df = load_csv(tmp_path)
        assert len(df) == 1
    finally:
        os.unlink(tmp_path)


def test_load_csv_columns_different_order():
    """
    Колонки в другом порядке — загрузка работает корректно.
    Ожидаемый результат: DataFrame загружен, длина 2 строки.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
        tmp.write("company,product,price,count,add_cost\nA,X,100,5,10\nB,Y,200,3,20")
        tmp_path = tmp.name

    try:
        df = load_csv(tmp_path)
        assert len(df) == 2
        assert "price" in df.columns
        assert "product" in df.columns
    finally:
        os.unlink(tmp_path)


def test_load_csv_empty_file():
    """
    Пустой файл (0 байт) — pandas не может прочитать, выбрасывает ошибку.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
        tmp.write("")
        tmp_path = tmp.name

    try:
        with pytest.raises(Exception):
            load_csv(tmp_path)
    finally:
        os.unlink(tmp_path)


def test_load_csv_extra_columns():
    """
    Лишние колонки в CSV — загрузка проходит, обязательные на месте.
    Ожидаемый результат: DataFrame загружен, длина 2 строки.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
        tmp.write("price,count,add_cost,company,product,extra_col\n100,5,10,A,X,foo\n200,3,20,B,Y,bar")
        tmp_path = tmp.name

    try:
        df = load_csv(tmp_path)
        assert len(df) == 2
        assert "price" in df.columns
        assert "extra_col" in df.columns
    finally:
        os.unlink(tmp_path)
