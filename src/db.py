from os import getenv
from typing import Optional

from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()


class PriceRecord(Base):
    """
    ORM-модель для таблицы price_records в PostgreSQL.
    """
    __tablename__ = "price_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    price = Column(Float, nullable=False)
    count = Column(Integer, nullable=False)
    add_cost = Column(Float, nullable=False)
    company = Column(String, nullable=False)
    product = Column(String, nullable=False)


def get_engine(db_url: Optional[str] = None) -> object:
    """
    Создаёт движок SQLAlchemy. Если db_url не передан, берёт из переменной окружения DATABASE_URL.
    """
    if db_url is None:
        db_url = getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("Строка подключения к БД не найдена. Укажите DATABASE_URL в .env или передайте db_url явно.")
    return create_engine(db_url)


def init_db(engine: object) -> None:
    """
    Создаёт таблицы в БД, если их нет.
    """
    Base.metadata.create_all(engine)


def save_records(engine: object, df: object) -> None:
    """
    Сохраняет DataFrame в таблицу price_records через bulk_insert_mappings.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        records = df.to_dict(orient="records")
        session.bulk_insert_mappings(PriceRecord, records)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
