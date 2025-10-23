import pytest


import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from src.infrastructure.orm import Base
from src.config import get_config


@pytest.fixture
def in_mem_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_mem_db):
    yield sessionmaker(bind=in_mem_db)()


def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("Postgres never came up")


def build_postgres_uri():
    settings = get_config()
    return f"postgresql://{settings.db.username}:{settings.db.password}@{settings.db.host}:{settings.db.port}/{settings.db.dbname}"


@pytest.fixture(scope="session")
def postgres_db():
    engine = create_engine(build_postgres_uri())
    if not database_exists(engine.url):
        create_database(engine.url)
    wait_for_postgres_to_come_up(engine)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session(postgres_db):
    yield sessionmaker(bind=postgres_db)()
    Base.metadata.drop_all(postgres_db)
    Base.metadata.create_all(postgres_db)
