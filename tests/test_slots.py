import pytest
import pytest_asyncio
from httpx import AsyncClient
from db import database
from fastapi import status
from datetime import date, time

@pytest_asyncio.fixture
async def setup_slot(test_db):
    db = next(test_db())
    doctor = database.Doctor(name="Dr. Test", specialty="Cardiology")
    db.add(doctor)
    db.commit()
    slot = database.AppointmentSlot(doctor_id=doctor.id, date=date(2025, 10, 18), start_time=time(10, 0), end_time=time(10, 30))
    db.add(slot)
    db.commit()
    db.refresh(slot)
    yield slot
    db.delete(slot)
    db.delete(doctor)
    db.commit()

@pytest.mark.asyncio
async def test_list_slots(client: AsyncClient, setup_slot):
    response = await client.get("/appointment_slots/list")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1
    assert response.json()[0]["doctor_id"] == setup_slot.doctor_id
    assert response.json()[0]["date"] == "2025-10-18"
    assert response.json()[0]["start_time"] == "10:00:00"
    assert response.json()[0]["end_time"] == "10:30:00"

@pytest.mark.asyncio
async def test_create_slot(client: AsyncClient, setup_slot):
    response = await client.post("/appointment_slots", data={"doctor_id": setup_slot.doctor_id, "date": "2025-10-19", "start_time": "11:00", "end_time": "11:30"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"
    assert response.json()["slot_id"] > 0

@pytest.mark.asyncio
async def test_update_slot(client: AsyncClient, setup_slot):
    response = await client.post("/appointment_slots/update", data={"slot_id": setup_slot.id, "doctor_id": setup_slot.doctor_id, "date": "2025-10-19", "start_time": "12:00", "end_time": "12:30", "is_available": True})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"

@pytest.mark.asyncio
async def test_delete_slot(client: AsyncClient, setup_slot):
    response = await client.post("/appointment_slots/delete", data={"slot_id": setup_slot.id})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"