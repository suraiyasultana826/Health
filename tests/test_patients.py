import pytest
import pytest_asyncio
from httpx import AsyncClient
from db import database
from fastapi import status

@pytest_asyncio.fixture
async def setup_patient(test_db):
    db = next(test_db())
    patient = database.Patient(name="Alice Test", email="alice@test.com")
    db.add(patient)
    db.commit()
    db.refresh(patient)
    yield patient
    db.delete(patient)
    db.commit()

@pytest.mark.asyncio
async def test_list_patients(client: AsyncClient, setup_patient):
    response = await client.get("/patients/list")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1
    assert response.json()[0]["name"] == "Alice Test"
    assert response.json()[0]["email"] == "alice@test.com"

@pytest.mark.asyncio
async def test_create_patient(client: AsyncClient):
    response = await client.post("/patients", data={"name": "Bob New", "email": "bob@test.com"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"
    assert response.json()["patient_id"] > 0

@pytest.mark.asyncio
async def test_update_patient(client: AsyncClient, setup_patient):
    response = await client.post("/patients/update", data={"patient_id": setup_patient.id, "name": "Alice Updated", "email": "alice.updated@test.com"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"

@pytest.mark.asyncio
async def test_delete_patient(client: AsyncClient, setup_patient):
    response = await client.post("/patients/delete", data={"patient_id": setup_patient.id})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"