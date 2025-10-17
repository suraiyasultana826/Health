from fastapi import APIRouter, HTTPException, Form
from db.database import SessionLocal
from db import database

router = APIRouter()

def get_slots(db):
    return db.query(database.AppointmentSlot).all()

@router.get("/list")
async def list_slots():
    db = SessionLocal()
    try:
        slots = get_slots(db)
        return [
            {
                "id": s.id,
                "doctor_id": s.doctor_id,
                "date": str(s.date),
                "start_time": str(s.start_time),
                "end_time": str(s.end_time),
                "is_available": s.is_available
            } for s in slots
        ]
    finally:
        db.close()

@router.post("/")
async def create_slot(
    doctor_id: int = Form(...),
    date: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    is_available: bool = Form(True)
):
    db = SessionLocal()
    try:
        slot = database.AppointmentSlot(
            doctor_id=doctor_id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            is_available=is_available
        )
        db.add(slot)
        db.commit()
        db.refresh(slot)
        return {"status": "success", "slot_id": slot.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/update")
async def update_slot(
    slot_id: int = Form(...),
    doctor_id: int = Form(...),
    date: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    is_available: bool = Form(...)
):
    db = SessionLocal()
    try:
        slot = db.query(database.AppointmentSlot).filter(database.AppointmentSlot.id == slot_id).first()
        if not slot:
            raise HTTPException(status_code=404, detail="Slot not found")
        slot.doctor_id = doctor_id
        slot.date = date
        slot.start_time = start_time
        slot.end_time = end_time
        slot.is_available = is_available
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/delete")
async def delete_slot(slot_id: int = Form(...)):
    db = SessionLocal()
    try:
        slot = db.query(database.AppointmentSlot).filter(database.AppointmentSlot.id == slot_id).first()
        if not slot:
            raise HTTPException(status_code=404, detail="Slot not found")
        db.delete(slot)
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()