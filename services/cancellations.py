from fastapi import APIRouter, HTTPException, Form
from db.database import SessionLocal
from db import database
from datetime import datetime
from sqlalchemy import func, case, and_, or_

router = APIRouter()

def get_cancellations(db):
    """Get all cancellations with related data"""
    return db.query(
        database.Cancellation,
        database.Appointment,
        database.Patient,
        database.AppointmentSlot,
        database.Doctor
    ).join(
        database.Appointment,
        database.Cancellation.appointment_id == database.Appointment.id
    ).join(
        database.Patient,
        database.Appointment.patient_id == database.Patient.id
    ).outerjoin(
        database.AppointmentSlot,
        database.Appointment.slot_id == database.AppointmentSlot.id
    ).outerjoin(
        database.Doctor,
        database.AppointmentSlot.doctor_id == database.Doctor.id
    ).all()

@router.get("/list")
async def list_cancellations():
    """List all cancellations with detailed information"""
    db = SessionLocal()
    try:
        cancellations = get_cancellations(db)
        
        return [{
            "id": c.Cancellation.id,
            "appointment_id": c.Cancellation.appointment_id,
            "reason": c.Cancellation.reason,
            "cancelled_at": str(c.Cancellation.cancelled_at),
            "patient_id": c.Patient.id if c.Patient else None,
            "patient_name": c.Patient.name if c.Patient else "Unknown",
            "patient_email": c.Patient.email if c.Patient else "N/A",
            "doctor_id": c.Doctor.id if c.Doctor else None,
            "doctor_name": c.Doctor.name if c.Doctor else "Unknown",
            "doctor_specialty": c.Doctor.specialty if c.Doctor else "N/A",
            "slot_date": str(c.AppointmentSlot.date) if c.AppointmentSlot else None,
            "slot_time": str(c.AppointmentSlot.start_time) if c.AppointmentSlot else None,
            "booked_at": str(c.Appointment.booked_at) if c.Appointment else None
        } for c in cancellations]
    finally:
        db.close()

@router.get("/analytics")
async def cancellation_analytics():
    """Get comprehensive cancellation analytics"""
    db = SessionLocal()
    try:
        # Total cancellations
        total_cancellations = db.query(func.count(database.Cancellation.id)).scalar()
        
        # Cancellations by reason
        reason_stats = db.query(
            database.Cancellation.reason,
            func.count(database.Cancellation.id).label('count')
        ).group_by(database.Cancellation.reason).all()
        
        # Cancellations by doctor
        doctor_stats = db.query(
            database.Doctor.name,
            database.Doctor.specialty,
            func.count(database.Cancellation.id).label('cancellations')
        ).join(
            database.AppointmentSlot,
            database.Doctor.id == database.AppointmentSlot.doctor_id
        ).join(
            database.Appointment,
            database.AppointmentSlot.id == database.Appointment.slot_id
        ).join(
            database.Cancellation,
            database.Appointment.id == database.Cancellation.appointment_id
        ).group_by(database.Doctor.id, database.Doctor.name, database.Doctor.specialty).all()
        
        # Cancellations by patient
        patient_stats = db.query(
            database.Patient.name,
            database.Patient.email,
            func.count(database.Cancellation.id).label('cancellations')
        ).join(
            database.Appointment,
            database.Patient.id == database.Appointment.patient_id
        ).join(
            database.Cancellation,
            database.Appointment.id == database.Cancellation.appointment_id
        ).group_by(database.Patient.id, database.Patient.name, database.Patient.email).all()
        
        # Cancellations by time period
        today = datetime.now().date()
        this_week = db.query(func.count(database.Cancellation.id)).filter(
            func.date(database.Cancellation.cancelled_at) >= func.date('now', '-7 days')
        ).scalar()
        
        this_month = db.query(func.count(database.Cancellation.id)).filter(
            func.date(database.Cancellation.cancelled_at) >= func.date('now', '-30 days')
        ).scalar()
        
        # Cancellation rate (cancellations vs total appointments)
        total_appointments = db.query(func.count(database.Appointment.id)).scalar()
        cancellation_rate = (total_cancellations / total_appointments * 100) if total_appointments > 0 else 0
        
        # Average time between booking and cancellation
        avg_time_to_cancel = db.query(
            func.avg(
                func.julianday(database.Cancellation.cancelled_at) - 
                func.julianday(database.Appointment.booked_at)
            ).label('avg_days')
        ).join(
            database.Appointment,
            database.Cancellation.appointment_id == database.Appointment.id
        ).scalar() or 0
        
        return {
            "total_cancellations": total_cancellations,
            "cancellation_rate": round(cancellation_rate, 2),
            "this_week": this_week or 0,
            "this_month": this_month or 0,
            "avg_days_to_cancel": round(avg_time_to_cancel, 1),
            "by_reason": [
                {"reason": r.reason or "No reason provided", "count": r.count}
                for r in reason_stats
            ],
            "by_doctor": [
                {
                    "doctor_name": d.name,
                    "specialty": d.specialty,
                    "cancellations": d.cancellations
                }
                for d in doctor_stats
            ],
            "by_patient": [
                {
                    "patient_name": p.name,
                    "email": p.email,
                    "cancellations": p.cancellations
                }
                for p in patient_stats
            ]
        }
    finally:
        db.close()

