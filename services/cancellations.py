from fastapi import APIRouter, HTTPException, Form
from db.database import SessionLocal
from db import database
from datetime import datetime

router = APIRouter()

def get_cancellations(db):
    return db.query(database.Cancellation).all()

@router.get("/list")
async def list_cancellations():
    db = SessionLocal()
    cancellations = get_cancellations(db)
    db.close()
    return [{"id": c.id, "appointment_id": c.appointment_id, "reason": c.reason, "cancelled_at": str(c.cancelled_at)} for c in cancellations]

@router.post("/")
async def create_cancellation(appointment_id: int = Form(...), reason: str = Form(None)):
    db = SessionLocal()
    try:
        cancellation = database.Cancellation(appointment_id=appointment_id, reason=reason, cancelled_at=datetime.now())
        db.add(cancellation)
        db.commit()
        db.refresh(cancellation)
        return {"status": "success", "cancellation_id": cancellation.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/update")
async def update_cancellation(cancellation_id: int = Form(...), appointment_id: int = Form(...), reason: str = Form(None)):
    db = SessionLocal()
    try:
        cancellation = db.query(database.Cancellation).filter(database.Cancellation.id == cancellation_id).first()
        if not cancellation:
            raise HTTPException(status_code=404, detail="Cancellation not found")
        cancellation.appointment_id = appointment_id
        cancellation.reason = reason
        cancellation.cancelled_at = datetime.now()
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/delete")
async def delete_cancellation(cancellation_id: int = Form(...)):
    db = SessionLocal()
    try:
        cancellation = db.query(database.Cancellation).filter(database.Cancellation.id == cancellation_id).first()
        if not cancellation:
            raise HTTPException(status_code=404, detail="Cancellation not found")
        db.delete(cancellation)
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()