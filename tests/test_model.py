import pandas as pd
from src.model import predict_price


def test_predict_price_basic():
    """
    Базовый тест прогноза цены: проверяем корректность расчёта для двух строк.
    Логика: базовая цена усредняется по продукту, затем применяется формула.
    Ожидаемый результат: predicted_price = 110 и 120 соответственно.
    """
    df = pd.DataFrame(
        [
            {"price": 100.0, "count": 5, "add_cost": 10.0, "company": "A", "product": "X"},
            {"price": 100.0, "count": 3, "add_cost": 20.0, "company": "B", "product": "X"},
        ]
    )
    result = predict_price(df, season_factor=1.0, competitor_factor=1.0)
    assert "predicted_price" in result.columns

    # Базовая цена для продукта X = среднее(100, 100) = 100
    # Строка 0: прогноз = 100 * 1.0 * 1.0 + 10 = 110
    # Строка 1: прогноз = 100 * 1.0 * 1.0 + 20 = 120
    assert result["predicted_price"].iloc[0] == 110.0
    assert result["predicted_price"].iloc[1] == 120.0


def test_predict_price_min_ratio():
    """
    Тест ограничения минимальной цены (min_price_ratio).
    Проверяем, что прогноз не падает ниже 90% от базовой цены.
    Ожидаемый результат: predicted_price >= 90.0.
    """
    df = pd.DataFrame(
        [
            {"price": 100.0, "count": 5, "add_cost": 0.0, "company": "A", "product": "X"},
        ]
    )
    # Базовая цена = 100, add_cost = 0, прогноз = 100 * 1.0 * 1.0 + 0 = 100
    # min_price_ratio = 0.9, нижняя граница = 100 * 0.9 = 90
    # Прогноз (100) выше границы (90), значит остаётся 100
    result = predict_price(df, season_factor=1.0, competitor_factor=1.0, min_price_ratio=0.9)
    assert result["predicted_price"].iloc[0] >= 90.0


def test_predict_price_empty_df():
    """
    Тест на пустой DataFrame: функция не должна падать.
    Ожидаемый результат: возвращается DataFrame с колонкой predicted_price и длиной 0.
    """
    df = pd.DataFrame(columns=["price", "count", "add_cost", "company", "product"])
    result = predict_price(df)
    assert "predicted_price" in result.columns
    assert len(result) == 0


def test_predict_price_season_factor():
    """
    Тест влияния сезонного коэффициента на прогноз.
    Проверяем, что изменение season_factor реально меняет результат.
    Ожидаемый результат: при factor=0.5 прогноз ограничен снизу (90.0), при factor=2.0 прогноз = 210.0.
    """
    df = pd.DataFrame(
        [
            {"price": 100.0, "count": 5, "add_cost": 10.0, "company": "A", "product": "X"},
        ]
    )
    result_low = predict_price(df, season_factor=0.5, competitor_factor=1.0)
    result_high = predict_price(df, season_factor=2.0, competitor_factor=1.0)

    # Без сезонного коэффициента прогноз = 100 + 10 = 110
    # С factor=0.5: 100 * 0.5 + 10 = 60, но clip снизу = 90 -> 90
    # С factor=2.0: 100 * 2.0 + 10 = 210
    assert result_low["predicted_price"].iloc[0] == 90.0
    assert result_high["predicted_price"].iloc[0] == 210.0
