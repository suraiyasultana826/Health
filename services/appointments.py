from mysql.connector import Error

class AppointmentService:
    def __init__(self, db):
        self.db = db

    def book_appointment(self, patient_id: int, slot_id: int) -> int:
        check_slot = "SELECT id FROM appointment_slots WHERE id = %s AND is_available = TRUE"
        check_patient = "SELECT id FROM patients WHERE id = %s"
        try:
            self.db.cursor.execute(check_slot, (slot_id,))
            if not self.db.cursor.fetchone():
                print(f"Error: Slot ID {slot_id} is invalid or unavailable")
                return None
            self.db.cursor.execute(check_patient, (patient_id,))
            if not self.db.cursor.fetchone():
                print(f"Error: Patient ID {patient_id} is invalid")
                return None
            query = """
            INSERT INTO appointments (patient_id, slot_id, booked_at)
            VALUES (%s, %s, NOW())
            """
            update_slot = "UPDATE appointment_slots SET is_available = FALSE WHERE id = %s"
            self.db.cursor.execute(query, (patient_id, slot_id))
            self.db.cursor.execute(update_slot, (slot_id,))
            self.db.connection.commit()
            return self.db.cursor.lastrowid
        except Error as e:
            print(f"Error booking appointment: {e}")
            self.db.connection.rollback()
            return None