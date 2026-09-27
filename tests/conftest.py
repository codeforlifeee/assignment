import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from eve_health.database import Base, get_db
from eve_health.main import app
import os

os.environ["TESTING"] = "True"

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_eve_health.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # Create the test database and tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the test database tables after all tests finish
    Base.metadata.drop_all(bind=engine)
    import os
    if os.path.exists("./test_eve_health.db"):
        os.remove("./test_eve_health.db")

@pytest.fixture(scope="function")
def db_session():
    # Provide a transactional scope around a series of operations
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
