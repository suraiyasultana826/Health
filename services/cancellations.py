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

    def get_cancellation(self, cancellation_id: int) -> tuple:
        query = """
        SELECT c.id, d.name, p.name, s.date, s.start_time, s.end_time, c.reason, c.cancelled_at
        FROM cancellations c
        JOIN appointments a ON c.appointment_id = a.id
        JOIN appointment_slots s ON a.slot_id = s.id
        JOIN doctors d ON s.doctor_id = d.id
        JOIN patients p ON a.patient_id = p.id
        WHERE c.id = %s
        """
        try:
            self.db.cursor.execute(query, (cancellation_id,))
            return self.db.cursor.fetchone()
        except Error as e:
            print(f"Error fetching cancellation: {e}")
            return None

    def get_all_cancellations(self, doctor_id: int = None, start_date: str = None, end_date: str = None, reason: str = None) -> list:
        query = """
        SELECT c.id, d.name, p.name, s.date, s.start_time, s.end_time, c.reason, c.cancelled_at
        FROM cancellations c
        JOIN appointments a ON c.appointment_id = a.id
        JOIN appointment_slots s ON a.slot_id = s.id
        JOIN doctors d ON s.doctor_id = d.id
        JOIN patients p ON a.patient_id = p.id
        WHERE 1=1
        """
        params = []
        if doctor_id:
            query += " AND d.id = %s"
            params.append(doctor_id)
        if start_date:
            query += " AND s.date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND s.date <= %s"
            params.append(end_date)
        if reason:
            query += " AND c.reason LIKE %s"
            params.append(f"%{reason}%")

        try:
            self.db.cursor.execute(query, params)
            return self.db.cursor.fetchall()
        except Error as e:
            print(f"Error fetching cancellations: {e}")
            return []

    def update_cancellation(self, cancellation_id: int, reason: str) -> bool:
        query = "UPDATE cancellations SET reason = %s WHERE id = %s"
        try:
            self.db.cursor.execute(query, (reason, cancellation_id))
            self.db.connection.commit()
            return self.db.cursor.rowcount > 0
        except Error as e:
            print(f"Error updating cancellation: {e}")
            self.db.connection.rollback()
            return False

    def delete_cancellation(self, cancellation_id: int) -> bool:
        query = "DELETE FROM cancellations WHERE id = %s"
        try:
            self.db.cursor.execute(query, (cancellation_id,))
            self.db.connection.commit()
            return self.db.cursor.rowcount > 0
        except Error as e:
            print(f"Error deleting cancellation: {e}")
            self.db.connection.rollback()
            return False