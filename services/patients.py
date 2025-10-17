from fastapi import APIRouter, HTTPException, Form
from db.database import SessionLocal
from db import database

router = APIRouter()

def get_patients(db):
    return db.query(database.Patient).all()

@router.get("/list")
async def list_patients():
    db = SessionLocal()
    patients = get_patients(db)
    db.close()
    return [{"id": p.id, "name": p.name, "email": p.email} for p in patients]

@router.post("/")
async def create_patient(name: str = Form(...), email: str = Form(...)):
    db = SessionLocal()
    try:
        patient = database.Patient(name=name, email=email)
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return {"status": "success", "patient_id": patient.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/update")
async def update_patient(patient_id: int = Form(...), name: str = Form(...), email: str = Form(...)):
    db = SessionLocal()
    try:
        patient = db.query(database.Patient).filter(database.Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        patient.name = name
        patient.email = email
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/delete")
async def delete_patient(patient_id: int = Form(...)):
    db = SessionLocal()
    try:
        patient = db.query(database.Patient).filter(database.Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        db.delete(patient)
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()