from mysql.connector import Error

class SlotService:
    def __init__(self, db):
        self.db = db

    def add_slot(self, doctor_id: int, date: str, start_time: str, end_time: str) -> int:
        query = """
        INSERT INTO appointment_slots (doctor_id, date, start_time, end_time)
        VALUES (%s, %s, %s, %s)
        """
        try:
            self.db.cursor.execute(query, (doctor_id, date, start_time, end_time))
            self.db.connection.commit()
            return self.db.cursor.lastrowid
        except Error as e:
            print(f"Error adding slot: {e}")
            return None

    def get_slot(self, slot_id: int) -> tuple:
        query = """
        SELECT id, doctor_id, date, start_time, end_time, is_available
        FROM appointment_slots WHERE id = %s
        """
        try:
            self.db.cursor.execute(query, (slot_id,))
            return self.db.cursor.fetchone()
        except Error as e:
            print(f"Error fetching slot: {e}")
            return None

    def get_all_slots(self) -> list:
        query = """
        SELECT s.id, d.name, s.date, s.start_time, s.end_time, s.is_available
        FROM appointment_slots s
        JOIN doctors d ON s.doctor_id = d.id
        """
        try:
            self.db.cursor.execute(query)
            return self.db.cursor.fetchall()
        except Error as e:
            print(f"Error fetching slots: {e}")
            return []

    def update_slot(self, slot_id: int, date: str, start_time: str, end_time: str) -> bool:
        query = """
        UPDATE appointment_slots
        SET date = %s, start_time = %s, end_time = %s
        WHERE id = %s AND is_available = TRUE
        """
        try:
            self.db.cursor.execute(query, (date, start_time, end_time, slot_id))
            self.db.connection.commit()
            return self.db.cursor.rowcount > 0
        except Error as e:
            print(f"Error updating slot: {e}")
            self.db.connection.rollback()
            return False

    def delete_slot(self, slot_id: int) -> bool:
        check_query = "SELECT COUNT(*) FROM appointments WHERE slot_id = %s"
        try:
            self.db.cursor.execute(check_query, (slot_id,))
            appt_count = self.db.cursor.fetchone()[0]
            if appt_count > 0:
                print(f"Error: Slot ID {slot_id} has {appt_count} associated appointments")
                return False
            delete_query = "DELETE FROM appointment_slots WHERE id = %s"
            self.db.cursor.execute(delete_query, (slot_id,))
            self.db.connection.commit()
            return self.db.cursor.rowcount > 0
        except Error as e:
            print(f"Error deleting slot: {e}")
            self.db.connection.rollback()
            return False