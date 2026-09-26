import os
from dotenv import load_dotenv
from src.loader import load_csv
from src.db import get_engine, init_db, save_records
from src.model import predict_price

load_dotenv()


def get_float_input(prompt: str, default: float) -> float:
    """
    Запрашивает у пользователя число. Если просто нажал Enter — возвращает default.
    В Docker stdin недоступен, поэтому берём из env-переменных.
    """
    env_key = prompt.split("(")[0].strip().upper().replace(" ", "_")
    env_key = f"INPUT_{env_key}"

    env_val = os.getenv(env_key)
    if env_val is not None:
        try:
            return float(env_val)
        except ValueError:
            pass

    try:
        user_input = input(f"{prompt} (по умолчанию {default}): ").strip()
    except EOFError:
        return default

    if user_input == "":
        return default
    try:
        return float(user_input)
    except ValueError:
        print(f"Некорректное число, используем значение по умолчанию: {default}")
        return default


def run_pipeline(csv_path: str, db_url: str | None = None):
    print("--- Запуск пайплайна ценообразования ---")

    # 1. Загрузка данных
    df = load_csv(csv_path)
    print(f"✅ Загружено строк: {len(df)}")

    # 2. Инициализация БД и сохранение
    engine = get_engine(db_url)
    init_db(engine)
    save_records(engine, df)
    print("✅ Данные сохранены в БД.")

    # 3. Коэффициенты: env-переменные с fallback на интерактив
    print("\n🎯 Настройка коэффициентов прогноза:")
    season_factor = get_float_input("Сезонный коэффициент (например, 1.2 в сезон)", 1.0)
    competitor_factor = get_float_input("Коэффициент конкуренции (1.0 = норма, <1 = конкуренты дешевле)", 1.0)
    min_ratio = get_float_input("Минимальный порог цены (доля от базовой, например 0.9)", 0.9)

    # 4. Прогноз
    print("\n🧮 Расчёт прогнозной цены...")
    result_df = predict_price(df, season_factor, competitor_factor, min_ratio)

    # Вывод статистики для наглядности
    print("\n📊 Статистика прогноза:")
    print(result_df[["product", "price", "add_cost", "predicted_price"]].head())

    # 5. Сохранение прогноза в output/
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "predictions.csv")
    result_df.to_csv(output_file, index=False)
    print(f"\n✅ Прогноз сохранён в файл: {output_file}")


if __name__ == "__main__":
    csv_file = "data/csv_data.csv"

    if not os.path.exists(csv_file):
        print(f"⚠️ Файл {csv_file} не найден! Создай его в папке data/ или положи туда csv_data.csv")
    else:
        run_pipeline(csv_file)
