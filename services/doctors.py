from fastapi import APIRouter, HTTPException, Form
from db.database import SessionLocal
from db import database

router = APIRouter()

def get_doctors(db):
    return db.query(database.Doctor).all()

@router.get("/list")
async def list_doctors():
    db = SessionLocal()
    try:
        doctors = get_doctors(db)
        return [{"id": d.id, "name": d.name, "specialty": d.specialty} for d in doctors]
    finally:
        db.close()

@router.post("/")
async def create_doctor(name: str = Form(...), specialty: str = Form(...)):
    db = SessionLocal()
    try:
        doctor = database.Doctor(name=name, specialty=specialty)
        db.add(doctor)
        db.commit()
        db.refresh(doctor)
        return {"status": "success", "doctor_id": doctor.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/update")
async def update_doctor(doctor_id: int = Form(...), name: str = Form(...), specialty: str = Form(...)):
    db = SessionLocal()
    try:
        doctor = db.query(database.Doctor).filter(database.Doctor.id == doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        doctor.name = name
        doctor.specialty = specialty
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/delete")
async def delete_doctor(doctor_id: int = Form(...)):
    db = SessionLocal()
    try:
        doctor = db.query(database.Doctor).filter(database.Doctor.id == doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        db.delete(doctor)
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()