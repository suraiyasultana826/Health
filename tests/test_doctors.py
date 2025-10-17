import pytest
import pytest_asyncio
from httpx import AsyncClient
from db import database
from fastapi import status

@pytest_asyncio.fixture
async def setup_doctor(test_db):
    db = next(test_db())
    doctor = database.Doctor(name="Dr. Test", specialty="Cardiology")
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    yield doctor
    db.delete(doctor)
    db.commit()

@pytest.mark.asyncio
async def test_list_doctors(client: AsyncClient, setup_doctor):
    response = await client.get("/doctors/list")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1
    assert response.json()[0]["name"] == "Dr. Test"
    assert response.json()[0]["specialty"] == "Cardiology"

@pytest.mark.asyncio
async def test_create_doctor(client: AsyncClient):
    response = await client.post("/doctors", data={"name": "Dr. New", "specialty": "Neurology"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"
    assert response.json()["doctor_id"] > 0

@pytest.mark.asyncio
async def test_update_doctor(client: AsyncClient, setup_doctor):
    response = await client.post("/doctors/update", data={"doctor_id": setup_doctor.id, "name": "Dr. Updated", "specialty": "Pediatrics"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"

@pytest.mark.asyncio
async def test_delete_doctor(client: AsyncClient, setup_doctor):
    response = await client.post("/doctors/delete", data={"doctor_id": setup_doctor.id})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"