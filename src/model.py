import pandas as pd


def predict_price(
    df: pd.DataFrame, season_factor: float = 1.0, competitor_factor: float = 1.0, min_price_ratio: float = 0.9
) -> pd.DataFrame:
    """
    Прогнозирует цену на основе исторических данных.

    Логика:
    1. Базовая цена — средняя цена по продукту.
    2. Прогноз = базовая * сезонный коэффициент * коэффициент конкуренции + затраты на продвижение.
    3. Ограничение: прогноз не ниже min_price_ratio от базовой цены.

    Возвращает DataFrame с колонкой predicted_price.
    """

    # Копируем, чтобы не модифицировать исходный DataFrame
    df = df.copy()

    # Базовая цена — среднее по продукту (векторизованная операция)
    base_price = df.groupby("product")["price"].transform("mean")

    # Прогнозная цена
    df["predicted_price"] = base_price * season_factor * competitor_factor + df["add_cost"]

    # Ограничение снизу
    df["predicted_price"] = df["predicted_price"].clip(lower=base_price * min_price_ratio)

    return df
