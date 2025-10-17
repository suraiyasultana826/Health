import pytest
import pytest_asyncio
from httpx import AsyncClient
from db import database
from fastapi import status
from datetime import date, time

@pytest_asyncio.fixture
async def setup_appointment(test_db):
    db = next(test_db())
    doctor = database.Doctor(name="Dr. Test", specialty="Cardiology")
    patient = database.Patient(name="Alice Test", email="alice@test.com")
    slot = database.AppointmentSlot(doctor_id=doctor.id, date=date(2025, 10, 18), start_time=time(10, 0), end_time=time(10, 30))
    db.add_all([doctor, patient, slot])
    db.commit()
    appointment = database.Appointment(patient_id=patient.id, slot_id=slot.id, booked_at="2025-10-18 10:00:00")
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    yield appointment
    db.delete(appointment)
    db.delete(slot)
    db.delete(patient)
    db.delete(doctor)
    db.commit()

@pytest.mark.asyncio
async def test_list_appointments(client: AsyncClient, setup_appointment):
    response = await client.get("/appointments/list")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1
    assert response.json()[0]["patient_id"] == setup_appointment.patient_id
    assert response.json()[0]["slot_id"] == setup_appointment.slot_id

@pytest.mark.asyncio
async def test_create_appointment(client: AsyncClient, setup_appointment):
    response = await client.post("/appointments", data={"patient_id": setup_appointment.patient_id, "slot_id": setup_appointment.slot_id})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"
    assert response.json()["appointment_id"] > 0

@pytest.mark.asyncio
async def test_update_appointment(client: AsyncClient, setup_appointment):
    response = await client.post("/appointments/update", data={"appointment_id": setup_appointment.id, "patient_id": setup_appointment.patient_id, "slot_id": setup_appointment.slot_id})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"

@pytest.mark.asyncio
async def test_delete_appointment(client: AsyncClient, setup_appointment):
    response = await client.post("/appointments/delete", data={"appointment_id": setup_appointment.id})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"