import pytest
import pytest_asyncio
from httpx import AsyncClient
from db import database
from fastapi import status
from datetime import date, time

@pytest_asyncio.fixture
async def setup_cancellation(test_db):
    db = next(test_db())
    doctor = database.Doctor(name="Dr. Test", specialty="Cardiology")
    patient = database.Patient(name="Alice Test", email="alice@test.com")
    slot = database.AppointmentSlot(doctor_id=doctor.id, date=date(2025, 10, 18), start_time=time(10, 0), end_time=time(10, 30))
    appointment = database.Appointment(patient_id=patient.id, slot_id=slot.id, booked_at="2025-10-18 10:00:00")
    cancellation = database.Cancellation(appointment_id=appointment.id, reason="No show", cancelled_at="2025-10-18 10:00:00")
    db.add_all([doctor, patient, slot, appointment, cancellation])
    db.commit()
    db.refresh(cancellation)
    yield cancellation
    db.delete(cancellation)
    db.delete(appointment)
    db.delete(slot)
    db.delete(patient)
    db.delete(doctor)
    db.commit()

@pytest.mark.asyncio
async def test_list_cancellations(client: AsyncClient, setup_cancellation):
    response = await client.get("/cancellations/list")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1
    assert response.json()[0]["appointment_id"] == setup_cancellation.appointment_id
    assert response.json()[0]["reason"] == "No show"

@pytest.mark.asyncio
async def test_create_cancellation(client: AsyncClient, setup_cancellation):
    response = await client.post("/cancellations", data={"appointment_id": setup_cancellation.appointment_id, "reason": "Patient request"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"
    assert response.json()["cancellation_id"] > 0

@pytest.mark.asyncio
async def test_update_cancellation(client: AsyncClient, setup_cancellation):
    response = await client.post("/cancellations/update", data={"cancellation_id": setup_cancellation.id, "appointment_id": setup_cancellation.appointment_id, "reason": "Updated reason"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"

@pytest.mark.asyncio
async def test_delete_cancellation(client: AsyncClient, setup_cancellation):
    response = await client.post("/cancellations/delete", data={"cancellation_id": setup_cancellation.id})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"