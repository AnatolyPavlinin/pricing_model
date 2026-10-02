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
    Ожидаемый результат: при factor=0.5 прогноз ограничен снизу (90.0), при factor=2.0 прогноз = 210.0.
    """
    df = pd.DataFrame(
        [
            {"price": 100.0, "count": 5, "add_cost": 10.0, "company": "A", "product": "X"},
        ]
    )
    result_low = predict_price(df, season_factor=0.5, competitor_factor=1.0)
    result_high = predict_price(df, season_factor=2.0, competitor_factor=1.0)

    assert result_low["predicted_price"].iloc[0] == 90.0
    assert result_high["predicted_price"].iloc[0] == 210.0


def test_predict_price_does_not_modify_original():
    """
    Проверка, что исходный DataFrame не изменился после вызова predict_price.
    Ожидаемый результат: колонки исходного df те же, predicted_price не добавилась.
    """
    df = pd.DataFrame(
        [
            {"price": 100.0, "count": 5, "add_cost": 10.0, "company": "A", "product": "X"},
        ]
    )
    original_cols = list(df.columns)
    result = predict_price(df, season_factor=1.0, competitor_factor=1.0)

    assert "predicted_price" not in df.columns
    assert list(df.columns) == original_cols
    assert "predicted_price" in result.columns


def test_predict_price_multiple_products():
    """
    Тест с разными продуктами: базовая цена считается отдельно для каждого.
    Ожидаемый результат: X → 110.0, Y → 220.0.
    """
    df = pd.DataFrame(
        [
            {"price": 100.0, "count": 5, "add_cost": 10.0, "company": "A", "product": "X"},
            {"price": 200.0, "count": 3, "add_cost": 20.0, "company": "B", "product": "Y"},
        ]
    )
    result = predict_price(df, season_factor=1.0, competitor_factor=1.0)

    assert result["predicted_price"].iloc[0] == 110.0
    assert result["predicted_price"].iloc[1] == 220.0


def test_predict_price_competitor_factor():
    """
    Тест влияния конкурентного коэффициента на прогноз.
    Ожидаемый результат: при competitor=0.5 прогноз ограничен снизу (90.0), при competitor=2.0 = 200.0.
    """
    df = pd.DataFrame(
        [
            {"price": 100.0, "count": 5, "add_cost": 0.0, "company": "A", "product": "X"},
        ]
    )
    result_low = predict_price(df, season_factor=1.0, competitor_factor=0.5)
    result_high = predict_price(df, season_factor=1.0, competitor_factor=2.0)

    # 100 * 1.0 * 0.5 + 0 = 50, clip to 90 → 90
    # 100 * 1.0 * 2.0 + 0 = 200
    assert result_low["predicted_price"].iloc[0] == 90.0
    assert result_high["predicted_price"].iloc[0] == 200.0


def test_predict_price_zero_price():
    """
    Тест с нулевой базовой ценой — граничный случай.
    Ожидаемый результат: прогноз = 0 + add_cost = 10.0, clip(lower=0) не влияет.
    """
    df = pd.DataFrame(
        [
            {"price": 0.0, "count": 5, "add_cost": 10.0, "company": "A", "product": "X"},
        ]
    )
    result = predict_price(df, season_factor=1.0, competitor_factor=1.0)
    assert result["predicted_price"].iloc[0] == 10.0
