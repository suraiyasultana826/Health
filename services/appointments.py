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
        # Check if slot is available
        slot = db.query(database.AppointmentSlot).filter(
            database.AppointmentSlot.id == slot_id
        ).first()
        
        if not slot:
            raise HTTPException(status_code=404, detail="Slot not found")
        
        if not slot.is_available:
            raise HTTPException(status_code=400, detail="Slot is not available")
        
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
        db.add(appointment)
        
        # Mark slot as unavailable
        slot.is_available = False
        
        db.commit()
        db.refresh(appointment)
        
        print(f"✅ Appointment created: ID={appointment.id}, Patient={patient_id}, Slot={slot_id}")
        
        return {"status": "success", "appointment_id": appointment.id}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating appointment: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/update")
async def update_appointment(
    appointment_id: int = Form(...), 
    patient_id: int = Form(...), 
    slot_id: int = Form(...)
):
    db = SessionLocal()
    try:
        # Get the existing appointment
        appointment = db.query(database.Appointment).filter(
            database.Appointment.id == appointment_id
        ).first()
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Check if this appointment has been cancelled
        cancellation = db.query(database.Cancellation).filter(
            database.Cancellation.appointment_id == appointment_id
        ).first()
        
        if cancellation:
            raise HTTPException(
                status_code=400, 
                detail="Cannot update a cancelled appointment. Please restore it first or create a new appointment."
            )
        
        # Store old slot ID
        old_slot_id = appointment.slot_id
        
        # If changing to a new slot
        if old_slot_id != slot_id:
            # Check if new slot is available
            new_slot = db.query(database.AppointmentSlot).filter(
                database.AppointmentSlot.id == slot_id
            ).first()
            
            if not new_slot:
                raise HTTPException(status_code=404, detail="New slot not found")
            
            if not new_slot.is_available:
                raise HTTPException(status_code=400, detail="New slot is not available")
            
            # Release old slot
            old_slot = db.query(database.AppointmentSlot).filter(
                database.AppointmentSlot.id == old_slot_id
            ).first()
            
            if old_slot:
                old_slot.is_available = True
                print(f"✅ Released old slot: ID={old_slot_id}")
            
            # Mark new slot as unavailable
            new_slot.is_available = False
            print(f"✅ Booked new slot: ID={slot_id}")
        
        # Update appointment
        appointment.patient_id = patient_id
        appointment.slot_id = slot_id
        appointment.booked_at = datetime.now()
        
        db.commit()
        
        print(f"✅ Appointment updated: ID={appointment_id}")
        
        return {"status": "success"}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating appointment: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/delete")
async def delete_appointment(appointment_id: int = Form(...)):
    """
    Delete an appointment without creating a cancellation record.
    This is a hard delete - use with caution!
    For cancellations with tracking, use the /cancellations/cancel-and-delete endpoint instead.
    """
    db = SessionLocal()
    try:
        # Get the appointment
        appointment = db.query(database.Appointment).filter(
            database.Appointment.id == appointment_id
        ).first()
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Get the slot ID before deleting
        slot_id = appointment.slot_id
        
        # Delete the appointment
        db.delete(appointment)
        
        # Release the slot (make it available again)
        slot = db.query(database.AppointmentSlot).filter(
            database.AppointmentSlot.id == slot_id
        ).first()
        
        if slot:
            slot.is_available = True
            print(f"✅ Released slot after appointment deletion: Slot ID={slot_id}")
        
        db.commit()
        
        print(f"✅ Appointment deleted: ID={appointment_id}, Slot ID={slot_id} is now available")
        
        return {
            "status": "success",
            "message": "Appointment deleted and slot is now available"
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Error deleting appointment: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/cancel")
async def cancel_appointment(
    appointment_id: int = Form(...),
    reason: str = Form(None),
    delete_appointment: bool = Form(False)
):
    """
    Cancel an appointment with proper tracking.
    
    Args:
        appointment_id: The appointment to cancel
        reason: Reason for cancellation
        delete_appointment: If True, deletes the appointment after recording cancellation
    """
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
            raise HTTPException(
                status_code=400,
                detail="This appointment has already been cancelled"
            )
        
        # Get slot info
        slot_id = appointment.slot_id
        slot = db.query(database.AppointmentSlot).filter(
            database.AppointmentSlot.id == slot_id
        ).first()
        
        # Create cancellation record
        cancellation = database.Cancellation(
            appointment_id=appointment_id,
            reason=reason or "Appointment cancelled",
            cancelled_at=datetime.now()
        )
        db.add(cancellation)
        db.flush()
        
        # Optionally delete the appointment
        if delete_appointment:
            db.delete(appointment)
        
        # Release the slot
        if slot:
            slot.is_available = True
            print(f"✅ Slot released after cancellation: Slot ID={slot_id}")
        
        db.commit()
        db.refresh(cancellation)
        
        print(f"✅ Appointment cancelled: ID={appointment_id}, Cancellation ID={cancellation.id}")
        
        return {
            "status": "success",
            "cancellation_id": cancellation.id,
            "slot_released": True,
            "slot_id": slot_id,
            "appointment_deleted": delete_appointment,
            "message": "Appointment cancelled successfully"
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Error cancelling appointment: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.get("/check-cancellation/{appointment_id}")
async def check_cancellation(appointment_id: int):
    """Check if an appointment has been cancelled"""
    db = SessionLocal()
    try:
        cancellation = db.query(database.Cancellation).filter(
            database.Cancellation.appointment_id == appointment_id
        ).first()
        
        return {
            "is_cancelled": cancellation is not None,
            "cancellation": {
                "id": cancellation.id,
                "reason": cancellation.reason,
                "cancelled_at": str(cancellation.cancelled_at)
            } if cancellation else None
        }
    finally:
        db.close()