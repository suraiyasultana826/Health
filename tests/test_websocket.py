import pytest
import pytest_asyncio
from websockets.client import connect
from db import database
from fastapi.testclient import TestClient
from main import app

@pytest_asyncio.fixture
async def ws_client():
    client = TestClient(app)
    async with connect("ws://localhost:8000/ws/doctors") as websocket:
        yield websocket
    client.close()

@pytest.mark.asyncio
async def test_websocket_doctors(test_db, ws_client):
    db = next(test_db())
    doctor = database.Doctor(name="Dr. Test", specialty="Cardiology")
    db.add(doctor)
    db.commit()
    # Simulate change in changes table
    change = database.Change(table_name="doctors", action="INSERT", record_id=doctor.id)
    db.add(change)
    db.commit()
    message = await ws_client.recv()
    assert message == "update_doctors"
    db.delete(doctor)
    db.delete(change)
    db.commit()