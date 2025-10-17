from db.database import Database
from services.doctors import DoctorService
from services.patients import PatientService
from services.slots import SlotService
from services.appointments import AppointmentService
from services.cancellations import CancellationService

def main():
    # Initialize database
    db = Database()
    db.create_schema()

    # Initialize services
    doctor_service = DoctorService(db)
    patient_service = PatientService(db)
    slot_service = SlotService(db)
    appointment_service = AppointmentService(db)
    cancellation_service = CancellationService(db)

    # Example usage
    doctor_id = doctor_service.add_doctor("Dr. Smith", "Cardiology")
    patient_id = patient_service.add_patient("John Doe", "john@example.com")
    slot_id = slot_service.add_slot(doctor_id, "2025-10-20", "10:00:00", "10:30:00")
    slot_id = slot_service.add_slot(doctor_id, "2025-10-20", "10:30:00", "11:30:00")
    appointment_id = appointment_service.book_appointment(patient_id, slot_id)
    cancellation_service.cancel_appointment(appointment_id, "Patient unavailable")

    # Fetch data
    print(doctor_service.get_doctor_availability(doctor_id, "2025-10-20"))
    print(patient_service.get_patient_appointments(patient_id))
    print(cancellation_service.get_cancellation_stats(doctor_id))

    db.close()

if __name__ == "__main__":
    main()