from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {"price", "count", "add_cost", "company", "product"}


def load_csv(file_path: str) -> pd.DataFrame:
    """
    Загружает CSV-файл, проверяет наличие обязательных колонок и типы данных.
    Возвращает DataFrame.
    """
    path = Path(file_path)

    # Проверяем существование файла
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    # Читаем CSV
    df = pd.read_csv(path)

    # Проверяем обязательные колонки
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(f"Отсутствуют обязательные колонки: {missing_cols}")

    # Проверяем типы данных для числовых колонок
    numeric_cols = ["price", "count", "add_cost"]
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise TypeError(f"Колонка {col} должна быть числовой, но имеет тип {df[col].dtype}")

    # Удаляем строки с пропусками в ключевых колонках
    df = df.dropna(subset=numeric_cols)

    return df
