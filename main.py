import os
from dotenv import load_dotenv

from src.loader import load_csv
from src.db import get_engine, init_db, save_records
from src.model import predict_price

load_dotenv()  # загружает переменные из .env


def run_pipeline(csv_path: str, db_url: str | None = None, season_factor: float = 1.0, competitor_factor: float = 1.0):
    """
    Полный пайплайн: загрузка CSV -> сохранение в БД -> прогноз -> сохранение прогноза.
    """
    # 1. Загрузка данных
    df = load_csv(csv_path)
    print(f"Загружено строк: {len(df)}")

    # 2. Инициализация БД и сохранение
    engine = get_engine(db_url)
    init_db(engine)
    save_records(engine, df)
    print("Данные сохранены в БД.")

    # 3. Прогноз
    result_df = predict_price(df, season_factor, competitor_factor)

    # 4. Сохранение прогноза
    result_df.to_csv("predictions.csv", index=False)
    print("Прогноз сохранён в predictions.csv")


if __name__ == "__main__":
    csv_file = "data/csv_data.csv"
    run_pipeline(csv_file)
