from src._shared.config import get_settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src._shared.infrastructure import orm


def build_postgres_uri():
    settings = get_settings()
    return f"postgresql://{settings.db.username}:{settings.db.password}@{settings.db.host}:{settings.db.port}/{settings.db.dbname}"


def postgres_db_engine():
    engine = create_engine(build_postgres_uri())
    orm.Base.metadata.create_all(engine)
    return engine


def get_db_session():
    yield sessionmaker(postgres_db_engine())
