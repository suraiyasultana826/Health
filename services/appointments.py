from fastapi import APIRouter, HTTPException, Form
from db.database import SessionLocal
from db import database
from datetime import datetime

router = APIRouter()

def get_appointments(db):
    return db.query(database.Appointment).all()

@router.get("/list")
async def list_appointments():
    db = SessionLocal()
    appointments = get_appointments(db)
    db.close()
    return [{"id": a.id, "patient_id": a.patient_id, "slot_id": a.slot_id, "booked_at": str(a.booked_at)} for a in appointments]

@router.post("/")
async def create_appointment(patient_id: int = Form(...), slot_id: int = Form(...)):
    db = SessionLocal()
    try:
        appointment = database.Appointment(patient_id=patient_id, slot_id=slot_id, booked_at=datetime.now())
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        return {"status": "success", "appointment_id": appointment.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/update")
async def update_appointment(appointment_id: int = Form(...), patient_id: int = Form(...), slot_id: int = Form(...)):
    db = SessionLocal()
    try:
        appointment = db.query(database.Appointment).filter(database.Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        appointment.patient_id = patient_id
        appointment.slot_id = slot_id
        appointment.booked_at = datetime.now()
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/delete")
async def delete_appointment(appointment_id: int = Form(...)):
    db = SessionLocal()
    try:
        appointment = db.query(database.Appointment).filter(database.Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        db.delete(appointment)
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()