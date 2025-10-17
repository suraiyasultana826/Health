
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base, SessionLocal
from main import app
from db import database
import asyncio

# Use SQLite in-memory database for tests
@pytest_asyncio.fixture
async def test_db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Override SessionLocal for tests
    def override_session():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[SessionLocal] = override_session
    yield TestingSessionLocal
    Base.metadata.drop_all(engine)

@pytest_asyncio.fixture
async def client():
    with TestClient(app) as c:
        yield c