@router.get("/trends")
async def cancellation_trends():
    """Get cancellation trends over time"""
    db = SessionLocal()
    try:
        # Cancellations by date for the last 30 days
        trends = db.query(
            func.date(database.Cancellation.cancelled_at).label('date'),
            func.count(database.Cancellation.id).label('count')
        ).filter(
            func.date(database.Cancellation.cancelled_at) >= func.date('now', '-30 days')
        ).group_by(func.date(database.Cancellation.cancelled_at)).all()
        
        # Cancellations by day of week
        day_of_week = db.query(
            func.strftime('%w', database.Cancellation.cancelled_at).label('day'),
            func.count(database.Cancellation.id).label('count')
        ).group_by(func.strftime('%w', database.Cancellation.cancelled_at)).all()
        
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        
        return {
            "daily_trends": [
                {"date": str(t.date), "count": t.count}
                for t in trends
            ],
            "by_day_of_week": [
                {"day": day_names[int(d.day)], "count": d.count}
                for d in day_of_week
            ]
        }
    finally:
        db.close()

@router.post("/")
async def create_cancellation(
    appointment_id: int = Form(...), 
    reason: str = Form(None)
):
    """Create a cancellation and release the slot"""
    db = SessionLocal()
    try:
        # Check if appointment exists
        appointment = db.query(database.Appointment).filter(
            database.Appointment.id == appointment_id
        ).first()
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Check if already cancelled
        existing_cancellation = db.query(database.Cancellation).filter(
            database.Cancellation.appointment_id == appointment_id
        ).first()
        
        if existing_cancellation:
            raise HTTPException(status_code=400, detail="Appointment already cancelled")
        
        # Create cancellation
        cancellation = database.Cancellation(
            appointment_id=appointment_id,
            reason=reason,
            cancelled_at=datetime.now()
        )
        db.add(cancellation)
        
        # Release the slot
        slot = db.query(database.AppointmentSlot).filter(
            database.AppointmentSlot.id == appointment.slot_id
        ).first()
        
        if slot:
            slot.is_available = True
            print(f"✅ Released slot after cancellation: Slot ID={slot.id}")
        
        db.commit()
        db.refresh(cancellation)
        
        print(f"✅ Cancellation created: ID={cancellation.id}, Appointment={appointment_id}")
        
        return {
            "status": "success",
            "cancellation_id": cancellation.id,
            "message": "Appointment cancelled and slot is now available"
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating cancellation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/update")
async def update_cancellation(
    cancellation_id: int = Form(...),
    appointment_id: int = Form(...),
    reason: str = Form(None)
):
    """Update cancellation details"""
    db = SessionLocal()
    try:
        cancellation = db.query(database.Cancellation).filter(
            database.Cancellation.id == cancellation_id
        ).first()
        
        if not cancellation:
            raise HTTPException(status_code=404, detail="Cancellation not found")
        
        cancellation.appointment_id = appointment_id
        cancellation.reason = reason
        cancellation.cancelled_at = datetime.now()
        
        db.commit()
        
        print(f"✅ Cancellation updated: ID={cancellation_id}")
        
        return {"status": "success"}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating cancellation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/delete")
async def delete_cancellation(cancellation_id: int = Form(...)):
    """Delete a cancellation record"""
    db = SessionLocal()
    try:
        cancellation = db.query(database.Cancellation).filter(
            database.Cancellation.id == cancellation_id
        ).first()
        
        if not cancellation:
            raise HTTPException(status_code=404, detail="Cancellation not found")
        
        db.delete(cancellation)
        db.commit()
        
        print(f"✅ Cancellation deleted: ID={cancellation_id}")
        
        return {"status": "success"}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Error deleting cancellation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.get("/patterns")
async def cancellation_patterns():
    """Identify cancellation patterns and insights"""
    db = SessionLocal()
    try:
        # Peak cancellation times
        hour_distribution = db.query(
            func.strftime('%H', database.Cancellation.cancelled_at).label('hour'),
            func.count(database.Cancellation.id).label('count')
        ).group_by(func.strftime('%H', database.Cancellation.cancelled_at)).all()
        
        # Most common reasons
        top_reasons = db.query(
            database.Cancellation.reason,
            func.count(database.Cancellation.id).label('count')
        ).filter(
            database.Cancellation.reason.isnot(None),
            database.Cancellation.reason != ''
        ).group_by(database.Cancellation.reason).order_by(
            func.count(database.Cancellation.id).desc()
        ).limit(5).all()
        
        # Patients with multiple cancellations
        frequent_cancellers = db.query(
            database.Patient.name,
            database.Patient.email,
            func.count(database.Cancellation.id).label('cancellations')
        ).join(
            database.Appointment,
            database.Patient.id == database.Appointment.patient_id
        ).join(
            database.Cancellation,
            database.Appointment.id == database.Cancellation.appointment_id
        ).group_by(database.Patient.id).having(
            func.count(database.Cancellation.id) > 1
        ).order_by(func.count(database.Cancellation.id).desc()).all()
        
        return {
            "peak_hours": [
                {"hour": f"{int(h.hour):02d}:00", "count": h.count}
                for h in hour_distribution
            ],
            "top_reasons": [
                {"reason": r.reason, "count": r.count}
                for r in top_reasons
            ],
            "frequent_cancellers": [
                {
                    "patient_name": f.name,
                    "email": f.email,
                    "cancellations": f.cancellations
                }
                for f in frequent_cancellers
            ]
        }
    finally:
        db.close()