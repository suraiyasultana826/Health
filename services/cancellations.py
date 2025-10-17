from mysql.connector import Error

class CancellationService:
    def __init__(self, db):
        self.db = db

    def cancel_appointment(self, appointment_id: int, reason: str) -> int:
        check_query = "SELECT id FROM appointments WHERE id = %s"
        self.db.cursor.execute(check_query, (appointment_id,))
        if not self.db.cursor.fetchone():
            print(f"Error: Appointment ID {appointment_id} does not exist")
            return None

        query = """
        INSERT INTO cancellations (appointment_id, reason, cancelled_at)
        VALUES (%s, %s, NOW())
        """
        update_slot = """
        UPDATE appointment_slots s
        JOIN appointments a ON s.id = a.slot_id
        SET s.is_available = TRUE
        WHERE a.id = %s
        """
        try:
            self.db.cursor.execute(query, (appointment_id, reason))
            self.db.cursor.execute(update_slot, (appointment_id,))
            self.db.connection.commit()
            return self.db.cursor.lastrowid
        except Error as e:
            print(f"Error cancelling appointment: {e}")
            self.db.connection.rollback()
            return None

    def get_cancellation_stats(self, doctor_id: int) -> tuple:
        query = """
        SELECT d.name, COUNT(c.id) as cancellation_count
        FROM cancellations c
        JOIN appointments a ON c.appointment_id = a.id
        JOIN appointment_slots s ON a.slot_id = s.id
        JOIN doctors d ON s.doctor_id = d.id
        WHERE d.id = %s
        GROUP BY d.id, d.name
        """
        try:
            self.db.cursor.execute(query, (doctor_id,))
            return self.db.cursor.fetchone()
        except Error as e:
            print(f"Error fetching cancellation stats: {e}")
            return None