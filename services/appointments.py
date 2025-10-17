from mysql.connector import Error

class AppointmentService:
    def __init__(self, db):
        self.db = db

    def book_appointment(self, patient_id, slot_id):
        query = """
        INSERT INTO appointments (patient_id, slot_id, booked_at)
        VALUES (%s, %s, NOW())
        """
        update_slot = "UPDATE appointment_slots SET is_available = FALSE WHERE id = %s"
        try:
            self.db.cursor.execute(query, (patient_id, slot_id))
            self.db.cursor.execute(update_slot, (slot_id,))
            self.db.connection.commit()
            return self.db.cursor.lastrowid
        except Error as e:
            print(f"Error booking appointment: {e}")
            self.db.connection.rollback()
            return None