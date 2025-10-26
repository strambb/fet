import pytest


import time
from sqlalchemy import create_engine, event
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from src._shared.infrastructure.orm import Base
from src._shared.infrastructure.database import build_postgres_uri
from fastapi.testclient import TestClient
from src._shared.config import Settings, TestConfig, DBConfig


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
    connection = postgres_db.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    # Start a SAVEPOINT - commits will only commit to this savepoint
    session.begin_nested()

    # Automatically restart the SAVEPOINT after each commit
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    yield session

    session.close()
    transaction.rollback()  # Rolls back everything, including "committed" data
    connection.close()


@pytest.fixture
def test_settings():
    
    
    test_config = TestConfig(
        username = "test_user",
        password= "Pa$$W0rd"
    )
    
    return Settings()



@pytest.fixture
def testclient():
    from src.main import app

    return TestClient(app)

@pytest.fixture
def test_user(test_settings):
    return {"username": f"{settings.test.username}", "password": f"{settings.test.password}"}


@pytest.fixture
def authorized_testclient(test_user, testclient):
    