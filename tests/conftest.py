import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.orm import Base


@pytest.fixture
def in_mem_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_mem_db):
    yield sessionmaker(bind=in_mem_db)()
