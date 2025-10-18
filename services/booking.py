from fastapi import APIRouter, HTTPException, Form
from sqlalchemy import func, and_, or_, case
from db.database import SessionLocal
from db import database
from datetime import datetime, date, time, timedelta

router = APIRouter()

@router.get("/search-availability")
async def search_availability(
    specialty: str = None,
    doctor_name: str = None,
    start_date: str = None,
    end_date: str = None
):
    """
    Complex query to search for doctor availability with multiple filters
    Returns doctors with their available slots count and details
    """
    db = SessionLocal()
    try:
        # Build complex query with joins and aggregations
        query = db.query(
            database.Doctor.id.label('doctor_id'),
            database.Doctor.name.label('doctor_name'),
            database.Doctor.specialty.label('specialty'),
            func.count(database.AppointmentSlot.id).label('total_slots'),
            func.sum(
                case(
                    (database.AppointmentSlot.is_available == True, 1),
                    else_=0
                )
            ).label('available_slots'),
            func.min(database.AppointmentSlot.date).label('earliest_date'),
            func.max(database.AppointmentSlot.date).label('latest_date')
        ).outerjoin(
            database.AppointmentSlot,
            database.Doctor.id == database.AppointmentSlot.doctor_id
        ).group_by(
            database.Doctor.id,
            database.Doctor.name,
            database.Doctor.specialty
        )
        
        # Apply filters
        if specialty:
            query = query.filter(database.Doctor.specialty.ilike(f'%{specialty}%'))
        
        if doctor_name:
            query = query.filter(database.Doctor.name.ilike(f'%{doctor_name}%'))
        
        if start_date:
            query = query.filter(
                or_(
                    database.AppointmentSlot.date >= start_date,
                    database.AppointmentSlot.date.is_(None)
                )
            )
        
        if end_date:
            query = query.filter(
                or_(
                    database.AppointmentSlot.date <= end_date,
                    database.AppointmentSlot.date.is_(None)
                )
            )
        
        results = query.all()
        
        return [
            {
                "doctor_id": r.doctor_id,
                "doctor_name": r.doctor_name,
                "specialty": r.specialty,
                "total_slots": r.total_slots or 0,
                "available_slots": r.available_slots or 0,
                "earliest_date": str(r.earliest_date) if r.earliest_date else None,
                "latest_date": str(r.latest_date) if r.latest_date else None
            }
            for r in results
        ]
    finally:
        db.close()

@router.get("/doctor-slots/{doctor_id}")
async def get_doctor_slots(
    doctor_id: int,
    start_date: str = None,
    end_date: str = None,
    available_only: bool = True
):
    """
    Get detailed slots for a specific doctor with filtering
    """
    db = SessionLocal()
    try:
        query = db.query(
            database.AppointmentSlot.id,
            database.AppointmentSlot.date,
            database.AppointmentSlot.start_time,
            database.AppointmentSlot.end_time,
            database.AppointmentSlot.is_available,
            database.Doctor.name.label('doctor_name'),
            database.Doctor.specialty
        ).join(
            database.Doctor,
            database.AppointmentSlot.doctor_id == database.Doctor.id
        ).filter(
            database.AppointmentSlot.doctor_id == doctor_id
        )
        
        if available_only:
            query = query.filter(database.AppointmentSlot.is_available == True)
        
        if start_date:
            query = query.filter(database.AppointmentSlot.date >= start_date)
        
        if end_date:
            query = query.filter(database.AppointmentSlot.date <= end_date)
        
        query = query.order_by(
            database.AppointmentSlot.date,
            database.AppointmentSlot.start_time
        )
        
        results = query.all()
        
        return [
            {
                "slot_id": r.id,
                "date": str(r.date),
                "start_time": str(r.start_time),
                "end_time": str(r.end_time),
                "is_available": r.is_available,
                "doctor_name": r.doctor_name,
                "specialty": r.specialty
            }
            for r in results
        ]
    finally:
        db.close()

@router.get("/capacity-analysis")
async def capacity_analysis(start_date: str = None, end_date: str = None):
    """
    Complex analytical query showing doctor capacity utilization
    """
    db = SessionLocal()
    try:
        # Complex query with subqueries and calculations
        query = db.query(
            database.Doctor.id,
            database.Doctor.name,
            database.Doctor.specialty,
            func.count(database.AppointmentSlot.id).label('total_slots'),
            func.sum(
                case(
                    (database.AppointmentSlot.is_available == True, 1),
                    else_=0
                )
            ).label('available_slots'),
            func.sum(
                case(
                    (database.AppointmentSlot.is_available == False, 1),
                    else_=0
                )
            ).label('booked_slots'),
            func.count(database.Appointment.id).label('confirmed_appointments')
        ).outerjoin(
            database.AppointmentSlot,
            database.Doctor.id == database.AppointmentSlot.doctor_id
        ).outerjoin(
            database.Appointment,
            database.AppointmentSlot.id == database.Appointment.slot_id
        )
        
        if start_date:
            query = query.filter(
                or_(
                    database.AppointmentSlot.date >= start_date,
                    database.AppointmentSlot.date.is_(None)
                )
            )
        
        if end_date:
            query = query.filter(
                or_(
                    database.AppointmentSlot.date <= end_date,
                    database.AppointmentSlot.date.is_(None)
                )
            )
        
        query = query.group_by(
            database.Doctor.id,
            database.Doctor.name,
            database.Doctor.specialty
        )
        
        results = query.all()
        
        return [
            {
                "doctor_id": r.id,
                "doctor_name": r.name,
                "specialty": r.specialty,
                "total_slots": r.total_slots or 0,
                "available_slots": r.available_slots or 0,
                "booked_slots": r.booked_slots or 0,
                "confirmed_appointments": r.confirmed_appointments or 0,
                "utilization_rate": round(
                    (r.booked_slots / r.total_slots * 100) if r.total_slots else 0,
                    2
                )
            }
            for r in results
        ]
    finally:
        db.close()

@router.post("/book-appointment")
async def book_appointment(
    patient_id: int = Form(...),
    slot_id: int = Form(...)
):
    """
    Book appointment with transaction safety and slot availability check
    """
    db = SessionLocal()
    try:
        # Check if slot exists and is available
        slot = db.query(database.AppointmentSlot).filter(
            database.AppointmentSlot.id == slot_id,
            database.AppointmentSlot.is_available == True
        ).first()
        
        if not slot:
            raise HTTPException(status_code=400, detail="Slot not available")
        
        # Check if patient exists
        patient = db.query(database.Patient).filter(
            database.Patient.id == patient_id
        ).first()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Create appointment
        appointment = database.Appointment(
            patient_id=patient_id,
            slot_id=slot_id,
            booked_at=datetime.now()
        )
        
        # Mark slot as unavailable
        slot.is_available = False
        
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        
        return {
            "status": "success",
            "appointment_id": appointment.id,
            "message": "Appointment booked successfully"
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()